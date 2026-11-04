import numpy as np

def calc_cosine_similarity(vec1, vec2):
    """计算两个用户评分向量的余弦相似度，只使用共同评分项"""
    mask = (vec1 != 0) & (vec2 != 0)
    if np.sum(mask) == 0:
        return 0.0
    v1 = vec1[mask]
    v2 = vec2[mask]
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def user_cf_recommend(target_user_id, user_item_rating_matrix, item_name_list, top_k=2):
    """
    基于用户的协同过滤推荐
    :param target_user_id: 待推荐用户编号
    :param user_item_rating_matrix: 用户-物品评分矩阵
    :param item_name_list: 物品名称列表
    :param top_k: 选取topK相似用户
    :return: 推荐列表 [(物品名,预测分数)]
    """
    user_num = user_item_rating_matrix.shape[0]
    # 计算用户相似度矩阵
    user_similarity_matrix = np.zeros((user_num, user_num))
    for i in range(user_num):
        for j in range(user_num):
            user_similarity_matrix[i, j] = calc_cosine_similarity(
                user_item_rating_matrix[i], user_item_rating_matrix[j]
            )

    # 获取目标用户和所有用户的相似度
    user_sims = user_similarity_matrix[target_user_id]
    user_sims[target_user_id] = -1  # 排除自己
    top_k_similar_user_ids = np.argsort(user_sims)[::-1][:top_k]

    print(f"\n目标用户{target_user_id} 最相似用户ID：{top_k_similar_user_ids}")
    print("对应相似度：", [user_sims[uid] for uid in top_k_similar_user_ids])

    item_pred_score = np.zeros(len(item_name_list))
    item_count = len(item_name_list)

    for item_idx in range(item_count):
        # 跳过用户已经评分过的物品
        if user_item_rating_matrix[target_user_id][item_idx] > 0:
            continue
        score_sum = 0.0
        weight_sum = 0.0
        for similar_uid in top_k_similar_user_ids:
            rating = user_item_rating_matrix[similar_uid][item_idx]
            if rating > 0:
                score_sum += rating * user_sims[similar_uid]
                weight_sum += user_sims[similar_uid]
        if weight_sum > 0:
            item_pred_score[item_idx] = score_sum / weight_sum

    # 按预测分从高到低排序
    sorted_item_idx = np.argsort(item_pred_score)[::-1]
    rec_result = [(item_name_list[i], item_pred_score[i])
                  for i in sorted_item_idx if item_pred_score[i] > 0]
    return rec_result


if __name__ == "__main__":
    # 用户-物品评分矩阵：行=用户，列=电影，0代表未评分
    user_item_rating_matrix = np.array([
        [5, 3, 0, 1, 0],
        [4, 0, 0, 1, 2],
        [1, 1, 0, 5, 4],
        [1, 0, 5, 4, 0],
        [0, 2, 4, 0, 5],
    ])
    item_name_list = ["电影A", "电影B", "电影C", "电影D", "电影E"]

    target_user_id = 0
    rec_list = user_cf_recommend(target_user_id, user_item_rating_matrix, item_name_list, top_k=2)
    print(f"\n===== 用户{target_user_id}推荐结果 =====")
    for item_name, pred_score in rec_list:
        print(f"{item_name}，预测评分：{pred_score:.2f}")
