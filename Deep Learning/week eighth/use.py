import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import datasets
from torch.utils.data import DataLoader

transform = transforms.Compose(
    [
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.209108]
        ),
    ]
)

data = datasets.CIFAR10(root="./data", train=False, download=False, transform=transform)
print(data.class_to_idx)
print(data.classes)
"""
test_loader = DataLoader(data, batch_size=64, shuffle=False)



class alexnet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 96, kernel_size=11, stride=4, padding=2)
        self.conv2 = nn.Conv2d(96, 256, kernel_size=5, padding=2)
        self.conv3 = nn.Conv2d(256, 384, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(384, 384, kernel_size=3, padding=1)
        self.conv5 = nn.Conv2d(384, 256, kernel_size=3, padding=1)

        self.pool = nn.MaxPool2d(kernel_size=3, stride=2)

        self.flatten = nn.Flatten()

        self.dropout = nn.Dropout(0.5)

        self.fc1 = nn.Linear(9216, 4096)
        self.fc2 = nn.Linear(4096, 4096)
        self.fc3 = nn.Linear(4096, 10)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = torch.relu(self.conv3(x))
        x = torch.relu(self.conv4(x))
        x = self.pool(torch.relu(self.conv5(x)))
        x = self.flatten(x)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x


model = alexnet()
model.load_state_dict(torch.load("./pth/alexnet_epoch28.pth"))
model.eval()


img, label = next(iter(test_loader))
print(img.shape, label.shape, sep="-----")
img, label = img[3], label[3]
print(img.shape, label.shape, sep="-----")
with torch.no_grad():
    out = model(img.unsqueeze(0))
print("预测类别:", out.argmax().item())
print("真实类别:", label.item())
"""