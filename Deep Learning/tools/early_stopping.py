class EarlyStopping:
    """按“准确率越高越好”实现的早停机制。

    每轮将当前准确率传入 __call__：
    - 若准确率比历史最佳提升超过 delta，则重置计数器并更新最佳值；
    - 否则计数器 +1，当计数器达到 patience 时置 early_stop 为 True。
    """

    def __init__(self, patience=5, delta=0.0, verbose=False):
        self.patience = patience          # 容忍多少轮无提升后停止
        self.delta = delta                # 视为“提升”所需的最小准确率增幅
        self.verbose = verbose            # 是否打印提示信息
        self.counter = 0                  # 连续无提升的轮数
        self.best_score = None            # 历史最佳准确率
        self.early_stop = False           # 是否触发早停

    def __call__(self, acc):
        # 第一轮：直接记录当前准确率作为初始最佳值
        if self.best_score is None:
            self.best_score = acc
            if self.verbose:
                print(f"EarlyStopping: 初始最佳准确率 {acc:.4f}")
            return

        if acc > self.best_score + self.delta:
            # 准确率提升：更新最佳值并重置计数器
            self.best_score = acc
            self.counter = 0
            if self.verbose:
                print(f"EarlyStopping: 准确率提升至 {acc:.4f}，计数器已重置")
        else:
            # 无提升：计数器 +1，达到 patience 则触发早停
            self.counter += 1
            if self.verbose:
                print(
                    f"EarlyStopping: 无提升 ({acc:.4f} <= 最佳 {self.best_score:.4f})，"
                    f"计数 {self.counter}/{self.patience}"
                )
            if self.counter >= self.patience:
                self.early_stop = True
                if self.verbose:
                    print("EarlyStopping: 触发早停，提前结束训练！")
                    
