#!/usr/bin/env python3
"""
为配置文件生成所有task目录的路径列表

这个脚本会扫描指定目录中所有的task文件夹，并生成适用于配置文件的路径列表。
"""

import os
from pathlib import Path
import yaml


def get_all_task_paths(base_path, robot_only=False, human_only=False):
    """获取所有task目录的路径"""
    base_path = Path(base_path)
    if not base_path.exists():
        raise ValueError(f"基础路径不存在: {base_path}")
    
    # 获取所有task目录
    task_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith('task_')]
    task_dirs.sort()
    
    robot_paths = []
    human_paths = []
    
    for task_dir in task_dirs:
        if task_dir.name.endswith('_human'):
            if not robot_only:
                human_paths.append(str(task_dir))
        else:
            if not human_only:
                robot_paths.append(str(task_dir))
    
    return robot_paths, human_paths


def generate_yaml_paths(base_dev_dir, dataset_subpath):
    """生成YAML格式的路径列表"""
    full_path = Path(base_dev_dir) / "xskill" / dataset_subpath
    robot_paths, human_paths = get_all_task_paths(full_path)
    
    # 转换为相对于base_dev_dir的路径
    robot_yaml_paths = []
    human_yaml_paths = []
    
    for path in robot_paths:
        rel_path = Path(path).relative_to(base_dev_dir)
        yaml_path = f"'${{base_dev_dir}}/{rel_path}'"
        robot_yaml_paths.append(yaml_path)
    
    for path in human_paths:
        rel_path = Path(path).relative_to(base_dev_dir)
        yaml_path = f"'${{base_dev_dir}}/{rel_path}'"
        human_yaml_paths.append(yaml_path)
    
    return robot_yaml_paths, human_yaml_paths


def update_config_file(config_file, base_dev_dir, dataset_subpath):
    """更新配置文件中的路径"""
    robot_paths, human_paths = generate_yaml_paths(base_dev_dir, dataset_subpath)
    
    print(f"找到 {len(robot_paths)} 个机器人task目录")
    print(f"找到 {len(human_paths)} 个人类task目录")
    
    # 读取配置文件
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成新的robot_dataset部分
    robot_section = "  _allowed_dirs: [\n"
    for path in robot_paths:
        robot_section += f"    {path},\n"
    robot_section += "  ]"
    
    # 生成新的human_dataset部分
    human_section = "  _allowed_dirs: [\n"
    for path in human_paths:
        human_section += f"    {path},\n"
    if human_paths:  # 如果有human路径，添加最后的空行
        human_section += "\n"
    human_section += "  ]"
    
    return robot_section, human_section, content


def main():
    # 配置参数
    base_dev_dir = '/home/alien/Research/'
    dataset_subpath = 'datasets/rh20T_test'
    config_file = 'config/realworld/skill_discovery.yaml'
    
    print(f"正在处理配置文件: {config_file}")
    print(f"数据集路径: {base_dev_dir}/{dataset_subpath}")
    
    try:
        robot_section, human_section, original_content = update_config_file(
            config_file, base_dev_dir, dataset_subpath
        )
        
        print("\n机器人数据集路径:")
        print(robot_section)
        
        print("\n人类数据集路径:")
        print(human_section)
        
        print(f"\n可以手动更新配置文件，或者使用程序自动替换。")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
