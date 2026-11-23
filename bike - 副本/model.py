import torch.nn as nn

# ---------------------- RNN 模型 ----------------------
class BikeRNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super().__init__()
        self.rnn = nn.RNN(
            input_size,
            hidden_size, 
            num_layers, 
            batch_first=True, 
            nonlinearity="tanh"
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.rnn(x)
        out = self.fc(out[:, -1, :])
        return out
