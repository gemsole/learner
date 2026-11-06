import torch
import torch.nn as nn
from tools import *


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(
        self,
        in_channels,
        out_channels,
        stride=1,
        downsample=None,
    ):
        super().__init__()

        # 3x3 卷积主路径
        self.conv1 = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias=False,
        )
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv2d(
            out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm2d(out_channels)

        # 下采样层（用于调整输入尺寸或通道数，使得能够与残差相加）
        self.downsample = downsample

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        # 残差连接：F(x) + x
        out += identity
        out = self.relu(out)

        return out


class ResNet(nn.Module):
    """支持自定义基础通道数的 ResNet 架构"""

    def __init__(
        self,
        block,
        layers,
        num_classes,
        base_channels=64,  # 新增：基础通道数（原版为 64，可设为 32 或 16）
        zero_init_residual=False,
    ):
        super().__init__()

        self.in_channels = base_channels

        # 初始卷积层
        self.conv1 = nn.Conv2d(
            3, self.in_channels, kernel_size=7, stride=2, padding=3, bias=False
        )
        self.bn1 = nn.BatchNorm2d(self.in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        # 四个主要的残差层组，按比例缩放通道数
        self.layer1 = self._make_layer(block, base_channels, layers[0], stride=1)
        self.layer2 = self._make_layer(block, base_channels * 2, layers[1], stride=2)
        self.layer3 = self._make_layer(block, base_channels * 4, layers[2], stride=2)
        self.layer4 = self._make_layer(block, base_channels * 8, layers[3], stride=2)

        # 全局平均池化与分类全连接层
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(base_channels * 8 * block.expansion, num_classes)

        # 参数初始化...（省略初始化代码保持一致）

    def _make_layer(self, block, out_channels, blocks, stride=1):
        downsample = None
        if stride != 1 or self.in_channels != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(
                    self.in_channels,
                    out_channels * block.expansion,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm2d(out_channels * block.expansion),
            )

        layers = []
        layers.append(block(self.in_channels, out_channels, stride, downsample))
        self.in_channels = out_channels * block.expansion

        for _ in range(1, blocks):
            layers.append(block(self.in_channels, out_channels))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x


def resnet18(num_classes=10, base_channels=32):
    """构建轻量化 ResNet-18，默认基础通道数降为 32（原版为 64）"""
    return ResNet(
        BasicBlock, [2, 2, 2, 2], num_classes=num_classes, base_channels=base_channels
    )


if __name__ == "__main__":
    print("CUDA 可用:", torch.cuda.is_available())
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = resnet18()
    tool = Tools("config.toml", model, device=device)
    tool.load()
    for epoch in range(1, 21):
        print(f"Epoch {epoch}")
        loss = tool.train()
        acc = tool.test()
        tool.log(f"Epoch {epoch}, Loss: {loss:.4f}, Acc: {acc:.4f}")
    tool.save(model.state_dict(), "resnet18.pth")
