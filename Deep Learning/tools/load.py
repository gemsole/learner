from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import tomllib

config = tomllib.load(open("tools/config.toml", "rb"))


def load():
    transform = transforms.Compose(
        [
            transforms.Resize(224),  # 28x28 → 224x224
            transforms.ToTensor(),  # 像素 0~255 → 0~1
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.209108)),
        ]
    )
    download = config["download"] == "True"
    pin_memory = config["pin_memory"] == "True"
    persistent_workers = config["persistent_workers"] == "True"

    train_data = datasets.CIFAR10(
        root=config["data_path"], train=True, transform=transform, download=download
    )
    test_data = datasets.CIFAR10(
        root=config["data_path"], train=False, transform=transform, download=download
    )

    train_loader = DataLoader(
        train_data,
        batch_size=config["size"],
        shuffle=True,
        num_workers=config["num_workers"],
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
        drop_last=True,
    )
    test_loader = DataLoader(
        test_data,
        batch_size=config["size"],
        shuffle=False,
        num_workers=config["num_workers"],
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
        drop_last=False,
    )
    return train_loader, test_loader, test_data
