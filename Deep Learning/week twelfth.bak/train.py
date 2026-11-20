"""
训练模块
========
封装训练循环 + 早停 + 最佳权重恢复。
"""

import torch
import torch.nn as nn


def train_model(model, train_loader, device,
                epochs=500, lr=0.01, patience=60):
    """
    训练循环（带早停，自动恢复最佳权重）。

    Args:
        model       : PyTorch 模型
        train_loader: 训练集 DataLoader
        device      : torch.device
        epochs      : 最大训练轮数
        lr          : 学习率
        patience    : 早停耐心值（loss 连续多少轮不下降就停）

    Returns:
        model       : 加载了最佳权重的模型
        train_losses: 每轮训练损失列表
    """
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    best_loss = float('inf')
    best_state = None
    counter = 0
    train_losses = []

    print(f"\n开始训练 (max {epochs} epochs, patience={patience})...")

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        n_batches = 0

        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)

            pred = model(bx)
            loss = criterion(pred, by)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1

        avg_loss = epoch_loss / n_batches
        train_losses.append(avg_loss)

        # 早停检查 + 保存最佳权重
        if avg_loss < best_loss:
            best_loss = avg_loss
            counter = 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            counter += 1

        if (epoch + 1) % 50 == 0:
            print(f"  Epoch [{epoch+1}/{epochs}], Loss={avg_loss:.6f}, Best={best_loss:.6f}")

        if counter >= patience:
            print(f"  早停 @ Epoch {epoch+1} (Best Loss={best_loss:.6f})")
            break

    if best_state:
        model.load_state_dict(best_state)
    print("训练完成，已恢复最佳模型权重!")

    return model, train_losses
