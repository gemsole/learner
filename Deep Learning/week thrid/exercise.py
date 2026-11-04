import torch

x = torch.tensor([2., 3.], requires_grad=True)
w = torch.tensor([0.5, 1.], requires_grad=True)
b = torch.tensor(0)
y = torch.tensor(5)
lr = torch.tensor(0.01)

# 1、x 和 w 都属于向量

model = lambda x: torch.dot(x, w)
pred = model(x)
loss = (pred - y) ** 2
print(loss) #  2、loss值为1

for epoch in range(100):
    print(epoch)
    loss.backward()
    with torch.no_grad():

        w -= lr * w.grad
        w.grad.zero_()
        pred = model(x)
        loss = (pred - y) ** 2


# print(model(x))