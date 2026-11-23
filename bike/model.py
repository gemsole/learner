import torch.nn as nn


# ---------------------- GRU 模型 ----------------------
# 相比原始单层 RNN：使用 GRU（缓解梯度消失）+ 两层堆叠 + Dropout + LayerNorm
class BikeRNN(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super().__init__()
        self.rnn = nn.GRU(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.rnn(x)
        return self.fc(out)
