import os
import shutil
import re
from pathlib import Path
from collections import defaultdict

def organize_dataset(source_dir, target_dir):
    """
    整理数据集文件到对应的task文件夹中，区分human和非human文件
    
    Args:
        source_dir: 源文件夹路径
        target_dir: 目标文件夹路径
    """
    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)
    
    # 用于存储每个task的文件列表，区分human和非human
    task_files = defaultdict(lambda: {'normal': [], 'human': []})
    
    # 遍历源目录中的所有文件和文件夹
    for root, dirs, files in os.walk(source_dir):
        for dir_name in dirs:
            # 提取task编号
            match = re.match(r'task_(\d+)_', dir_name)
            if match:
                task_num = match.group(1)
                full_path = os.path.join(root, dir_name)
                
                # 检查是否包含human后缀
                if 'human' in dir_name.lower():
                    task_files[task_num]['human'].append(full_path)
                else:
                    task_files[task_num]['normal'].append(full_path)
    
    # 处理每个task组
    for task_num, file_groups in task_files.items():
        # 处理普通文件（无human后缀）
        if file_groups['normal']:
            task_folder = os.path.join(target_dir, f'task_{task_num}')
            os.makedirs(task_folder, exist_ok=True)
            
            # 对文件路径进行排序
            file_groups['normal'].sort()
            
            # 移动并重命名文件
            for idx, old_path in enumerate(file_groups['normal'], 1):
                new_folder_name = create_new_folder_name(old_path, idx)
                new_path = os.path.join(task_folder, new_folder_name)
                
                try:
                    shutil.move(old_path, new_path)
                    print(f'已移动: {old_path} -> {new_path}')
                    # 处理内部的cam文件夹
                    rename_cam_folders_with_filter(new_path)
                except Exception as e:
                    print(f'移动失败: {old_path} -> {new_path}, 错误: {e}')
        
        # 处理human文件
        if file_groups['human']:
            task_human_folder = os.path.join(target_dir, f'task_{task_num}_human')
            os.makedirs(task_human_folder, exist_ok=True)
            
            # 对文件路径进行排序
            file_groups['human'].sort()
            
            # 移动并重命名文件
            for idx, old_path in enumerate(file_groups['human'], 1):
                new_folder_name = create_new_folder_name(old_path, idx)
                new_path = os.path.join(task_human_folder, new_folder_name)
                
                try:
                    shutil.move(old_path, new_path)
                    print(f'已移动: {old_path} -> {new_path}')
                    # 处理内部的cam文件夹
                    rename_cam_folders_with_filter(new_path)
                except Exception as e:
                    print(f'移动失败: {old_path} -> {new_path}, 错误: {e}')

def organize_dataset_copy(source_dir, target_dir):
    """
    整理数据集文件到对应的task文件夹中（复制而非移动），区分human和非human文件
    
    Args:
        source_dir: 源文件夹路径
        target_dir: 目标文件夹路径
    """
    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)
    
    # 用于存储每个task的文件列表，区分human和非human
    task_files = defaultdict(lambda: {'normal': [], 'human': []})
    
    # 遍历源目录中的所有文件和文件夹
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            # 提取task编号
            match = re.match(r'task_(\d+)_', item)
            if match:
                task_num = match.group(1)
                
                # 检查是否包含human后缀
                if 'human' in item.lower():
                    task_files[task_num]['human'].append(item_path)
                else:
                    task_files[task_num]['normal'].append(item_path)
    
    # 处理每个task组
    for task_num, file_groups in task_files.items():
        # 处理普通文件（无human后缀）
        if file_groups['normal']:
            task_folder = os.path.join(target_dir, f'task_{task_num}')
            os.makedirs(task_folder, exist_ok=True)
            
            # 对文件路径进行排序
            file_groups['normal'].sort()
            
            # 复制并重命名文件
            for idx, old_path in enumerate(file_groups['normal'], 1):
                new_folder_name = create_new_folder_name(old_path, idx)
                new_path = os.path.join(task_folder, new_folder_name)
                
                try:
                    shutil.copytree(old_path, new_path)
                    print(f'已复制: {old_path} -> {new_path}')
                    # 处理内部的cam文件夹
                    rename_cam_folders_with_filter(new_path)
                except Exception as e:
                    print(f'复制失败: {old_path} -> {new_path}, 错误: {e}')
        
        # 处理human文件
        if file_groups['human']:
            task_human_folder = os.path.join(target_dir, f'task_{task_num}_human')
            os.makedirs(task_human_folder, exist_ok=True)
            
            # 对文件路径进行排序
            file_groups['human'].sort()
            
            # 复制并重命名文件
            for idx, old_path in enumerate(file_groups['human'], 1):
                new_folder_name = create_new_folder_name(old_path, idx)
                new_path = os.path.join(task_human_folder, new_folder_name)
                
                try:
                    shutil.copytree(old_path, new_path)
                    print(f'已复制: {old_path} -> {new_path}')
                    # 处理内部的cam文件夹
                    rename_cam_folders_with_filter(new_path)
                except Exception as e:
                    print(f'复制失败: {old_path} -> {new_path}, 错误: {e}')

