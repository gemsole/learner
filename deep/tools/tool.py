import tomli
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import torch.nn as nn
import torch.optim as optim

# 项目根目录，用于将配置中的相对路径统一解析
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Tools:
    def __init__(self, config, model, device):
        with open(config, "rb") as f:
            self.config = tomli.load(f)
        self.data_root = PROJECT_ROOT / self.config["data"]
        self.log_path = PROJECT_ROOT / self.config["log"]
        self.model = model
        self.device = device
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config["lr"])

    def log(self, msg):
        with open(self.log_path, "a") as f:
            f.write(msg + "\n")

    def load(self):
        """
        加载数据集并返回数据加载器
        train_loader, test_loader, test_data
        """
        transform = transforms.Compose(
            [
                transforms.Resize(self.config["resize"]),
                transforms.ToTensor(),
                transforms.Normalize(
                    tuple(self.config["mean"]), tuple(self.config["std"])
                ),
            ]
        )

        batch_size = self.config["batch_size"]
        num_workers = self.config["num_workers"]
        pin_memory = self.config["pin_memory"]
        # persistent_workers 仅在 num_workers > 0 时有效
        persistent_workers = self.config["persistent_workers"] and num_workers > 0

        train_data = datasets.CIFAR10(
            root=self.data_root,
            train=True,
            download=self.config["download"],
            transform=transform,
        )
        test_data = datasets.CIFAR10(
            root=self.data_root,
            train=False,
            download=self.config["download"],
            transform=transform,
        )
        train_loader = DataLoader(
            train_data,
            batch_size=batch_size,
            shuffle=self.config["shuffle"],
            pin_memory=pin_memory,
            num_workers=num_workers,
            persistent_workers=persistent_workers,
        )
        test_loader = DataLoader(
            test_data,
            batch_size=batch_size,
            shuffle=False,
            pin_memory=pin_memory,
            num_workers=num_workers,
            persistent_workers=persistent_workers,
        )
        print('data loaded')
        return train_loader, test_loader, test_data

    def train(self, train_loader):
        """
        训练模型
        return: 训练损失
        """
        self.model.train()
        total_loss = 0
        for img, label in train_loader:
            img, label = img.to(
                self.device, non_blocking=self.config["non_blocking"]
            ), label.to(self.device, non_blocking=self.config["non_blocking"])
            self.optimizer.zero_grad()
            out = self.model(img)
            loss = self.criterion(out, label)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        return total_loss / len(train_loader)

    def test(self, test_loader, test_data):
        """
        测试模型
        return: 测试准确率
        """
        self.model.eval()
        correct = 0
        with torch.no_grad():
            for img, label in test_loader:
                img, label = img.to(
                    self.device, non_blocking=self.config["non_blocking"]
                ), label.to(self.device, non_blocking=self.config["non_blocking"])
                out = self.model(img)
                pred = torch.argmax(out, dim=1)
                correct += (pred == label).sum().item()
        return correct / len(test_data)
   
    @staticmethod
    def save(state_dict, path):
        torch.save(state_dict, path)
