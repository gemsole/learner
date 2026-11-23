import torch
import torch.nn as nn


# 训练循环：小批量 + 随机打乱 + 梯度裁剪 + 可选学习率调度
def train(epochs, model, X_train, y_train, criterion, optimizer,
          batch_size=32, grad_clip=1.0, scheduler=None):
    n = len(X_train)
    history = []
    for epoch in range(epochs):
        model.train()
        perm = torch.randperm(n)
        total = 0.0
        for start in range(0, n, batch_size):
            idx = perm[start:start + batch_size]
            optimizer.zero_grad()
            loss = criterion(model(X_train[idx]), y_train[idx])
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()
            total += loss.item() * len(idx)
        if scheduler is not None:
            scheduler.step()

        avg_loss = total / n
        history.append(avg_loss)
        if epoch == 0 or (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.6f}")
    return history
