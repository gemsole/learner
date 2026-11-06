import torch
import torch.nn.functional as F

a = torch.tensor([5., 2., 3.])
print(a)
b = F.softmax(a)
print(b)
print(b.argmax())
