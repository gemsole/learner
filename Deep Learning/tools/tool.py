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
    def __init__(self, config, model, device = "cuda"):
        with open(config, "rb") as f:
            self.config = tomli.load(f)
        self.data_root = PROJECT_ROOT / self.config["data"]
        self.log_path = PROJECT_ROOT / self.config["log"]
        self.model = model
        self.device = device
        self.model.to(self.device)

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config["lr"])
        self.train_data = None
        self.test_data = None
        self.train_loader = None
        self.test_loader = None

    def log(self, msg):
        with open(self.log_path, "a") as f:
            f.write(msg + "\n")

    def load(self):
        """
        加载数据集并返回数据加载器\n
        train_loader, test_loader, train_data, test_data
        """
        transform = transforms.Compose(
            [
                transforms.Resize(self.config["resize"]),
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.209108)
                ),
            ]
        )

        num_workers = self.config["num_workers"]
        pin_memory = self.config["pin_memory"]
        # persistent_workers 仅在 num_workers > 0 时有效
        persistent_workers = self.config["persistent_workers"] and num_workers > 0

        self.train_data = datasets.CIFAR10(
            root=self.data_root,
            train=True,
            download=self.config["download"],
            transform=transform,
        )
        self.test_data = datasets.CIFAR10(
            root=self.data_root,
            train=False,
            download=self.config["download"],
            transform=transform,
        )
        self.train_loader = DataLoader(
            self.train_data,
            batch_size=self.config["batch_size"],
            shuffle=self.config["shuffle"],
            pin_memory=pin_memory,
            num_workers=num_workers,
            persistent_workers=persistent_workers,
        )
        self.test_loader = DataLoader(
            self.test_data,
            batch_size=self.config["batch_size"],
            shuffle=False,
            pin_memory=pin_memory,
            num_workers=num_workers,
            persistent_workers=persistent_workers,
        )
        print("data loaded")
        return self.train_loader, self.test_loader, self.train_data, self.test_data

    def train(self):
        """
        训练模型
        return: 训练损失
        """
        self.model.train()
        total_loss = 0
        non_blocking = self.config["non_blocking"]
        device = self.device
        optimizer = self.optimizer
        model = self.model
        train_loader = self.train_loader
        criterion = self.criterion
        for img, label in train_loader:
            img, label = img.to(
                device, non_blocking=non_blocking
            ), label.to(device, non_blocking=non_blocking)
            optimizer.zero_grad(set_to_none=True)
            out = model(img)
            loss = criterion(out, label)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        return total_loss / len(self.train_loader)

    def test(self):
        """
        测试模型
        return: 测试准确率
        """
        self.model.eval()
        correct = 0
        non_blocking = self.config["non_blocking"]
        device = self.device
        model = self.model
        test_loader = self.test_loader
        with torch.no_grad():
            for img, label in test_loader:
                img, label = img.to(
                    device, non_blocking=non_blocking
                ), label.to(device, non_blocking=non_blocking)
                out = model(img)
                pred = torch.argmax(out, dim=1)
                correct += (pred == label).sum().item()
        return correct / len(self.test_data)

    @staticmethod
    def save(state_dict, path = "model.pth"):
        """
        保存模型状态字典到指定路径\n
        path: 模型状态字典保存路径
        """
        torch.save(state_dict, path)
