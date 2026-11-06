#!/bin/bash
#SBATCH --job-name=alexnet        # 作业名称
#SBATCH --partition=gpu           # 分区/队列名，用 sinfo 命令查看可用的分区，改成实际的
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4         # 申请的 CPU 核数
#SBATCH --gres=gpu:1              # 申请 1 张 GPU
#SBATCH --time=02:00:00           # 最长运行时间，超时会被杀掉
#SBATCH --output=slurm_%j.out     # 标准输出文件（%j 会替换成作业号）
#SBATCH --error=slurm_%j.err      # 错误输出文件

# ============ 1. 激活 conda 环境 ============

# conda 安装在哪个目录就 source 哪个；在登录节点用 conda info --base 可查到实际路径
# 如果装的是 anaconda 就把 miniconda3 改成 anaconda3
source ~/miniconda3/etc/profile.d/conda.sh
conda activate base

# ============ 2. 进入工作目录（改成你实际上传 demo.py 的路径）============

cd /home/your_username/week_eight

# ============ 3. 运行 ============

# 先确认 torch 能看到 GPU；输出 False 说明装的是 CPU 版 torch，需要重装 GPU 版
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

python demo.py
