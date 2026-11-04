import pandas as pd
import numpy as np

# ======================
# 维度：时间季度time，地区location，商品item；度量：销售额money_sold
# time(Q1‑Q4), location=[深圳,杭州,南京,武汉], item=[日常用品,饮料,电器,食品]
# ======================
data = [
    {"time": "Q1", "location": "深圳", "item": "日常用品", "money_sold": 440},
    {"time": "Q1", "location": "杭州", "item": "日常用品", "money_sold": 1560},
    {"time": "Q1", "location": "南京", "item": "日常用品", "money_sold": 395},
    {"time": "Q1", "location": "武汉", "item": "日常用品", "money_sold": 605},
    {"time": "Q1", "location": "深圳", "item": "饮料", "money_sold": 220},
    {"time": "Q1", "location": "杭州", "item": "饮料", "money_sold": 880},
    {"time": "Q1", "location": "南京", "item": "饮料", "money_sold": 210},
    {"time": "Q1", "location": "武汉", "item": "饮料", "money_sold": 825},
    {"time": "Q1", "location": "深圳", "item": "电器", "money_sold": 30},
    {"time": "Q1", "location": "杭州", "item": "电器", "money_sold": 60},
    {"time": "Q1", "location": "南京", "item": "电器", "money_sold": 8},
    {"time": "Q1", "location": "武汉", "item": "电器", "money_sold": 14},
    {"time": "Q1", "location": "深圳", "item": "食品", "money_sold": 200},
    {"time": "Q1", "location": "杭州", "item": "食品", "money_sold": 310},
    {"time": "Q1", "location": "南京", "item": "食品", "money_sold": 120},
    {"time": "Q1", "location": "武汉", "item": "食品", "money_sold": 400},
    {"time": "Q2", "location": "深圳", "item": "日常用品", "money_sold": 410},
    {"time": "Q2", "location": "杭州", "item": "日常用品", "money_sold": 1420},
    {"time": "Q2", "location": "南京", "item": "日常用品", "money_sold": 360},
    {"time": "Q2", "location": "武汉", "item": "日常用品", "money_sold": 580},
    {"time": "Q3", "location": "深圳", "item": "日常用品", "money_sold": 380},
    {"time": "Q3", "location": "杭州", "item": "日常用品", "money_sold": 1300},
    {"time": "Q3", "location": "南京", "item": "日常用品", "money_sold": 330},
    {"time": "Q3", "location": "武汉", "item": "日常用品", "money_sold": 520},
    {"time": "Q4", "location": "深圳", "item": "日常用品", "money_sold": 350},
    {"time": "Q4", "location": "杭州", "item": "日常用品", "money_sold": 1200},
    {"time": "Q4", "location": "南京", "item": "日常用品", "money_sold": 300},
    {"time": "Q4", "location": "武汉", "item": "日常用品", "money_sold": 480},
]
df = pd.DataFrame(data)
print("====立方体明细数据（事实表）====")
print(df.head(12))

# ----------------------
# 模拟维度表（星型模型：事实表+3张维表）
# ----------------------
dim_time = pd.DataFrame(
    {
        "time": ["Q1", "Q2", "Q3", "Q4"],
        "half_year": ["H1", "H1", "H2", "H2"],
        "year": ["2025"] * 4,
    }
)

dim_location = pd.DataFrame(
    {
        "location": ["深圳", "杭州", "南京", "武汉"],
        "province": ["广东", "浙江", "江苏", "湖北"],
    }
)

dim_item = pd.DataFrame(
    {
        "item": ["日常用品", "饮料", "电器", "食品"],
        "category": ["百货", "饮品", "家电", "生鲜"],
    }
)

# ==========单独打印三张维度表==========
print("\n" + "=" * 50)
print("【时间维度表 dim_time】层级：年 → 半年 → 季度")
print(dim_time)

print("\n" + "=" * 50)
print("【地区维度表 dim_location】层级：省份 → 城市")
print(dim_location)

print("\n" + "=" * 50)
print("【商品维度表 dim_item】层级：商品大类 → 单品")
print(dim_item)
# ============================================================

# 事实表join维度表，完整星型模型
df_star = (
    df.merge(dim_time, on="time")
    .merge(dim_location, on="location")
    .merge(dim_item, on="item")
)
print("\n====星型模型：事实表关联维度表之后的宽表====")
print(
    df_star[
        ["time", "half_year", "province", "location", "category", "item", "money_sold"]
    ].head(10)
)


#  上卷
print("\n" + "=" * 60)
print("【1.上卷 Roll‑up】城市 → 省份（沿着地区维度向上聚合）")
rollup_province = (
    df_star.groupby(["time", "province", "item"])["money_sold"].sum().reset_index()
)
print(rollup_province)

# 下钻
print("\n" + "=" * 60)
print("【2.下钻 Drill‑down】省份下钻回到城市（沿着维度向下拆分明细）")
drill_city = rollup_province.merge(dim_location, on="province")
print(drill_city[["time", "province", "location", "item", "money_sold"]].head(10))

# 切片
print("【3.切片 Slice】固定 time=Q1，切出一个平面（单个维度固定取值）")
slice_q1 = df_star[df_star["time"] == "Q1"]
print(slice_q1[["time", "location", "item", "money_sold"]])

# 切块
print("\n" + "=" * 60)
print(
    "【4.切块 Dice】多维度过滤：location in [南京,武汉] & time in [Q1,Q2] & item in [日常用品,饮料]"
)
dice_data = df_star[
    (df_star["location"].isin(["南京", "武汉"]))
    & (df_star["time"].isin(["Q1", "Q2"]))
    & (df_star["item"].isin(["日常用品", "饮料"]))
]

# 转轴
print("\n" + "=" * 60)
print("【5.转轴 Pivot】旋转维度，item放行，location放列")
pivot_table = pd.pivot_table(
    data=slice_q1, index="item", columns="location", values="money_sold", aggfunc="sum"
)
print(pivot_table)


# 统计2024上半年 H1（Q1+Q2），各个商品大类 category 的总销售额。
print("\n" + "=" * 60)

h1_total = (
    df_star[(df_star["half_year"] == "H1") & (df_star["time"] == "Q1") | (df_star["time"] == "Q2")].groupby("category")["money_sold"].sum().reset_index()
)
print(h1_total)

