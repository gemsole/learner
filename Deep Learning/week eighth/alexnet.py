import os

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# ========== 1. 设备与路径 ==========
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(BASE_DIR, "..", "data")  # 复用项目根目录下的 data/MNIST

# ========== 2. 数据预处理 ==========
# AlexNet 原论文输入为 224x224 三通道图像，MNIST 需要放大并转成三通道
transform = transforms.Compose([
    transforms.Resize(224),                        # 28x28 → 224x224
    transforms.Grayscale(num_output_channels=3),   # 1 通道灰度图 → 3 通道
    transforms.ToTensor(),                         # 像素 0~255 → 0~1
    transforms.Normalize((0.1307,) * 3, (0.3081,) * 3),  # MNIST 均值、标准差
])

train_data = datasets.MNIST(root=DATA_ROOT, train=True, transform=transform, download=True)
test_data = datasets.MNIST(root=DATA_ROOT, train=False, transform=transform, download=True)

train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
test_loader = DataLoader(test_data, batch_size=32, shuffle=False)

# ========== 3. 搭建 AlexNet 网络模型 ==========
class AlexNet(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        # 卷积特征提取部分：5 个卷积层 + 3 个最大池化层
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),   # 224x224 → 64x55x55
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),                   # 64x55x55 → 64x27x27

            nn.Conv2d(64, 192, kernel_size=5, padding=2),            # 64x27x27 → 192x27x27
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),                   # 192x27x27 → 192x13x13

            nn.Conv2d(192, 384, kernel_size=3, padding=1),           # 192x13x13 → 384x13x13
            nn.ReLU(inplace=True),

            nn.Conv2d(384, 256, kernel_size=3, padding=1),           # 384x13x13 → 256x13x13
            nn.ReLU(inplace=True),

            nn.Conv2d(256, 256, kernel_size=3, padding=1),           # 256x13x13 → 256x13x13
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),                   # 256x13x13 → 256x6x6
        )

        # 全连接分类部分：3 个全连接层
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),

            nn.Dropout(p=0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),

            nn.Linear(4096, num_classes),                            # 输出 10 类 0~9
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)     # 256x6x6 → 9216
        x = self.classifier(x)
        return x


model = AlexNet().to(device)


# 打印每层输出的形状
def show_shapes():
    def hook(name):
        def fn(module, inputs, output):
            print(f"{name:<12} 输出形状: {tuple(output.shape)}")

        return fn

    handles = [
        m.register_forward_hook(hook(n))
        for n, m in model.named_modules()
        if len(list(m.children())) == 0 and not isinstance(m, nn.Dropout)
    ]
    model(torch.randn(1, 3, 224, 224).to(device))  # 用一张假输入跑一次前向
    for h in handles:
        h.remove()


show_shapes()

# ========== 4. 损失函数、优化器 ==========
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0005)  # AlexNet 原论文使用较小学习率


# ========== 5. 训练函数 ==========
def train(epoch):
    model.train()
    total_loss = 0
    for img, label in train_loader:
        img, label = img.to(device), label.to(device)
        optimizer.zero_grad()
        out = model(img)
        loss = criterion(out, label)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch:{epoch}, Train Loss:{total_loss / len(train_loader):.4f}", end="\t")


# ========== 6. 测试评估 ==========
def test():
    model.eval()
    correct = 0
    with torch.no_grad():
        for img, label in test_loader:
            img, label = img.to(device), label.to(device)
            out = model(img)
            pred = torch.argmax(out, dim=1)
            correct += (pred == label).sum().item()
    acc = correct / len(test_data)
    print(f"Test Acc: {acc:.4f}")


# ========== 7. 开始训练 ==========
if __name__ == "__main__":
    for epoch in range(1, 6):  # 训练5轮（CPU 上 224x224 输入较慢，可自行减少）
        train(epoch)
        test()
    torch.save(model.state_dict(), os.path.join(BASE_DIR, "alexnet.pth"))
    # 下次加载：model.load_state_dict(torch.load("alexnet.pth", map_location=device))
