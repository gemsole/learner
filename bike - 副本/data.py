import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch


# 时序数据集构造器：输入为前 look_back 天特征，标签为第 look_back 天的 cnt
def create_sequences(features_scaled, target_scaled, look_back):
    X, y = [], []
    for i in range(len(features_scaled) - look_back):
        X.append(features_scaled[i:i+look_back, :])
        y.append(target_scaled[i+look_back])
    return np.array(X), np.array(y)


features = ["season","yr","mnth","weekday","holiday","workingday","weathersit","temp","atemp","hum","windspeed"]
target = "cnt"


# ---------------------- 数据加载 ----------------------
def load_data(path="./dataset/day.csv", features=features, look_back=7, split=0.9):
    df = pd.read_csv(path)
    X_raw = df[features]
    y_raw = df[[target]]

    # 划分训练集和测试集
    train_end = int(len(df) * split)

    # 归一化参数只用训练段计算，避免测试集信息泄漏
    X_scaler = MinMaxScaler(feature_range=(0,1))
    X_scaler.fit(X_raw.iloc[:train_end].values)
    y_scaler = MinMaxScaler(feature_range=(0,1))
    y_scaler.fit(y_raw.iloc[:train_end].values)

    X_scaled = X_scaler.transform(X_raw.values)
    y_scaled = y_scaler.transform(y_raw.values)

    # 训练集：用前 train_end 行连续数据自己构造序列
    X_train, y_train = create_sequences(
        X_scaled[:train_end], y_scaled[:train_end], look_back
    )
    # 测试集：用 train_end 之后的连续数据自己构造序列
    X_test, y_test = create_sequences(
        X_scaled[train_end:], y_scaled[train_end:], look_back
    )

    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.float32)

    return X_train, X_test, y_train, y_test, y_scaler
