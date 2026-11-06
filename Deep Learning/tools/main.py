import tomllib
import torch


config = tomllib.load(open("tools/config.toml", "rb"))


def log(file, msg):
    with open(file, "a") as f:
        f.write(msg + "\n")


def train(model, train_loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    for img, label in train_loader:
        img, label = img.to(device, non_blocking=config["non_blocking"]), label.to(
            device, non_blocking=config["non_blocking"]
        )
        optimizer.zero_grad()
        out = model(img)
        loss = criterion(out, label)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(train_loader)


def test(model, test_loader, test_data, device):
    model.eval()
    correct = 0
    with torch.no_grad():
        for img, label in test_loader:
            img, label = img.to(device, non_blocking=config["non_blocking"]), label.to(
                device, non_blocking=config["non_blocking"]
            )
            out = model(img)
            pred = torch.argmax(out, dim=1)
            correct += (pred == label).sum().item()
    acc = correct / len(test_data)
    return acc