def rename_cam_folders(parent_path):
    """
    重命名指定路径下的cam_开头的文件夹为数字编号
    
    Args:
        parent_path: 父文件夹路径
    """
    # 获取所有cam开头的文件夹
    cam_folders = []
    for item in os.listdir(parent_path):
        item_path = os.path.join(parent_path, item)
        if os.path.isdir(item_path) and item.startswith('cam_'):
            cam_folders.append(item)
    
    # 按名称排序以保证顺序一致
    cam_folders.sort()
    
    # 重命名
    for idx, old_name in enumerate(cam_folders):
        old_path = os.path.join(parent_path, old_name)
        new_name = str(idx)
        new_path = os.path.join(parent_path, new_name)
        
        try:
            os.rename(old_path, new_path)
            print(f'  已重命名cam文件夹: {old_name} -> {new_name}')
        except Exception as e:
            print(f'  重命名cam文件夹失败: {old_name} -> {new_name}, 错误: {e}')

def clean_folders_keep_color_mp4(parent_path):
    """
    清理文件夹，只保留包含color.mp4的文件夹，并删除同目录下的其他文件
    
    Args:
        parent_path: 父文件夹路径
    """
    folders_to_remove = []
    
    # 遍历所有子文件夹
    for item in os.listdir(parent_path):
        item_path = os.path.join(parent_path, item)
        if os.path.isdir(item_path):
            # 检查文件夹是否包含color.mp4
            color_mp4_path = os.path.join(item_path, 'color.mp4')
            if os.path.exists(color_mp4_path):
                # 保留这个文件夹，但删除除color.mp4外的其他文件
                for file in os.listdir(item_path):
                    file_path = os.path.join(item_path, file)
                    if os.path.isfile(file_path) and file != 'color.mp4':
                        try:
                            os.remove(file_path)
                            print(f'    已删除文件: {file_path}')
                        except Exception as e:
                            print(f'    删除文件失败: {file_path}, 错误: {e}')
            else:
                # 标记不包含color.mp4的文件夹，稍后删除
                folders_to_remove.append(item_path)
    
    # 删除不包含color.mp4的文件夹
    for folder_path in folders_to_remove:
        try:
            shutil.rmtree(folder_path)
            print(f'  已删除文件夹: {folder_path}')
        except Exception as e:
            print(f'  删除文件夹失败: {folder_path}, 错误: {e}')

