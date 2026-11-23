import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler

features = ["season", "yr", "mnth", "weekday", "holiday", "workingday", "weathersit",
            "temp", "atemp", "hum", "windspeed"]
target = "cnt"


# ---------------------- 特征工程 ----------------------
# 在原始特征基础上补充：年内周期的 sin/cos 编码 + 客流滞后特征
# 滞后特征只使用当天之前的值，不会泄漏目标当天的 cnt
def _build_features(df, base_features, use_lag=True):
    feat = df[base_features].copy()

    doy = pd.to_datetime(df["dteday"]).dt.dayofyear
    feat["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    feat["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    feat["weekday_sin"] = np.sin(2 * np.pi * df["weekday"] / 7)
    feat["weekday_cos"] = np.cos(2 * np.pi * df["weekday"] / 7)

    if use_lag:
        cnt = df[target]
        feat["cnt_lag1"] = cnt.shift(1)
        feat["cnt_lag7"] = cnt.shift(7)
        feat["cnt_roll7"] = cnt.shift(1).rolling(7).mean()
    return feat


# ---------------------- 时序数据集构造 ----------------------
# 当日预测：窗口为 [t-look_back+1, t]，标签为窗口最后一天的 cnt
def create_sequences(features_scaled, target_scaled, look_back):
    X, y, pos = [], [], []
    for i in range(look_back - 1, len(features_scaled)):
        X.append(features_scaled[i - look_back + 1:i + 1])
        y.append(target_scaled[i])
        pos.append(i)
    return np.array(X), np.array(y), np.array(pos)


# ---------------------- 数据加载 ----------------------
def load_data(path="./dataset/day.csv", features=features, look_back=14, split=0.9):
    df = pd.read_csv(path)
    frame = _build_features(df, features).dropna()
    y_raw = df.loc[frame.index, target].values.reshape(-1, 1)

    # 按原始时间顺序划分，测试段之前的历史序列仍可用于构造输入窗口
    split_idx = int(len(df) * split)
    train_count = int((frame.index < split_idx).sum())

    # 归一化参数只用训练段计算，避免测试集信息泄漏
    X_scaler = MinMaxScaler(feature_range=(0, 1)).fit(frame.iloc[:train_count].values)
    y_scaler = MinMaxScaler(feature_range=(0, 1)).fit(y_raw[:train_count])

    X_scaled = X_scaler.transform(frame.values)
    y_scaled = y_scaler.transform(y_raw)

    X_all, y_all, pos = create_sequences(X_scaled, y_scaled, look_back)
    train_mask = pos < train_count

    X_train = torch.tensor(X_all[train_mask], dtype=torch.float32)
    X_test = torch.tensor(X_all[~train_mask], dtype=torch.float32)
    y_train = torch.tensor(y_all[train_mask], dtype=torch.float32)
    y_test = torch.tensor(y_all[~train_mask], dtype=torch.float32)

    return X_train, X_test, y_train, y_test, y_scaler
