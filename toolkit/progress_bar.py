from tqdm import tqdm
import time


def make_bar(percent: float, width: int = 20) -> str:
    """生成一个迷你进度条字符串"""
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f'[{bar}] {percent:.0f}%'


class ToolkitProgressBar(tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paused = False
        self.last_time = self._time()
        self.batch_bar = None  # 嵌套的批次进度条

    def pause(self):
        if not self.paused:
            self.paused = True
            self.last_time = self._time()

    def unpause(self):
        if self.paused:
            self.paused = False
            cur_t = self._time()
            self.start_t += cur_t - self.last_time
            self.last_print_t = cur_t

    def update(self, *args, **kwargs):
        if not self.paused:
            super().update(*args, **kwargs)

    def set_batch_progress(self, batch_num: int, total_batches: int, phase: str = ""):
        """设置批次进度"""
        if total_batches <= 1:
            return
        percent = (batch_num / total_batches) * 100
        bar_str = make_bar(percent, 15)
        postfix = f"批次 {batch_num}/{total_batches} {bar_str}"
        if phase:
            postfix += f" {phase}"
        self.set_postfix_str(postfix)

    def clear_batch_progress(self):
        """清除批次进度显示"""
        self.set_postfix_str("")
