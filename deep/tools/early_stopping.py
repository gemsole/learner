import copy
import torch


class EarlyStopping:
    """
    patience: 容忍多少轮无提升后停止
    delta: 视为“提升”所需的最小增幅
    mode: 'max'（如准确率）或 'min'（如 Loss）
    hint: 是否打印提示信息
    """

    def __init__(self, patience=5, delta=0.0, mode="max", hint=False):
        self.patience = patience
        self.delta = delta
        self.mode = mode
        self.hint = hint
        
        self.best_model = None
        self.counter = 0
        self.early_stop = False
        self.best_score = None

        # 根据模式定义优化的比较逻辑
        if self.mode == "max":
            self.is_better = lambda current, best: current > best + self.delta
        elif self.mode == "min":
            self.is_better = lambda current, best: current < best - self.delta
        else:
            raise ValueError(f"Unsupported mode: {self.mode}. Use 'max' or 'min'.")

    def __call__(self, score, model):
        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(model)
            if self.hint:
                print(f"EarlyStopping: 初始最佳指标 {score:.4f}")
            return

        if self.is_better(score, self.best_score):
            self.best_score = score
            self.save_checkpoint(model)
            self.counter = 0
            if self.hint:
                print(f"EarlyStopping: 指标提升至 {score:.4f}，计数器已重置")
        else:
            self.counter += 1
            if self.hint:
                print(
                    f"EarlyStopping: 无提升 ({score:.4f} vs 最佳 {self.best_score:.4f})，"
                    f"计数 {self.counter}/{self.patience}"
                )
            if self.counter >= self.patience:
                self.early_stop = True
                if self.hint:
                    print("EarlyStopping: 触发早停，提前结束训练！")

    def save_checkpoint(self, model):
        """优化：仅克隆 state_dict 中的 tensor，避免深拷贝整个模型对象的开销"""
        self.best_model = {k: v.cpu().clone() for k, v in model.state_dict().items()}