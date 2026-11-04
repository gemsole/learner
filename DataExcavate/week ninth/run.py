import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.metrics import roc_auc_score



# 1. 数据清洗
def load_and_preprocess(data_path='ml-100k/'):
    # 1.1 读取评分数据 u.data
    data_csv = data_path + 'u.data'
    data_df = pd.read_csv(data_csv, sep='\t', header=None)
    data_df.columns = ['user_id', 'item_id', 'label', 'timestamp']

    # 评分标签转换为二元标签：评分 > 3 记为1，否则为0
    threshold = 3
    data_df['label'] = (data_df['label'] > threshold).astype(int)

    # 时间戳归一化
    mms = MinMaxScaler()
    data_df['timestamp'] = mms.fit_transform(data_df['timestamp'].values.reshape(-1, 1))

    # 1.2 读取用户数据 u.user
    user_csv = data_path + 'u.user'
    user_df = pd.read_csv(user_csv, sep='|', header=None)
    user_df.columns = ['user_id', 'age', 'gender', 'occupation', 'zip_code']
    user_df.drop(columns=['zip_code'], inplace=True)

    # 1.3 读取电影数据 u.item
    item_csv = data_path + 'u.item'
    item_df = pd.read_csv(item_csv, sep='|', header=None, encoding='latin-1')

    # 提取流派(genre)数据生成新列
    seq_len = item_df[range(5, 24)].sum(axis=1).max()

    def convert_genre(x):
        genre = list(np.where(x.iloc[5:].values)[0])
        genre.extend([0] * (seq_len - len(genre)))  # 补零对齐长度
        return genre

    item_df['genre'] = item_df.apply(convert_genre, axis=1)
    # 删除不必要的电影属性列，只保留 movie id, release date, genre
    item_df.drop(columns=[1, *range(3, 24)], inplace=True)
    item_df.columns = ['item_id', 'release_year', 'genre']

    # 提取上映年份
    fill_na = item_df['release_year'].mode()[0][-4:]
    item_df['release_year'] = item_df['release_year'].apply(
        lambda x: x[-4:] if pd.notnull(x) else fill_na
    ).astype(int)

    # 1.4 合并数据 (Merge)
    df = data_df.merge(user_df, on='user_id', how='left').merge(item_df, on='item_id', how='left')
    # 按用户和时间排序
    df = df.sort_values(by=['user_id', 'timestamp'], ascending=[1, 1]).reset_index(drop=True)

    # 1.5 类别特征编码 (Label Encoding)
    token_col = ['user_id', 'item_id', 'age', 'gender', 'occupation', 'release_year']
    mappings = {}
    for i in token_col:
        le = LabelEncoder()
        le.fit(df[i])
        mappings[i] = dict(zip(le.transform(le.classes_), le.classes_))
        df[i] = le.transform(df[i])

    return df, token_col



# 2. 定义 MovieLens 100K 数据集类
class MovieLens_100K_Dataset(Dataset):
    def __init__(self, df, token_col):
        self.df = df[token_col].values
        self.field_dims = df[token_col].nunique().values
        self.labels = df['label'].values

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.df[idx], self.labels[idx]



# 3. 定义回归模型类
class LogisticRegressionModel(nn.Module):
    def __init__(self, field_dims, output_dim=1):
        super().__init__()
        # 使用Embedding层表示特征的线性部分
        self.fc = nn.Embedding(sum(field_dims), output_dim)
        self.bias = nn.Parameter(torch.zeros((output_dim,)))

        # 计算特征域的偏移量 offsets
        self.offsets = np.array((0, *np.cumsum(field_dims)[:-1]))

        # 初始化权重
        torch.nn.init.xavier_uniform_(self.fc.weight.data)

    def forward(self, x):
        # 将特征编码后的索引转换为在整个特征向量中的位置
        x = x + x.new_tensor(self.offsets).unsqueeze(0)
        # 查表求和 + 偏置
        linear_output = torch.sum(self.fc(x), dim=1) + self.bias
        # 使用sigmoid激活函数输出概率值
        return torch.sigmoid(linear_output).squeeze(1)



# 4. 训练、验证模型函数
def train_epoch(model, data_loader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    for x, y in data_loader:
        x, y = x.to(device), y.to(device)
        y_pred = model(x)
        y = y.to(torch.float32)

        loss = criterion(y_pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * x.size(0)
    return total_loss / len(data_loader.dataset)


def validate_model(model, data_loader, criterion, device):
    model.eval()
    total_loss = 0
    targets, predictions = [], []
    with torch.no_grad():
        for x, y in data_loader:
            x, y = x.to(device), y.to(device)
            y_pred = model(x)
            y = y.to(torch.float32)

            loss = criterion(y_pred, y)
            total_loss += loss.item() * x.size(0)
            targets.extend(y.tolist())
            predictions.extend(y_pred.tolist())

    auc = roc_auc_score(targets, predictions)
    return total_loss / len(data_loader.dataset), auc



# 5. 主函数：训练和验证循环
def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # 加载并处理数据
    df, token_col = load_and_preprocess(data_path='ml-100k/')  # 根据自己的100k数据集位置修改对应的位置

    # 划分训练集和验证集 (按8:2划分)
    train_df = df.sample(frac=0.8, random_state=42)
    val_df = df.drop(train_df.index)

    train_dataset = MovieLens_100K_Dataset(train_df, token_col)
    val_dataset = MovieLens_100K_Dataset(val_df, token_col)

    train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=256, shuffle=False)

    # 初始化模型、损失函数和优化器
    field_dims = train_dataset.field_dims
    model = LogisticRegressionModel(field_dims).to(device)
    criterion = nn.BCELoss()  # 二分类交叉熵损失
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 训练参数
    num_epochs = 50
    kill_cnt = 0
    best_valid_auc = 0.0

    for epoch in range(num_epochs):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_auc = validate_model(model, val_loader, criterion, device)

        # 早停机制 (Early Stopping)
        if val_auc > best_valid_auc:
            best_valid_auc = val_auc
            kill_cnt = 0
        else:
            kill_cnt += 1
            if kill_cnt > 5:
                print("Early Stopping!!")
                break

        print(
            f'Epoch {epoch + 1}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, Val AUC: {val_auc:.4f}, Patience: {kill_cnt:d}')


if __name__ == '__main__':
    main()