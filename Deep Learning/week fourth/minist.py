import torch
import torch.nn as nn
from torchvision import datasets, transforms

# 1. 加载 MNIST 数据集
transform = transforms.ToTensor()
train_set = datasets.MNIST('data', train=True, download=True, transform=transform)
test_set = datasets.MNIST('data', train=False, download=True, transform=transform)
train_loader = torch.utils.data.DataLoader(train_set, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_set, batch_size=1000)

# 2. 定义简单的全连接网络
model = nn.Sequential(
    nn.Flatten(),               # 28x28 图片展平成 784 维向量
    nn.Linear(28 * 28, 128),
    nn.ReLU(),
    nn.Linear(128, 10)          # 输出 0-9 十个数字的分数
)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()

# 3. 训练
for epoch in range(5):
    for images, labels in train_loader:
        optimizer.zero_grad()
        loss = loss_fn(model(images), labels)
        loss.backward()
        optimizer.step()
    print(f'epoch {epoch + 1}, loss: {loss.item():.4f}')

# 4. 测试
correct = 0
with torch.no_grad():
    for images, labels in test_loader:
        pred = model(images).argmax(dim=1)
        correct += (pred == labels).sum().item()
print(f'测试准确率: {correct / len(test_set):.2%}')

