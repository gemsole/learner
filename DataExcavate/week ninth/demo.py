import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split


# 1. 数据清洗与特征工程
def load_and_preprocess(data_path='ml-100k/'):
    print("开始加载和处理数据...")
    # 1.1 读取评分数据
    data_df = pd.read_csv(data_path + 'u.data', sep='\t', header=None)
    data_df.columns = ['user_id', 'item_id', 'label', 'timestamp']

    # 评分标签转换为二元标签：评分 > 3 记为1，否则为0
    threshold = 3
    data_df['label'] = (data_df['label'] > threshold).astype(int)

    # 时间戳归一化
    mms = MinMaxScaler()
    data_df['timestamp'] = mms.fit_transform(data_df['timestamp'].values.reshape(-1, 1))

    # 1.2 读取用户数据
    user_df = pd.read_csv(data_path + 'u.user', sep='|', header=None)
    user_df.columns = ['user_id', 'age', 'gender', 'occupation', 'zip_code']
    # 删除邮编 邮编通常噪声较大，对推荐任务帮助有限
    user_df.drop(columns=['zip_code'], inplace=True)

    # 1.3 读取电影数据
    item_df = pd.read_csv(data_path + 'u.item', sep='|', header=None, encoding='latin-1')

    # 提取流派(genre)数据
    seq_len = item_df[range(5, 24)].sum(axis=1).max()

    def convert_genre(x):
        genre = list(np.where(x.iloc[5:].values)[0])
        genre.extend([0] * (seq_len - len(genre)))
        return genre

    item_df['genre'] = item_df.apply(convert_genre, axis=1)
    item_df.drop(columns=[1, *range(3, 24)], inplace=True)
    item_df.columns = ['item_id', 'release_year', 'genre']

    # 提取上映年份
    fill_na = item_df['release_year'].mode()[0][-4:]
    item_df['release_year'] = item_df['release_year'].apply(
        lambda x: x[-4:] if pd.notnull(x) else fill_na
    ).astype(int)

    # 1.4 合并数据
    df = data_df.merge(user_df, on='user_id', how='left').merge(item_df, on='item_id', how='left')
    df = df.sort_values(by=['user_id', 'timestamp'], ascending=[1, 1]).reset_index(drop=True)

    # 1.5 类别特征编码 (Label Encoding)
    token_col = ['user_id', 'item_id', 'age', 'gender', 'occupation', 'release_year']
    mappings = {}
    for i in token_col:
        le = LabelEncoder()
        le.fit(df[i])
        mappings[i] = dict(zip(le.transform(le.classes_), le.classes_))
        df[i] = le.transform(df[i])

    print(f"数据处理完成，共 {len(df)} 条记录。")
    return df, token_col, mappings



# 2. 定义数据集类
class MovieLens_100K_Dataset(Dataset):
    def __init__(self, df, token_col, global_field_dims):
        self.df = df[token_col].values
        # 使用外部传入的全局特征维度，避免各个子集维度不一致
        self.field_dims = global_field_dims
        self.labels = df['label'].values

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.df[idx], self.labels[idx]


# 3. 定义回归模型类
class LogisticRegressionModel(nn.Module):
    def __init__(self, field_dims, output_dim=1):
        super().__init__()
        self.fc = nn.Embedding(sum(field_dims), output_dim)
        self.bias = nn.Parameter(torch.zeros((output_dim,)))
        self.offsets = np.array((0, *np.cumsum(field_dims)[:-1]), dtype=np.int32)
        torch.nn.init.xavier_uniform_(self.fc.weight.data)

    def forward(self, x):
        x = x + x.new_tensor(self.offsets).unsqueeze(0)
        linear_output = torch.sum(self.fc(x), dim=1) + self.bias
        return torch.sigmoid(linear_output).squeeze(1)


# 4. 训练和验证函数
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



# 5. 最终的用户推荐函数 (Inference)
def recommend_for_user(encoded_user_id, model, df, token_col, top_k=10):
    """
    给指定用户推荐电影。
    注意：这里的 encoded_user_id 是经过 LabelEncoder 编码后的 ID (0~942)。
    """
    model.eval()
    device = next(model.parameters()).device

    # 找出该用户历史看过的所有电影
    watched_items = df[df['user_id'] == encoded_user_id]['item_id'].unique()

    # 获取全库中该用户没看过的电影
    all_items = df['item_id'].unique()
    unwatched_items = np.setdiff1d(all_items, watched_items)

    # 获取该用户的画像信息
    user_info = df[df['user_id'] == encoded_user_id].iloc[0][['age', 'gender', 'occupation']]

    # 构造待预测的特征矩阵 [user_id, item_id, age, gender, occupation, release_year]
    release_year_mode = int(df['release_year'].mode()[0])

    input_data = []
    for item_id in unwatched_items:
        record = [encoded_user_id, item_id, user_info['age'], user_info['gender'], user_info['occupation'],
                  release_year_mode]
        input_data.append(record)

    input_tensor = torch.tensor(input_data, dtype=torch.long).to(device)

    # 预测得分
    with torch.no_grad():
        scores = model(input_tensor).cpu().numpy()

    # 排序并取出 Top-K
    top_indices = np.argsort(scores)[::-1][:top_k]
    top_item_ids = unwatched_items[top_indices]
    top_scores = scores[top_indices]

    print(f"\n 为用户 (Encoded ID: {encoded_user_id}) 推荐的 Top-{top_k} 部电影:")
    for i, (item_id, score) in enumerate(zip(top_item_ids, top_scores)):
        print(f"  排名 {i + 1}: 电影ID {item_id}, 预测得分 {score:.4f}")

    return top_item_ids



# 6. 主函数：整合训练、测试与推荐
def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    if device.type == 'cuda':
        print(f"GPU 型号: {torch.cuda.get_device_name(0)}")

    # 1. 加载全量数据
    df, token_col, mappings = load_and_preprocess(data_path='ml-100k/')  # 请根据实际路径修改

    # 关键修复：基于全量数据计算全局唯一的 field_dims
    global_field_dims = df[token_col].nunique().values
    print(f"全局特征维度: {global_field_dims}")

    # 2. 划分数据集 (70% 训练, 15% 验证, 15% 测试)
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

    # 传入 global_field_dims
    train_dataset = MovieLens_100K_Dataset(train_df, token_col, global_field_dims)
    val_dataset = MovieLens_100K_Dataset(val_df, token_col, global_field_dims)
    test_dataset = MovieLens_100K_Dataset(test_df, token_col, global_field_dims)

    test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False, pin_memory=True)

    # 3. 初始化模型
    criterion = nn.BCELoss()



    # 步骤二：在独立的测试集上进行最终评估
    print("\n" + "=" * 50)
    print("加载表现最好的模型，在测试集上进行最终评估...")
    best_model = LogisticRegressionModel(global_field_dims).to(device)
    # 增加 weights_only=True 消除 FutureWarning
    best_model.load_state_dict(torch.load('./week ninth/best_model.pth', map_location=device, weights_only=True))

    test_loss, test_auc = validate_model(best_model, test_loader, criterion, device)
    print(f"最终测试集 Loss: {test_loss:.4f}")
    print(f"最终测试集 AUC: {test_auc:.4f}")
    print("=" * 50)

    # 步骤三：给特定用户生成推荐
    # 原始数据集用户ID是 1~943，LabelEncoder后变成 0~942。
    # 这里传入 0，代表原始用户ID为 1 的用户
    sample_encoded_user_id = 0
    recommend_for_user(sample_encoded_user_id, best_model, df, token_col, top_k=10)


if __name__ == '__main__':
    main()