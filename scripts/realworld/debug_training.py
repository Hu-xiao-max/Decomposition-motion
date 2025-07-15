import hydra
import pytorch_lightning as pl
import torch
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig, OmegaConf
from pytorch_lightning.callbacks import ModelCheckpoint
import wandb
from xskill.dataset.dataset import ConcatDataset
from xskill.utility.transform import get_transform_pipeline
import numpy as np


@hydra.main(version_base=None,
            config_path="../../config/realworld",
            config_name="skill_discovery")
def debug_pretrain(cfg: DictConfig):
    """调试版本的训练函数，包含详细的数据观察点"""
    output_dir = HydraConfig.get().runtime.output_dir
    print(f"output_dir: {output_dir}")
    
    # ========= 断点1: 数据预处理流程观察 =========
    pretrain_pipeline = get_transform_pipeline(cfg.augmentations)
    print(f"Data augmentation pipeline: {cfg.augmentations}")
    
    # ========= 断点2: 数据集构建观察 =========
    robot_dataset = hydra.utils.instantiate(cfg.robot_dataset)
    human_dataset = hydra.utils.instantiate(cfg.human_dataset)
    
    print(f"Robot dataset size: {len(robot_dataset)}")
    print(f"Human dataset size: {len(human_dataset)}")
    
    # 观察单个数据样本
    if len(robot_dataset) > 0:
        robot_sample = robot_dataset[0]
        print(f"Robot sample structure: {type(robot_sample)}")
        print(f"Robot sample im_q shape: {robot_sample.im_q.shape}")
        print(f"Robot sample index: {robot_sample.index}")
        print(f"Robot sample info: {robot_sample.info}")
    
    if len(human_dataset) > 0:
        human_sample = human_dataset[0]
        print(f"Human sample structure: {type(human_sample)}")
        print(f"Human sample im_q shape: {human_sample.im_q.shape}")
        
    combine_dataset = ConcatDataset(robot_dataset, human_dataset)
    print(f"Combined dataset size: {len(combine_dataset)}")
    
    # ========= 断点3: DataLoader观察 =========
    dataloader = torch.utils.data.DataLoader(
        combine_dataset,
        batch_size=cfg.batch_size,
        num_workers=cfg.num_workers,
        shuffle=True,
        pin_memory=cfg.pin_memory,
        persistent_workers=cfg.persistent_workers,
        drop_last=cfg.drop_last)

    steps_per_epoch = len(dataloader)
    print(f"Steps per epoch: {steps_per_epoch}")

    # ========= 断点4: 模型构建观察 =========
    model = hydra.utils.instantiate(
        cfg.Model,
        steps_per_epoch=steps_per_epoch,
        pretrain_pipeline=pretrain_pipeline,
    )
    
    print(f"Model structure:")
    print(f"  - Encoder: {type(model.encoder_q)}")
    print(f"  - Skill prior: {type(model.skill_prior)}")
    print(f"  - Slide window: {model.slide}")
    print(f"  - Stack frames: {model.stack_frames}")
    
    # ========= 断点5: 训练数据流观察 =========
    print("\n=== 开始观察训练数据流 ===")
    
    # 获取一个batch的数据
    for batch_idx, batch in enumerate(dataloader):
        robot_batch, human_batch = batch
        
        print(f"\nBatch {batch_idx}:")
        print(f"Robot batch - eps_im shape: {robot_batch[0].shape}")
        print(f"Human batch - eps_im shape: {human_batch[0].shape}")
        
        # 模拟训练步骤中的数据处理
        eps_im = robot_batch[0]  # (B,T,C,H,W)
        batch_size = eps_im.shape[0]
        
        print(f"Episode images shape: {eps_im.shape}")
        print(f"Batch size: {batch_size}")
        
        # 观察数据预处理
        for i in range(min(2, batch_size)):  # 只观察前2个样本
            im = eps_im[i]
            print(f"\nSample {i}:")
            print(f"  Original im shape: {im.shape}")
            print(f"  Min value: {im.min():.4f}, Max value: {im.max():.4f}")
            
            # 应用数据增强
            im_q = torch.stack([
                pretrain_pipeline(im[j:j + model.slide + 1])
                for j in range(len(im) - model.slide)
            ])
            
            print(f"  After augmentation im_q shape: {im_q.shape}")
            print(f"  After augmentation - Min: {im_q.min():.4f}, Max: {im_q.max():.4f}")
            
        # 只处理第一个batch用于观察
        if batch_idx == 0:
            break
    
    print("\n=== 数据流观察完成 ===")
    
    # 可以选择继续正常训练或停止
    # 如果想继续训练，取消下面的注释
    """
    checkpoint_callback = ModelCheckpoint(
        every_n_epochs=cfg.callback.every_n_epoch,
        save_top_k=-1,
        dirpath=output_dir,
        filename="{epoch:02d}",
    )

    wandb.init(project="Real_kitchen_prototype_learning_debug")
    wandb.config.update(OmegaConf.to_container(cfg))
    
    trainer = pl.Trainer(
        callbacks=[checkpoint_callback],
        enable_checkpointing=True,
        default_root_dir=output_dir,
        max_epochs=1,  # 只训练1个epoch用于调试
        **cfg.Trainer,
    )

    trainer.fit(model=model, train_dataloaders=dataloader)
    """


if __name__ == "__main__":
    debug_pretrain() 