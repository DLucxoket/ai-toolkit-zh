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
        self.dataset_size = 0  # 数据集总图片数
        self.current_image = 0  # 当前处理的图片序号

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

    def set_image_progress(self, image_idx: int, phase: str = ""):
        """设置当前图片进度"""
        if self.dataset_size > 0:
            percent = (image_idx / self.dataset_size) * 100
            bar_str = make_bar(percent, 15)
            postfix = f"图片 {image_idx}/{self.dataset_size} {bar_str}"
            if phase:
                postfix += f" {phase}"
            self.set_postfix_str(postfix)

    def clear_image_progress(self):
        """清除图片进度显示"""
        self.set_postfix_str("")
