import torch
import torch.nn as nn
        
# 加载数据
import data
features = ["season","yr","mnth","weekday","holiday","workingday","weathersit","temp","atemp","hum","windspeed"]
X_train, X_test, y_train, y_test, y_scaler = data.load_data("./dataset/day.csv", features, 7)
        
# 导入模型
from model import BikeRNN
        
# 初始化
model = BikeRNN(X_train.shape[2], 32, 3)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 训练模型
from train import train
train(150, model, X_train, y_train, criterion, optimizer)

# 预测评估
model.eval()
from test import test
test_pred, test_loss = test(model, X_test, y_test, criterion)
print(f"Test Loss: {test_loss.item():.4f}")

# 反归一化
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
