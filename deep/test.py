from tools import *
from torchvision import models
model = models.resnet18(pretrained=False)
tools = Tools("config.toml", model)
train_loader, test_loader, train_data, test_data = tools.load()
print(len(train_loader))
print(len(test_loader))
print(len(train_data))
print(len(test_data))