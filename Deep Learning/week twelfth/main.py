import torch
import torch.nn as nn


# 加载数据
import data
LOOK_BACK = 7
X_train, X_test, y_train, y_test, y_scaler = data.load_data("./dataset/day.csv", LOOK_BACK)

# 导入模型与训练/评估工具
from model import BikeRNN
from train import train
from test import test

# 训练配置
EPOCHS = 200
BATCH_SIZE = 32
LR = 5e-4
SEEDS = 3  


torch.manual_seed(seed)
model = BikeRNN(X_train.shape[2], 64, 2)
criterion = nn.MSELoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

train(EPOCHS, model, X_train, y_train, criterion, optimizer,
        batch_size=BATCH_SIZE, scheduler=scheduler)


torch.save(model.state_dict(), "./result/bike_model.pth")

seed_pred = test(model, X_test)
test_loss = criterion(seed_pred, y_test)
print(f"\nTest Loss (scaled MSE): {test_loss.item():.6f}")
with open("test_loss.txt", "w") as f:
    f.write(f"Test Loss (scaled MSE): {test_loss.item():.6f}\n")


y_true = y_scaler.inverse_transform(y_test.numpy())
y_pred = y_scaler.inverse_transform(seed_pred.numpy())

import matplotlib.pyplot as plt

plt.title("Bike Count Prediction")
plt.plot(y_true[:, 0], label="True")
plt.plot(y_pred[:, 0], label="Pred")
plt.xlabel("Time")
plt.ylabel("Bike Count")
plt.legend()
plt.savefig("./result/bike_pred.png")
plt.show()
