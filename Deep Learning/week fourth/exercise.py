import torch
from torch.optim import SGD

x = torch.tensor([2.0])
w = torch.tensor([0.1], requires_grad=True)
b = torch.tensor([0.1], requires_grad=True)
y = torch.tensor([3.0])
ir = torch.tensor(0.01)
optimizer = SGD([w, b], lr=ir.item())

for epoch in range(1, 101):
    pred = w * x + b
    loss = (pred - y) ** 2
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
    # with torch.no_grad():
    #     w -= ir * w.grad
    #     b -= ir * b.grad
    # w.grad.zero_()
    # b.grad.zero_()

    if epoch % 20 == 0:
        print(f'epoch:{epoch},pred:{pred.item():.2f}, w:{w.item():.2f}, b:{b.item():.2f}, loss:{loss.item():.2f}')
