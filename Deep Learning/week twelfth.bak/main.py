"""
基于循环神经网络（RNN）的共享单车租赁量预测 —— 主入口
======================================================
串起数据加载 -> 模型实例化 -> 训练 -> 评估 -> 可视化 -> 滚动预测
"""

import matplotlib.pyplot as plt
import torch
from data_utils import load_data, prepare_dataloaders
from model import BikeRNN  # 换成 BikeLSTM 即可切换模型
from train import train_model
from test import evaluate, rolling_predict_future, print_future_preds


# ---------------------- 设备 ----------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")

# ---------------------- 超参数 ----------------------
SEQ_LEN = 7  # 滑动窗口: 过去 7 天
PRED_LEN = 1  # 预测第 8 天
BATCH_SIZE = 32
HIDDEN_SIZE = 32  # 隐藏层维度
NUM_LAYERS = 3  # RNN 层数
LEARNING_RATE = 0.01
EPOCHS = 500
TRAIN_RATIO = 0.8
PATIENCE = 60  # 早停耐心值


# ---------------------- 1. 数据 ----------------------
df, cnt_data, cnt_scaled, scaler = load_data()

(
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
    X_all,
    y_all,
) = prepare_dataloaders(cnt_scaled, SEQ_LEN, PRED_LEN, BATCH_SIZE, TRAIN_RATIO)


# ---------------------- 2. 模型 ----------------------
model = BikeRNN()

print(f"\n模型结构:\n{model}")
total_params = sum(p.numel() for p in model.parameters())
print(f"可训练参数: {total_params:,}")


# ---------------------- 3. 训练 ----------------------
model, train_losses = train_model(
    model=model,
    train_loader=train_loader,
    device=device,
    epochs=EPOCHS,
    lr=LEARNING_RATE,
    patience=PATIENCE,
)


# ---------------------- 4. 评估 ----------------------
metrics, preds, truths = evaluate(
    model=model,
    scaler=scaler,
    device=device,
    X_train_t=X_train_t,
    y_train=y_train,
    X_test_t=X_test_t,
    y_test=y_test,
    X_all=X_all,
    y_all=y_all,
)
pred_train, pred_test, pred_all = preds
y_train_orig, y_test_orig, y_all_orig = truths
rmse, mae, mape = metrics["rmse"], metrics["mae"], metrics["mape"]


# ---------------------- 5. 可视化 ----------------------
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# (1) 训练损失
axes[0, 0].plot(train_losses, "b-", lw=1.5)
axes[0, 0].set_title("训练损失曲线 (Training Loss)", fontsize=13)
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("MSE Loss")
axes[0, 0].grid(True, alpha=0.3)

# (2) 测试集 真实 vs 预测
axes[0, 1].plot(y_test_orig, "b-", label="真实 Actual", lw=1.5, alpha=0.8)
axes[0, 1].plot(pred_test, "r-", label="预测 Predicted", lw=1.5, alpha=0.8)
axes[0, 1].set_title(
    f"测试集: 真实值 vs 预测值\nRMSE={rmse:.1f}, MAE={mae:.1f}, MAPE={mape:.1f}%",
    fontsize=13,
)
axes[0, 1].set_xlabel("样本索引")
axes[0, 1].set_ylabel("租赁量 cnt")
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# (3) 散点图
axes[1, 0].scatter(y_test_orig, pred_test, alpha=0.6, s=30, c="steelblue")
lo = min(y_test_orig.min(), pred_test.min())
hi = max(y_test_orig.max(), pred_test.max())
axes[1, 0].plot([lo, hi], [lo, hi], "r--", lw=2, label="理想线")
axes[1, 0].set_title("预测散点图", fontsize=13)
axes[1, 0].set_xlabel("真实值")
axes[1, 0].set_ylabel("预测值")
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# (4) 全量拟合
axes[1, 1].plot(y_all_orig[:train_size], "b-", label="训练集真实", lw=1, alpha=0.7)
axes[1, 1].plot(
    range(train_size), pred_all[:train_size], "g-", label="训练集预测", lw=1, alpha=0.7
)
axes[1, 1].plot(
    range(train_size, len(y_all_orig)), y_all_orig[train_size:], "b-", lw=1, alpha=0.3
)
axes[1, 1].plot(
    range(train_size, len(y_all_orig)),
    pred_all[train_size:],
    "r-",
    label="测试集预测",
    lw=1.5,
    alpha=0.8,
)
axes[1, 1].axvline(train_size, color="gray", ls="--", alpha=0.5, label="分界线")
axes[1, 1].set_title("全部数据拟合效果", fontsize=13)
axes[1, 1].set_xlabel("天数")
axes[1, 1].set_ylabel("租赁量 cnt")
axes[1, 1].legend(fontsize=8)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("bike_rnn_results.png", dpi=150, bbox_inches="tight")
print("\n结果图已保存: bike_rnn_results.png")
plt.show()


# ---------------------- 6. 滚动预测未来 7 天 ----------------------
future_preds = rolling_predict_future(
    model=model,
    scaler=scaler,
    cnt_scaled=cnt_scaled,
    device=device,
    seq_len=SEQ_LEN,
    future_days=7,
)
print_future_preds(future_preds, df)

print("\n任务完成!")
