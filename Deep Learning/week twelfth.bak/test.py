import numpy as np
import pandas as pd
import torch
from sklearn.metrics import mean_squared_error, mean_absolute_error


def evaluate(model, scaler, device, X_train_t, y_train, X_test_t, y_test, X_all, y_all):
    """
    评估训练集 & 测试集，返回反归一化后的预测结果 + 指标字典。

    Returns:
        metrics  : dict {train_rmse, rmse, mae, mape}
        pred_train, pred_test, pred_all : 反归一化后的 numpy 数组
        y_train_orig, y_test_orig, y_all_orig : 反归一化后的真实值
    """
    model.eval()
    with torch.no_grad():
        pred_train = scaler.inverse_transform(model(X_train_t.to(device)).cpu().numpy())
        pred_test = scaler.inverse_transform(model(X_test_t.to(device)).cpu().numpy())
        pred_all = scaler.inverse_transform(
            model(torch.from_numpy(X_all).to(device)).cpu().numpy()
        )

    y_train_orig = scaler.inverse_transform(y_train)
    y_test_orig = scaler.inverse_transform(y_test)
    y_all_orig = scaler.inverse_transform(y_all)

    train_rmse = np.sqrt(mean_squared_error(y_train_orig, pred_train))
    rmse = np.sqrt(mean_squared_error(y_test_orig, pred_test))
    mae = mean_absolute_error(y_test_orig, pred_test)
    mape = np.mean(np.abs((y_test_orig - pred_test) / np.maximum(y_test_orig, 1))) * 100

    metrics = {
        "train_rmse": train_rmse,
        "rmse": rmse,
        "mae": mae,
        "mape": mape,
    }

    print(f"\n{'='*55}")
    print(f"测试集评估:")
    print(f"{'='*55}")
    print(f"RMSE  = {rmse:.2f}")
    print(f"MAE   = {mae:.2f}")
    print(f"MAPE  = {mape:.2f}%")
    print(f"{'='*55}")
    print(f"训练集 RMSE = {train_rmse:.2f}")

    return (
        metrics,
        (pred_train, pred_test, pred_all),
        (y_train_orig, y_test_orig, y_all_orig),
    )


def rolling_predict_future(model, scaler, cnt_scaled, device, seq_len, future_days=7):
    """
    滚动预测未来 N 天租赁量（用前一步预测值做下一步输入）。

    Args:
        model        : 训练好的模型
        scaler       : 训练好的 MinMaxScaler
        cnt_scaled   : 归一化后的历史序列 (N, 1)
        device       : torch.device
        seq_len      : 滑动窗口长度
        future_days  : 预测天数

    Returns:
        future_preds : list[float]，反归一化后的未来租赁量
    """
    model.eval()
    future_preds = []
    current = cnt_scaled[-seq_len:].copy().reshape(1, seq_len, 1)

    with torch.no_grad():
        for _ in range(future_days):
            seq_t = torch.from_numpy(current).to(device)
            pred_scaled = model(seq_t)
            val = scaler.inverse_transform(pred_scaled.cpu().numpy())[0, 0]
            future_preds.append(val)
            # 滑动窗口更新: 丢掉最旧的一天，加入新预测
            current = np.concatenate(
                [current[:, 1:, :], pred_scaled.cpu().numpy().reshape(1, 1, 1)], axis=1
            )

    return future_preds


def print_future_preds(future_preds, df):
    """把滚动预测结果以日期+数量格式打印出来。"""
    print(f"\n{'='*55}")
    print(f"扩展: 滚动预测未来 {len(future_preds)} 天租赁量")
    print(f"{'='*55}")

    last_date = pd.to_datetime(df["dteday"].iloc[-1])
    print(f"\n数据截止: {df['dteday'].iloc[-1]}")
    for i, v in enumerate(future_preds):
        d = last_date + pd.Timedelta(days=i + 1)
        print(f"  {d.strftime('%Y-%m-%d')}: {v:.0f} 辆")

    print(f"\n{'='*55}")
