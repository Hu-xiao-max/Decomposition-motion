#!/usr/bin/env python3
"""
为视频数据创建最小的 replay_buffer.zarr 文件

这个脚本会分析视频目录结构，并创建包含基本元数据的 replay_buffer.zarr 文件，
使其能够与 RealWorldEpisodeTrajDataset 兼容。
"""

import os
import zarr
import numpy as np
import av
from pathlib import Path
from tqdm import tqdm
import argparse
from xskill.common.replay_buffer import ReplayBuffer


def get_video_frame_count(video_path):
    """获取视频的帧数"""
    try:
        with av.open(str(video_path)) as container:
            video_stream = container.streams.video[0]
            return video_stream.frames
    except:
        # 如果无法获取精确帧数，尝试通过解码来计算
        try:
            with av.open(str(video_path)) as container:
                count = 0
                for frame in container.decode(video=0):
                    count += 1
                return count
        except:
            print(f"警告: 无法获取视频 {video_path} 的帧数，使用默认值 100")
            return 100


def analyze_video_structure(dataset_path):
    """分析视频目录结构，获取episode信息"""
    videos_dir = Path(dataset_path) / 'videos'
    if not videos_dir.exists():
        raise ValueError(f"视频目录不存在: {videos_dir}")
    
    episodes = []
    episode_dirs = sorted([d for d in videos_dir.iterdir() if d.is_dir()], 
                         key=lambda x: int(x.name))
    
    print(f"发现 {len(episode_dirs)} 个episode目录")
    
    for episode_dir in tqdm(episode_dirs, desc="分析episode"):
        episode_idx = int(episode_dir.name)
        
        # 获取相机目录
        camera_dirs = sorted([d for d in episode_dir.iterdir() if d.is_dir()], 
                           key=lambda x: int(x.name))
        
        if not camera_dirs:
            print(f"警告: Episode {episode_idx} 没有相机目录")
            continue
        
        # 使用第一个相机来获取episode长度
        first_camera_dir = camera_dirs[0]
        video_path = first_camera_dir / 'color.mp4'
        
        if not video_path.exists():
            print(f"警告: Episode {episode_idx}, Camera {first_camera_dir.name} 没有 color.mp4 文件")
            frame_count = 100  # 默认值
        else:
            frame_count = get_video_frame_count(video_path)
        
        episodes.append({
            'episode_idx': episode_idx,
            'frame_count': frame_count,
            'cameras': [int(d.name) for d in camera_dirs]
        })
        
        print(f"Episode {episode_idx}: {frame_count} 帧, 相机: {[int(d.name) for d in camera_dirs]}")
    
    return episodes


def create_minimal_replay_buffer(dataset_path, episodes):
    """创建最小的replay_buffer.zarr文件"""
    zarr_path = Path(dataset_path) / 'replay_buffer.zarr'
    
    if zarr_path.exists():
        print(f"警告: {zarr_path} 已存在，将被覆盖")
        import shutil
        shutil.rmtree(zarr_path)
    
    # 创建zarr存储
    store = zarr.DirectoryStore(str(zarr_path))
    replay_buffer = ReplayBuffer.create_empty_zarr(storage=store)
    
    # 计算episode_ends
    episode_ends = []
    total_frames = 0
    for episode in episodes:
        total_frames += episode['frame_count']
        episode_ends.append(total_frames)
    
    # 创建episode_ends数组
    episode_ends_arr = np.array(episode_ends, dtype=np.int64)
    del replay_buffer.root['meta']['episode_ends']  # 删除现有的空数组
    replay_buffer.root['meta']['episode_ends'] = episode_ends_arr
    
    # 创建虚拟的timestamp数据（假设30fps）
    dt = 1.0 / 30.0  # 30fps
    timestamps = np.arange(total_frames, dtype=np.float64) * dt
    
    replay_buffer.root['data']['timestamp'] = timestamps
    
    # 创建虚拟的action数据（如果需要的话）
    # 这里创建7维的零动作（通常机器人有7个自由度）
    actions = np.zeros((total_frames, 7), dtype=np.float32)
    replay_buffer.root['data']['action'] = actions
    
    # 创建虚拟的状态数据（假设30维状态）
    states = np.zeros((total_frames, 30), dtype=np.float32)
    replay_buffer.root['data']['obs'] = states
    
    print(f"创建了 replay_buffer.zarr:")
    print(f"  总帧数: {total_frames}")
    print(f"  Episode数: {len(episodes)}")
    print(f"  Episode ends: {episode_ends}")
    
    return replay_buffer


def process_single_task(task_path):
    """处理单个task目录"""
    print(f"处理数据集: {task_path}")
    
    # 分析视频结构
    episodes = analyze_video_structure(task_path)
    
    if not episodes:
        print("错误: 没有找到有效的episode")
        return False
    
    # 创建replay_buffer
    create_minimal_replay_buffer(task_path, episodes)
    print("完成!")
    return True


def main():
    dataset_base_path = '/home/alien/Research/xskill/datasets/rh20T_test'
    
    dataset_base_path = Path(dataset_base_path)
    if not dataset_base_path.exists():
        raise ValueError(f"数据集路径不存在: {dataset_base_path}")
    
    # 查找所有task目录
    task_dirs = [d for d in dataset_base_path.iterdir() if d.is_dir() and d.name.startswith('task_')]
    task_dirs.sort()  # 按名称排序
    
    if not task_dirs:
        print("错误: 没有找到任何task目录")
        return
    
    print(f"发现 {len(task_dirs)} 个task目录:")
    for task_dir in task_dirs:
        print(f"  - {task_dir.name}")
    
    print("\n开始处理所有task目录...")
    
    success_count = 0
    failed_tasks = []
    
    for task_dir in task_dirs:
        print(f"\n{'='*50}")
        try:
            if process_single_task(task_dir):
                success_count += 1
            else:
                failed_tasks.append(task_dir.name)
        except Exception as e:
            print(f"处理 {task_dir.name} 时发生错误: {e}")
            failed_tasks.append(task_dir.name)
    
    print(f"\n{'='*50}")
    print(f"处理完成! 成功: {success_count}/{len(task_dirs)}")
    
    if failed_tasks:
        print(f"失败的task: {', '.join(failed_tasks)}")
    else:
        print("所有task都处理成功!")


if __name__ == "__main__":
    main()