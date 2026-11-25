import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler


target = "cnt"
features = ["season", "yr", "mnth", "weekday", "holiday", "workingday", "weathersit",
            "temp", "atemp", "hum", "windspeed"]

# ---------------------- 特征工程 ----------------------
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
    print(feat.columns)
    print(feat.head())
    return feat


# ---------------------- 时序数据集构造 ----------------------
def create_sequences(features_scaled, target_scaled, look_back):
    X, y, pos = [], [], []
    for i in range(look_back - 1, len(features_scaled) - 1):
        X.append(features_scaled[i - look_back + 1:i + 1])
        y.append(target_scaled[i + 1])
        pos.append(i)
    return np.array(X), np.array(y), np.array(pos)


# ---------------------- 数据加载 ----------------------
def load_data(path="./dataset/day.csv", look_back=7, split=0.9):
    df = pd.read_csv(path)
    frame = _build_features(df, features).dropna()
    y_raw = df.loc[frame.index, target].values.reshape(-1, 1)

    split_idx = int(len(df) * split)
    train_count = int((frame.index < split_idx).sum())

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