def keep_only_first_three_folders(parent_path):
    """
    只保留前三个包含color.mp4的文件夹（0, 1, 2），删除其余文件夹
    
    Args:
        parent_path: 父文件夹路径
    """
    # 获取所有数字命名的文件夹
    folders = []
    for item in os.listdir(parent_path):
        item_path = os.path.join(parent_path, item)
        if os.path.isdir(item_path) and item.isdigit():
            folders.append((int(item), item_path))
    
    # 按数字排序
    folders.sort(key=lambda x: x[0])
    
    # 删除索引大于2的文件夹
    deleted_count = 0
    for idx, folder_path in folders:
        if idx > 2:
            try:
                shutil.rmtree(folder_path)
                print(f'  已删除文件夹: {folder_path}')
                deleted_count += 1
            except Exception as e:
                print(f'  删除文件夹失败: {folder_path}, 错误: {e}')
    
    if deleted_count > 0:
        print(f'  共删除了 {deleted_count} 个文件夹')

def rename_cam_folders_with_filter(parent_path):
    """
    重命名指定路径下的cam_开头的文件夹为数字编号，并只保留包含color.mp4的文件夹
    
    Args:
        parent_path: 父文件夹路径
    """
    # 先清理文件夹
    clean_folders_keep_color_mp4(parent_path)
    
    # 获取剩余的cam开头的文件夹
    cam_folders = []
    for item in os.listdir(parent_path):
        item_path = os.path.join(parent_path, item)
        if os.path.isdir(item_path) and item.startswith('cam_'):
            cam_folders.append(item)
    
    # 按名称排序以保证顺序一致
    cam_folders.sort()
    
    # 重命名
    for idx, old_name in enumerate(cam_folders):
        old_path = os.path.join(parent_path, old_name)
        new_name = str(idx)
        new_path = os.path.join(parent_path, new_name)
        
        try:
            os.rename(old_path, new_path)
            print(f'  已重命名cam文件夹: {old_name} -> {new_name}')
        except Exception as e:
            print(f'  重命名cam文件夹失败: {old_name} -> {new_name}, 错误: {e}')
    
    # 只保留前三个文件夹
    keep_only_first_three_folders(parent_path)

def create_new_folder_name(old_path, idx):
    """
    创建新的文件夹名称
    
    Args:
        old_path: 原始文件夹路径
        idx: 序号
        
    Returns:
        新的文件夹名称
    """
    # 直接返回从0开始的数字编号
    return str(idx - 1)

def delete_meta_json_files(directory):
    """
    递归删除指定目录下所有的meta.json和metadata.json文件
    
    Args:
        directory: 要处理的目录路径
    """
    deleted_count = 0
    
    # 递归遍历目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file in ['meta.json', 'metadata.json']:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f'已删除: {file_path}')
                    deleted_count += 1
                except Exception as e:
                    print(f'删除失败: {file_path}, 错误: {e}')
    
    print(f'\n总共删除了 {deleted_count} 个meta.json/metadata.json文件')

def create_videos_folder_structure(task_folder):
    """
    在task文件夹中创建videos子文件夹，并将所有内容移动到videos中
    
    Args:
        task_folder: task文件夹路径
    """
    videos_folder = os.path.join(task_folder, 'videos')
    os.makedirs(videos_folder, exist_ok=True)
    
    # 获取task文件夹中的所有项目（除了videos文件夹本身）
    items_to_move = []
    for item in os.listdir(task_folder):
        item_path = os.path.join(task_folder, item)
        if item != 'videos' and os.path.isdir(item_path):
            items_to_move.append(item)
    
    # 移动所有项目到videos文件夹
    for item in items_to_move:
        old_path = os.path.join(task_folder, item)
        new_path = os.path.join(videos_folder, item)
        try:
            shutil.move(old_path, new_path)
            print(f'  已移动到videos文件夹: {item}')
        except Exception as e:
            print(f'  移动失败: {item}, 错误: {e}')

