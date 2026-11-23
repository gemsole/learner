import numpy as np
import torch


# 预测评估
def test(model, X_test, y_test, criterion):
    model.eval()
    with torch.no_grad():
        test_pred = model(X_test)
        test_loss = criterion(test_pred, y_test)
    return test_pred, test_loss
