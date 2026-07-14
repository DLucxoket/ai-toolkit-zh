from tqdm import tqdm
import time


def make_bar(percent: float, width: int = 20) -> str:
    """生成一个迷你进度条字符串"""
    filled = int(width * percent / 100)
    bar = '#' * filled + '-' * (width - filled)
    return f'[{bar}] {percent:.0f}%'


class ToolkitProgressBar(tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paused = False
        self.last_time = self._time()
        self.dataset_size = 0  # 数据集总图片数
        self.current_image = 0  # 当前处理的图片序号
        self.last_loss_str = ""  # 上次的 loss 信息
        self.step_num = 0  # 当前步数

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

    def set_dataset_info(self, dataset_size: int):
        """设置数据集大小"""
        self.dataset_size = dataset_size

    def set_image_progress(self, image_idx: int, total_in_step: int, phase: str = ""):
        """设置当前图片进度 (当前step内的第几张 + 总进度)"""
        if total_in_step > 0:
            percent = (image_idx / total_in_step) * 100
            bar_str = make_bar(percent, 10)
            postfix = f"img {image_idx}/{total_in_step} {bar_str}"
            # 显示总进度
            if self.dataset_size > 0:
                global_idx = (self.step_num * total_in_step + image_idx - 1) % self.dataset_size + 1
                total_percent = (global_idx / self.dataset_size) * 100
                postfix += f" | total {global_idx}/{self.dataset_size} ({total_percent:.0f}%)"
            if phase:
                postfix += f" | {phase}"
            if self.last_loss_str:
                postfix += f" | {self.last_loss_str}"
            self.set_postfix_str(postfix)

    def clear_image_progress(self):
        """清除图片进度显示"""
        self.set_postfix_str("")