def remove_tasks_without_human(target_dir):
    """
    删除没有对应human版本的task文件夹
    
    Args:
        target_dir: 目标目录路径
    """
    # 获取所有的task编号
    task_numbers = set()
    human_task_numbers = set()
    
    for folder in os.listdir(target_dir):
        if folder.startswith('task_'):
            match = re.match(r'task_(\d+)(?:_human)?$', folder)
            if match:
                task_num = match.group(1)
                if folder.endswith('_human'):
                    human_task_numbers.add(task_num)
                else:
                    task_numbers.add(task_num)
    
    # 找出没有human版本的task
    tasks_without_human = task_numbers - human_task_numbers
    
    # 删除这些task文件夹
    deleted_count = 0
    for task_num in tasks_without_human:
        folder_name = f'task_{task_num}'
        folder_path = os.path.join(target_dir, folder_name)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f'已删除没有human版本的task文件夹: {folder_name}')
                deleted_count += 1
            except Exception as e:
                print(f'删除文件夹失败: {folder_name}, 错误: {e}')
    
    if deleted_count > 0:
        print(f'\n总共删除了 {deleted_count} 个没有human版本的task文件夹')
    else:
        print('\n所有task都有对应的human版本，无需删除')

def main():
    # 设置源目录和目标目录
    source_directory = '/home/alien/Dataset/RH20T_cfg3_restored/'  # 修改为您的源文件夹路径
    target_directory = '/home/alien/Research/xskill/datasets/rh20T_test'  # 修改为您的目标文件夹路径
    
    print("开始整理数据集...")
    print(f"源目录: {source_directory}")
    print(f"目标目录: {target_directory}")
    
    # 选择使用移动还是复制
    use_copy = True  # 设置为False则使用移动操作
    
    if use_copy:
        print("使用复制模式...")
        organize_dataset_copy(source_directory, target_directory)
    else:
        print("使用移动模式...")
        organize_dataset(source_directory, target_directory)
    
    print("整理完成！")
    
    # 删除没有human版本的task文件夹
    print("\n检查并删除没有human版本的task文件夹...")
    remove_tasks_without_human(target_directory)
    
    # 在每个task文件夹中创建videos文件夹结构
    print("\n创建videos文件夹结构...")
    if os.path.exists(target_directory):
        for folder in os.listdir(target_directory):
            folder_path = os.path.join(target_directory, folder)
            if os.path.isdir(folder_path) and (folder.startswith('task_')):
                print(f'\n处理文件夹: {folder}')
                create_videos_folder_structure(folder_path)
    
    # 删除所有meta.json和metadata.json文件
    print("\n开始删除meta.json和metadata.json文件...")
    delete_meta_json_files(target_directory)
    
    # 打印整理结果统计
    if os.path.exists(target_directory):
        all_folders = [f for f in os.listdir(target_directory) if os.path.isdir(os.path.join(target_directory, f))]
        task_folders = [f for f in all_folders if re.match(r'task_\d+$', f)]
        human_folders = [f for f in all_folders if re.match(r'task_\d+_human$', f)]
        
        print(f"\n整理统计:")
        print(f"创建了 {len(task_folders)} 个普通task文件夹")
        print(f"创建了 {len(human_folders)} 个human task文件夹")
        print(f"总计: {len(all_folders)} 个文件夹\n")
        
        # 显示详细统计
        print("详细统计:")
        for folder in sorted(all_folders):
            folder_path = os.path.join(target_directory, folder)
            num_items = len(os.listdir(folder_path))
            folder_type = "human" if folder.endswith('_human') else "normal"
            print(f"  {folder} ({folder_type}): {num_items} 个项目")

if __name__ == "__main__":
    main()
    # Run
    # create_replay_buffer.py datasets/rh20T_test/task_0001
    # Run for all tasks
    # for task in task_0003 task_0004 task_0005 task_0006 task_0007 task_0008 task_0001_human task_0003_human task_0004_human task_0005_human task_0006_human task_0007_human task_0008_human; do echo "重新创建 $task..."; rm -rf datasets/rh20T_test/$task/replay_buffer.zarr; /home/alien/anaconda3/envs/xskill/bin/python utils/create_replay_buffer.py datasets/rh20T_test/$task > /dev/null 2>&1; done