import torch


# 预测评估
def test(model, X_test):
    model.eval()
    with torch.no_grad():
        test_pred = model(X_test)
    return test_pred
