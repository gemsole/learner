import numpy as np

def calc_item_cosine_similarity(item_vec1, item_vec2):
    """
    计算两个物品评分向量之间的余弦相似度
    物品向量：列向量，保存所有用户对该物品的评分，0代表用户未对该物品评分
    计算规则：只选取【同时对两个物品都有评分】的用户数据，未评分用户不参与相似度计算

    参数：
        item_vec1: np.array，物品1的全部用户评分向量（一维）
        item_vec2: np.array，物品2的全部用户评分向量（一维）
    返回：
        float: 余弦相似度，范围[-1,1]，越大代表两个物品越相似；无共同评分用户返回0.0
    """
    # 掩码mask：筛选出同时给物品1、物品2打分的用户位置（两个评分都不等于0）
    mask = (item_vec1 != 0) & (item_vec2 != 0)

    # np.sum(mask)统计共同评分用户数量，如果没有共同评分用户，相似度直接返回0
    if np.sum(mask) == 0:
        return 0.0

    # 根据掩码，提取共同评分用户对这两个物品的评分
    v1 = item_vec1[mask]
    v2 = item_vec2[mask]

    # 余弦相似度公式：向量点积 / (向量1模长 * 向量2模长)
    dot_product = np.dot(v1, v2)          # 向量点积
    norm_v1 = np.linalg.norm(v1)          # v1的L2范数（模长）
    norm_v2 = np.linalg.norm(v2)          # v2的L2范数（模长）
    cos_sim = dot_product / (norm_v1 * norm_v2)

    return cos_sim


def item_cf_recommend(target_user_id, user_item_rating_matrix, item_name_list):
    """
    基于物品的协同过滤推荐算法
    物品之间计算相似度；找到与用户历史喜欢物品相似的物品进行推荐
    用户未评分物品的预测分数 = 用户已评分物品的评分 × 物品相似度 加权平均

    参数：
        target_user_id: int，待推荐的目标用户编号
        user_item_rating_matrix: np.array，用户-物品评分矩阵
                                 矩阵形状：[用户数量, 物品数量]
                                 行：每一行代表一个用户；列：每一列代表一个物品
                                 值：>0代表用户评分；0代表用户没有对该物品评分
        item_name_list: list，物品名称列表，下标和矩阵列下标一一对应
    返回：
        list: 推荐结果列表，元素为元组 (物品名称, 预测评分)，按预测分数降序排列
    """
    # 获取矩阵维度：user_num 用户总数；item_num 物品总数
    user_num, item_num = user_item_rating_matrix.shape

    # 构建物品-物品相似度矩阵
    # 初始化物品相似度矩阵，维度：物品数 × 物品数，初始值全部为0
    # item_similarity_matrix[i][j] 代表：物品i 和 物品j 的相似度
    item_similarity_matrix = np.zeros((item_num, item_num))

    # 双重循环遍历所有物品两两组合，计算相似度
    for i in range(item_num):
        # 取出第i个物品的全部用户评分：矩阵第i列，即所有用户对物品i的评分
        item_i_vec = user_item_rating_matrix[:, i]
        for j in range(item_num):
            # 取出第j个物品的全部用户评分：矩阵第j列
            item_j_vec = user_item_rating_matrix[:, j]
            # 计算物品i与物品j余弦相似度，存入相似度矩阵
            item_similarity_matrix[i, j] = calc_item_cosine_similarity(item_i_vec, item_j_vec)

    # 获取目标用户已经评分过的物品
    # 取出目标用户的整行评分数据：该用户对所有物品的评分
    target_user_rating = user_item_rating_matrix[target_user_id]

    # np.where(target_user_rating > 0)[0]：找到评分大于0的下标，即用户已经评分物品的ID
    rated_item_idx = np.where(target_user_rating > 0)[0]
    print(f"\n目标用户{target_user_id}已评分物品ID：{rated_item_idx}")

    # 逐个预测目标用户未评分物品的评分
    # 初始化预测分数数组，保存每一个物品的预测评分，初始全部为0
    item_pred_score = np.zeros(item_num)

    # 遍历每一个物品，逐个计算预测分
    for item_pred_idx in range(item_num):
        # 如果目标用户已经对这个物品评过分，跳过，不需要推荐已经看过的物品
        if target_user_rating[item_pred_idx] > 0:
            continue

        score_sum = 0.0   # 分子：评分 * 物品相似度 的累加和
        weight_sum = 0.0  # 分母：相似度权重累加和

        # 遍历目标用户所有【已经评分过】的物品
        for rated_i in rated_item_idx:
            # 获取：已评分物品rated_i 和待预测物品item_pred_idx 的相似度
            sim = item_similarity_matrix[rated_i, item_pred_idx]
            # 相似度<=0，无正向参考价值，跳过
            if sim <= 0:
                continue
            # 获取目标用户对物品rated_i 的真实评分
            rating = target_user_rating[rated_i]
            # 加权累加：评分 × 相似度
            score_sum += rating * sim
            # 权重累加
            weight_sum += sim

        # 分母大于0，代表有有效相似物品参与计算，计算加权平均分作为预测分
        if weight_sum > 0:
            item_pred_score[item_pred_idx] = score_sum / weight_sum

    # 对预测分数排序，生成推荐列表
    # argsort：从小到大排序，返回物品下标；[::-1]反转，变成从大到小
    sorted_item_idx = np.argsort(item_pred_score)[::-1]

    # 构建推荐列表：只保留预测分数>0的物品，格式(物品名称,预测分数)
    rec_result = [(item_name_list[i], item_pred_score[i])
                  for i in sorted_item_idx if item_pred_score[i] > 0]

    return rec_result


if __name__ == "__main__":
    """程序入口，测试代码"""
    # 用户-物品评分矩阵
    # 行：用户0~用户4；列：电影A、电影B、电影C、电影D、电影E
    # 数字>0是用户评分，0代表用户没有看过该电影，没有评分
    user_item_rating_matrix = np.array([
        [5, 3, 0, 1, 0],  # 用户0：A=5分，B=3分，D=1分；C、E未评分（待推荐）
        [4, 0, 0, 1, 2],  # 用户1：A=4分，D=1分，E=2分；B、C未评分
        [1, 1, 0, 5, 4],  # 用户2：A=1分，B=1分，D=5分，E=4分；C未评分
        [1, 0, 5, 4, 0],  # 用户3：A=1分，C=5分，D=4分；B、E未评分
        [0, 2, 4, 0, 5],  # 用户4：B=2分，C=4分，E=5分；A、D未评分
    ])
    # 物品名称列表，下标和矩阵列一一对应
    item_name_list = ["电影A", "电影B", "电影C", "电影D", "电影E"]

    # 设置要推荐的目标用户编号
    target_user_id = 0
    # 调用ItemCF推荐函数
    rec_list = item_cf_recommend(target_user_id, user_item_rating_matrix, item_name_list)

    # 输出推荐结果
    print(f"\n===== ItemCF 用户{target_user_id}推荐结果 =====")
    for item_name, pred_score in rec_list:
        print(f"{item_name}，预测评分：{pred_score:.2f}")


#