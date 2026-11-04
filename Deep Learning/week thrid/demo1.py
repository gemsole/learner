import torch

logits = torch.tensor([2.5, 0.3, -0.1])
test = torch.tensor([[3.3, 2.2, 1.1], [4.4, 5.5, 64.4]])
softmax = torch.nn.Softmax(dim=1)
probs = softmax(test)
print(probs)