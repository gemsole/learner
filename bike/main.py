import torch
import torch.nn as nn

# 固定单线程，保证 CPU 训练结果可复现
torch.set_num_threads(1)

# 加载数据
import data
features = ["season","yr","mnth","weekday","holiday","workingday","weathersit","temp","atemp","hum","windspeed"]
LOOK_BACK = 7
X_train, X_test, y_train, y_test, y_scaler = data.load_data("./dataset/day.csv", features, LOOK_BACK)

# 导入模型与训练/评估工具
from model import BikeRNN
from train import train
from test import test

# 训练配置
EPOCHS = 200
BATCH_SIZE = 32
LR = 5e-4
SEEDS = 3  # 多随机种子集成，降低单次训练波动

preds = []
for seed in range(SEEDS):
    torch.manual_seed(seed)
    model = BikeRNN(X_train.shape[2], 64, 2)
    criterion = nn.MSELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    train(EPOCHS, model, X_train, y_train, criterion, optimizer,
          batch_size=BATCH_SIZE, scheduler=scheduler)

    seed_pred, _ = test(model, X_test, y_test, criterion)
    preds.append(seed_pred)

# 集成预测
test_pred = torch.stack(preds).mean(dim=0)
test_loss = criterion(test_pred, y_test)
print(f"\nTest Loss (scaled MSE): {test_loss.item():.6f}")

# 反归一化并计算原始尺度指标
y_true = y_scaler.inverse_transform(y_test.numpy())
y_pred = y_scaler.inverse_transform(test_pred.numpy())

import matplotlib.pyplot as plt

plt.title("Bike Count Prediction")
plt.plot(y_true[:, 0], label="True")
plt.plot(y_pred[:, 0], label="Pred")
plt.xlabel("Time")
plt.ylabel("Bike Count")
plt.legend()
plt.savefig("./result/bike_pred.png")
plt.show()
