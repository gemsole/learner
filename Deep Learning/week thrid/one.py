import torch

logits = torch.tensor([2.5, 0.3, -0.1])
probs = torch.nn.functional.softmax(logits, dim=0)
print(probs)
pred = probs.argmax()
print(pred)