import torch

x = torch.tensor(2., requires_grad=True)
y = torch.tensor(3., requires_grad=True)

f = 3 * x ** 2 + 2 * x * y + y ** 2
f.backward()
print(x.grad)
print(y.grad)
print(f.grad)