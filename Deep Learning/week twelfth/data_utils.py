"""
数据加载与预处理模块
====================
负责 Bike-Sharing-Dataset/day.csv 的加载、归一化、
时间序列样本构造、训练/测试集划分、DataLoader 创建。
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset


def load_data(data_path=None):
    """
    加载共享单车日数据，提取租赁量 cnt 并归一化。

    Returns:
        df          : 原始 DataFrame
        cnt_data    : 原始租赁量 (N, 1) float32
        cnt_scaled  : 归一化后租赁量 (N, 1) float32
        scaler      : 训练好的 MinMaxScaler（用于 inverse_transform）
    """
    if data_path is None:
        data_path = os.path.join("Bike-Sharing-Dataset", "day.csv")

    df = pd.read_csv(data_path)
    print(f"数据加载完成: {df.shape[0]} 条记录, {df.shape[1]} 列")

    cnt_data = df["cnt"].values.reshape(-1, 1).astype(np.float32)
    print(
        f"租赁量统计: 均值={cnt_data.mean():.1f}, 标准差={cnt_data.std():.1f}, "
        f"最小={cnt_data.min():.1f}, 最大={cnt_data.max():.1f}"
    )

    scaler = MinMaxScaler(feature_range=(0, 1))
    cnt_scaled = scaler.fit_transform(cnt_data).astype(np.float32)

    return df, cnt_data, cnt_scaled, scaler


def create_sequences(data, seq_len, pred_len):
    """
    构造滑动窗口时间序列样本。

    输入: 过去 seq_len 天的序列
    标签: 未来 pred_len 天的值

    Args:
        data     : 归一化后的时间序列 (N, 1)
        seq_len  : 输入时间步长度
        pred_len : 预测长度

    Returns:
        X : (n_samples, seq_len, 1)
        y : (n_samples, pred_len)
    """
    X, y = [], []
    for i in range(len(data) - seq_len - pred_len + 1):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len : i + seq_len + pred_len])
    return np.array(X), np.array(y).reshape(-1, pred_len)


def prepare_dataloaders(
    cnt_scaled, seq_len=7, pred_len=1, batch_size=32, train_ratio=0.8
):
    """
    一站式完成序列构造、划分、Tensor 转换、DataLoader 创建。

    Args:
        cnt_scaled   : 归一化后的租赁量序列 (N, 1)
        seq_len      : 输入时间步
        pred_len     : 预测长度
        batch_size   : DataLoader batch size
        train_ratio  : 训练集比例

    Returns:
        X_train, X_test, y_train, y_test   : numpy 数组
        X_train_t, y_train_t, X_test_t, y_test_t  : torch Tensor
        train_loader                        : DataLoader
        train_size                          : 训练集样本数
    """
    X, y = create_sequences(cnt_scaled, seq_len, pred_len)
    print(f"序列形状: X={X.shape}, y={y.shape}  (时间步={seq_len})")

    train_size = int(len(X) * train_ratio)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    print(f"训练集: {X_train.shape[0]}, 测试集: {X_test.shape[0]}")

    X_train_t = torch_from_numpy(X_train)
    y_train_t = torch_from_numpy(y_train)
    X_test_t = torch_from_numpy(X_test)
    y_test_t = torch_from_numpy(y_test)

    train_loader = DataLoader(
        TensorDataset(X_train_t, y_train_t), batch_size=batch_size, shuffle=True
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        X_train_t,
        y_train_t,
        X_test_t,
        y_test_t,
        train_loader,
        train_size,
        X,
        y,
    )


def torch_from_numpy(arr):
    """numpy -> torch Tensor (float32)，避免重复 import。"""
    import torch

    return torch.from_numpy(arr)
