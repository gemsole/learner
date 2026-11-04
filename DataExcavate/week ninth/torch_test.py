import torch
print("PyTorch 版本:", torch.__version__)
print("CUDA 是否可用:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA 版本:", torch.version.cuda)
    print("当前显卡设备:", torch.cuda.get_device_name(0))
else:
    print("无法使用GPU，请检查环境配置！")