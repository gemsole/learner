import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from early_stopping import EarlyStopping

# ========== 2. 数据预处理 ==========
# VGG 原论文输入为 224x224 三通道图像，CIFAR-10 的 32x32 需要放大到 224x224
transform = transforms.Compose(
    [
        transforms.Resize(224),  # 28x28 → 224x224
        transforms.ToTensor(),  # 像素 0~255 → 0~1
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.209108)),
    ]
)


train_data = datasets.CIFAR10(
    root="../data", train=True, transform=transform, download=False
)
test_data = datasets.CIFAR10(
    root="../data", train=False, transform=transform, download=False
)

train_loader = DataLoader(
    train_data,
    batch_size=256,
    shuffle=True,
    num_workers=8,
    pin_memory=True,
    persistent_workers=True,
    drop_last=True,
)
test_loader = DataLoader(
    test_data,
    batch_size=256,
    shuffle=False,
    num_workers=8,
    pin_memory=True,
    persistent_workers=True,
    drop_last=False,
)


# ========== 3. 搭建 VGG-16 网络模型 ==========
# VGG-16（配置 D）：13 个卷积层 + 3 个全连接层 = 16 层
# 特点：全部使用 3x3 小卷积核（stride=1, padding=1 保持尺寸不变），
#       每 2~3 层卷积后接一次 2x2 最大池化（尺寸减半、通道数翻倍）
class VGG16(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        # 卷积特征提取部分：5 个卷积块，共 13 个卷积层
        self.features = nn.Sequential(
            # ---- Block 1 ----
            nn.Conv2d(3, 64, kernel_size=3, padding=1),  # 3x224x224  → 64x224x224
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),  # 64x224x224 → 64x224x224
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 64x224x224 → 64x112x112
            # ---- Block 2 ----
            nn.Conv2d(64, 128, kernel_size=3, padding=1),  # 64x112x112  → 128x112x112
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),  # 128x112x112 → 128x112x112
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 128x112x112 → 128x56x56
            # ---- Block 3 ----
            nn.Conv2d(128, 256, kernel_size=3, padding=1),  # 128x56x56 → 256x56x56
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),  # 256x56x56 → 256x56x56
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),  # 256x56x56 → 256x56x56
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 256x56x56 → 256x28x28
            # ---- Block 4 ----
            nn.Conv2d(256, 512, kernel_size=3, padding=1),  # 256x28x28 → 512x28x28
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),  # 512x28x28 → 512x28x28
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),  # 512x28x28 → 512x28x28
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 512x28x28 → 512x14x14
            # ---- Block 5 ----
            nn.Conv2d(512, 512, kernel_size=3, padding=1),  # 512x14x14 → 512x14x14
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),  # 512x14x14 → 512x14x14
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),  # 512x14x14 → 512x14x14
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 512x14x14 → 512x7x7
        )

        # 全连接分类部分：3 个全连接层
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes),  # 输出 10 类 0~9
        )

        self.early_stop = EarlyStopping(patience=2)

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)  # 512x7x7 → 25088
        x = self.classifier(x)
        return x

    def use(self, img):
        with torch.no_grad():
            out = self(img.unsqueeze(0))
            return out.argmax().item()



model = VGG16()
model.load_state_dict(torch.load('./pth/vgg16_epoch8.pth', map_location=torch.device('cpu'), weights_only=True))
model.eval()
img, label = test_data[1001]
print('True label:', label)
print('Use output:', model.use(img))
print('Model output:', model(img.unsqueeze(0)).argmax().item())


