import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from PIL import Image

# 1. 读取图片
img = Image.open("img.png").convert("RGB")
img = img.resize((100, 100))  # 固定100*100像素
img_array = np.array(img)
h, w, c = img_array.shape

# 2. 把H×W×3图片 转化为 像素样本矩阵 (10000,3)，每一行=一个RGB三维向量
pixels = img_array.reshape(-1, 3)

# 3. K-Means聚类，k=4
k = 4
kmeans = KMeans(n_clusters=k, n_init="auto", random_state=42)
labels = kmeans.fit_predict(pixels)
centers = kmeans.cluster_centers_.astype(np.uint8)

# 4. 聚类
seg_pixels = centers[labels]
seg_img = seg_pixels.reshape(h, w, 3)

# 5. 绘图
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.title("原图")
plt.imshow(img_array)
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title(f"K-means分割 k={k}")
plt.imshow(seg_img)
plt.axis("off")

plt.tight_layout()
plt.show()
