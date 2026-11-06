import torch


def _shape_text(value):
    """把张量（或张量元组）转换为形状字符串。"""
    if isinstance(value, torch.Tensor):
        return str(list(value.shape))
    if isinstance(value, (tuple, list)):
        parts = [_shape_text(v) for v in value]
        return " | ".join(parts) if parts else "()"
    return type(value).__name__


def _pad(text, width):
    """按显示宽度右侧补空格，保证表格对齐（中文字符按 2 个宽度计算）。"""
    display = sum(2 if ord(ch) > 127 else 1 for ch in text)
    return text + " " * max(width - display, 1)


def print_layer_shapes(model, input_shape):
    """打印模型输入图片的张量形状，并按执行顺序打印每一层的名称、类型与输入/输出形状。

    参数:
        model: nn.Module 模型
        input_shape: 输入图片形状（不含 batch 维），如 (3, 32, 32)
    """
    device = next(model.parameters()).device
    shape = tuple(input_shape) if len(input_shape) == 4 else (1, *input_shape)
    x = torch.zeros(shape, device=device)

    # 1. 打印输入图片张量形状
    print(f"输入图片张量形状: {list(shape)} (batch, 通道, 高, 宽)")

    # 2. 注册前向钩子，按执行顺序记录每层的名称、类型、输入/输出形状
    records = []

    def make_hook(name):
        def hook(module, inputs, output):
            records.append(
                (name, type(module).__name__, _shape_text(inputs), _shape_text(output))
            )

        return hook

    handles = [
        module.register_forward_hook(make_hook(name))
        for name, module in model.named_modules()
        if name  # 跳过模型本身
    ]

    # 3. 空跑一次前向传播触发钩子（eval + no_grad，结束后恢复模型原状态并移除钩子）
    was_training = model.training
    model.eval()
    with torch.no_grad():
        model(x)
    model.train(was_training)
    for handle in handles:
        handle.remove()

    # 4. 打印形状流转表格
    name_w, type_w, shape_w = 24, 14, 22
    separator = "-" * (name_w + type_w + shape_w + 10)
    print(separator)
    print(
        _pad("层名称", name_w)
        + _pad("层类型", type_w)
        + _pad("输入形状", shape_w)
        + "输出形状"
    )
    print(separator)
    for name, layer_type, in_shape, out_shape in records:
        print(
            _pad(name, name_w)
            + _pad(layer_type, type_w)
            + _pad(in_shape, shape_w)
            + out_shape
        )
    print(separator)
