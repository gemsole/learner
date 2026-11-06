from torch import nn

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),   # 224x224 → 64x55x55
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),                   # 64x55x55 → 64x27x27
            nn.Conv2d(64, 192, kernel_size=5, padding=2),            # 64x27x27 → 192x27x27
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),                   # 192x27x27 → 192x13x13
        )