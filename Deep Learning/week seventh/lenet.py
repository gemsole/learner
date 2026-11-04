import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


# ========== 2. 数据预处理 ==========
transform = transforms.Compose([
    transforms.ToTensor(),                      # 转为张量，像素0~255 → 0~1
    transforms.Normalize((0.1307,), (0.3081,))  # MNIST数据集均值、标准差归一化
])

# 加载MNIST数据集
train_data = datasets.MNIST(root='./data', train=True, transform=transform)
test_data = datasets.MNIST(root='./data', train=False, transform=transform)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

# ========== 3. 搭建LeNet-5网络模型 ==========
class LeNet(nn.Module):
    def __init__(self):
        super().__init__()
        # 卷积层
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5, padding=2)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.conv3 = nn.Conv2d(16, 120, kernel_size=5)
        self.pool = nn.MaxPool2d(2, 2)

        # 全连接层
        self.fc1 = nn.Linear(120, 84)
        # 输出层：10类 0~9
        self.fc2 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))   # 1x28x28 → 6x14x14
        x = self.pool(torch.relu(self.conv2(x)))   # 6x14x14 → 16x5x5
        x = torch.flatten(torch.relu(self.conv3(x)), 1)   # 120x1x1 → 120
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = LeNet()


# 打印每层输出的形状
def show_shapes():
    def hook(module, inputs, output):
        print(f"{module.__class__.__name__:<10} 输出形状: {tuple(output.shape)}")

    handles = [m.register_forward_hook(hook) for m in model.children()]
    model(torch.randn(1, 1, 28, 28))  # 用一张假输入跑一次前向
    for h in handles:
        h.remove()


show_shapes()

# ========== 4. 损失函数、优化器 ==========
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# ========== 5. 训练函数 ==========
def train(epoch):
    model.train()
    total_loss = 0
    for img, label in train_loader:
        optimizer.zero_grad()
        out = model(img)
        loss = criterion(out, label)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch:{epoch}, Train Loss:{total_loss/len(train_loader):.4f}", end="\t")

# ========== 6. 测试评估 ==========
def test():
    model.eval()
    correct = 0
    with torch.no_grad():
        for img, label in test_loader:
            out = model(img)
            pred = torch.argmax(out, dim=1)
            correct += (pred == label).sum().item()
    acc = correct / len(test_data)
    print(f"Test Acc: {acc:.4f}")

# ========== 7. 开始训练 ==========
if __name__ == "__main__":
    for epoch in range(1, 11):  # 训练10轮
        train(epoch)
        test()
    torch.save(model.state_dict(), "lenet.pth")
    
