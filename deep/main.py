import torch
import torch.nn as nn
from tools import *


# 1. 定义 ResNet 的基础残差块 (Residual Block)
class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes, planes, stride=1):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(
            in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False
        )
        self.bn1 = nn.BatchNorm2d(planes)

        self.conv2 = nn.Conv2d(
            planes, planes, kernel_size=3, stride=1, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm2d(planes)

        self.shortcut = nn.Sequential()
        # 如果步长不为 1 或者输入输出通道不一致，需要通过 1x1 卷积调整维度以匹配残差相加
        if stride != 1 or in_planes != self.expansion * planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(
                    in_planes,
                    self.expansion * planes,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm2d(self.expansion * planes),
            )

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = torch.relu(out)
        return out


# 2. 手动搭建 ResNet-18 架构
class ResNet(nn.Module):
    def __init__(self, block, num_blocks, num_classes=10):
        super(ResNet, self).__init__()
        self.in_planes = 64

        # 针对 CIFAR-10 (32x32) 调整初始卷积层
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)

        # 4 个主要的残差层组 (ResNet-18 对应配置：[2, 2, 2, 2])
        self.layer1 = self._make_layer(block, 64, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, 128, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, 256, num_blocks[2], stride=2)
        self.layer4 = self._make_layer(block, 512, num_blocks[3], stride=2)

        # 全连接分类层
        self.linear = nn.Linear(512 * block.expansion, num_classes)
        self.early_stopping = EarlyStopping(patience=5, verbose=False)

    def _make_layer(self, block, planes, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride))
            self.in_planes = planes * block.expansion
        return nn.Sequential(*layers)

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = nn.functional.adaptive_avg_pool2d(out, (1, 1))
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out


def ResNet18():
    return ResNet(BasicBlock, [2, 2, 2, 2])


# ==================== 3. 训练与测试主程序 ====================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ResNet18().to(device)
tools = Tools("config.toml", model, device)
train_loader, test_loader, test_data = tools.load()

if __name__ == "__main__":
    print('start')
    print(f'use {device} device')
    for epoch in range(20):
        print('start train')
        loss = tools.train(train_loader)
        print('start test')
        acc = tools.test(test_loader, test_data)
        tools.log(f"Epoch {epoch}, Loss: {loss:.4f}, Acc: {acc:.4f}")
        model.early_stopping(acc, model)
        if model.early_stopping.early_stop:
            tools.log("Early stopping triggered")
            break
    tools.save(model.early_stopping.best_model, "best_model.pth")

