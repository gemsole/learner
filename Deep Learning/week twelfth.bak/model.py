"""
模型定义模块
============
封装共享单车租赁量预测使用的循环神经网络。
支持 RNN / LSTM 两种实现，统一接口: forward(x) -> 预测值。
"""

import torch.nn as nn


class BikeRNN(nn.Module):
    """
    课程参考结构:
      RNN(input_size, hidden_size, num_layers, batch_first=True)
        -> 取最后时间步 -> Linear(hidden_size, 1)

    Args:
        input_size   : 每个时间步的输入特征数 (单变量=1)
        hidden_size  : RNN 隐藏层维度
        num_layers   : RNN 层数
        nonlinearity : 'tanh' 或 'relu'
    """

    def __init__(self, input_size=1, hidden_size=32, num_layers=3, nonlinearity="tanh"):
        super().__init__()
        self.rnn = nn.RNN(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            nonlinearity=nonlinearity,
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        outputs, _ = self.rnn(x)  # (batch, seq_len, hidden_size)
        output = outputs[:, -1, :]  # 取最后时间步  (batch, hidden_size)
        out = self.fc(output)  # (batch, 1)
        return out
