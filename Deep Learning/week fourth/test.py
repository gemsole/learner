import torch
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
import torch.nn.functional as F


train_dataset = datasets.MNIST(
    root="./data", train=True, download=True, transform=transforms.ToTensor()
)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

test_dataset = datasets.MNIST(
    root="./data", train=False, download=True, transform=transforms.ToTensor()
)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)


model = torch.nn.Sequential(
    torch.nn.Linear(784, 128), torch.nn.ReLU(), torch.nn.Linear(128, 10)
)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)


def forward(x):
    return model(x)


def loss_fn(y, y_pred):
    return F.cross_entropy(y_pred, y)


def accuracy(y, y_pred):
    return (y_pred == y).float().mean()


def plot_loss_acc(train_loss, train_acc, test_loss, test_acc):
    plt.figure(figsize=(12, 8))
    plt.subplot(1, 2, 1)
    plt.plot(train_loss, label="Train Loss")
    plt.plot(test_loss, label="Test Loss")
    plt.title("Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Value")
    plt.legend()
    plt.show()

    plt.subplot(1, 2, 2)
    plt.plot(train_acc, label="Train Acc")
    plt.plot(test_acc, label="Test Acc")
    plt.title("Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Value")
    plt.legend()
    plt.show()


def plot_predictions(model, test_loader):
    model.eval()
    with torch.no_grad():
        for i, (inputs, labels) in enumerate(test_loader):
            outputs = forward(inputs.view(-1, 784))
            _, predicted = torch.max(outputs, dim=1)
            plt.subplot(3, 4, i + 1)
            plt.tight_layout()
            plt.imshow(
                inputs[i].numpy().reshape(28, 28), cmap="gray", interpolation="none"
            )
            plt.title(f"Pred: {predicted.item()}")


def test_model(model, test_loader):
    test_loss, test_acc = test(model, test_loader)
    print(f"Test Loss: {test_loss:.4f}, " f"Test Acc: {test_acc:.4f}")
    return test_acc


def backward(loss, optimizer):
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()


def train(model, train_loader, optimizer, epoch):
    model.train()
    running_loss = 0.0
    running_acc = 0.0
    for inputs, labels in train_loader:
        outputs = forward(inputs.view(-1, 784))
        loss = loss_fn(labels, outputs)
        running_loss += loss.item()
        running_acc += accuracy(labels, torch.argmax(outputs, dim=1))
        backward(loss, optimizer)
    return running_loss / len(train_loader), running_acc / len(train_loader)


def test(model, test_loader):
    model.eval()
    running_loss = 0.0
    running_acc = 0.0
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = forward(inputs.view(-1, 784))
            loss = loss_fn(labels, outputs)
            running_acc += accuracy(labels, torch.argmax(outputs, dim=1))
        return running_loss / len(test_loader), running_acc / len(test_loader)


def main():
    for epoch in range(10):
        train_loss, train_acc = train(model, train_loader, optimizer, epoch)
        test_loss, test_acc = test(model, test_loader)
        print(
            f"Epoch [{epoch+1}/{10}], "
            f"Train Loss: {train_loss:.4f}, "
            f"Train Acc: {train_acc:.4f}, "
            f"Test Loss: {test_loss:.4f}, "
            f"Test Acc: {test_acc:.4f}"
        )
    test_acc = test_model(model, test_loader)
    plot_loss_acc(train_loss, train_acc, test_loss, test_acc)
    plot_predictions(model, test_loader)
    plt.show()


if __name__ == "__main__":
    main()
