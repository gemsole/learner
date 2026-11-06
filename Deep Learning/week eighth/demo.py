import torch
from torch import nn
import torch.optim as optim
import torchvision
from torch.utils.data import DataLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = torchvision.transforms.Compose(
    [
        torchvision.transforms.Resize(224),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize(
            mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.209108]
        ),
    ]
)

train_data = torchvision.datasets.CIFAR10(
    root="./data", train=True, download=False, transform=transform
)
test_data = torchvision.datasets.CIFAR10(
    root="./data", train=False, download=False, transform=transform
)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=64, shuffle=False)


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
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.dropout(torch.relu(self.fc2(x)))
        x = self.fc3(x)
        return x


model = alexnet().to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)


def train():
    model.train()
    total_loss = 0
    with open("train.log", "w") as f:
        f.write(f"train altogether batch {len(train_loader)}\n")
    for i, (img, label) in enumerate(train_loader):
        with open("train.log", "a") as f:
            f.write(f"train batch {i}\n")
        img, label = img.to(device), label.to(device)
        optimizer.zero_grad()
        out = model(img)
        loss = criterion(out, label)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(train_loader)


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
    return acc


if __name__ == "__main__":
    for epoch in range(30):
        print(f"Epoch {epoch+1} start")
        train_loss = train()
        test_acc = test()
        print(
            f"Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Test Acc: {test_acc:.4f}"
        )
        with open("result.log", "a") as f:
            f.write(
                f"Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Test Acc: {test_acc:.4f}\n"
            )
        torch.save(model.state_dict(), f"alexnet_epoch{epoch+1}.pth")
