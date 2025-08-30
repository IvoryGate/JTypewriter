import time
import threading
from collections import defaultdict

class TypingEngine:

    # ----------- 初始化 ----------- #

    def __init__(self):
        """初始化输入引擎"""
        # 文本
        self.text = ""
        self.expected_text = ""
        
        # 用户输入情况
        self.user_input = ""
        self.current_position = 0

        # 统计
        self.total_chars = 0
        self.correct_chars = 0
        self.error_counts = 0
        self.error_positions = set()
        self.error_analysis = defaultdict(int)

        # 打字机状态
        self.is_active = False
        self.is_completed = False

        # 计时器
        self.timer = None
        self.start_time = None
        self.end_time = None

    def load_text(self,text:str) -> None:
        """加载文本
        Args: 
            text(str): 文本
        """
        self.text = text
        self.expected_text = text

    def reset_engine(self) -> None:
        """重制打字引擎状态"""
        self.user_input = ""
        self.current_position = 0
        self.start_time = None
        self.end_time = None
        self.total_chars = len(self.text)
        self.correct_chars = 0
        self.error_counts = 0
        self.is_active = False
        self.is_completed = False
        self.timer = None

    # ----------- 引擎状态控制 ----------- #

    def start_session(self) -> None:
        """启动打字会话"""
        if not self.text:
            raise ValueError("文本未加载！")
        self.reset_engine()
        self.start_time = time.time()
        self.is_active = True

        # 启动计时器
        self.timer = threading.Thread(target=self.update_timer, daemon = True)
        self.timer.start()
    
    def pause_session(self) -> None:
        """暂停打字会话"""
        if self.is_active:
            self.is_active = False
            if self.start_time and not self.end_time:
                self.end_time = time.time()
    
    def resume_session(self) -> None:
        """恢复打字会话"""
        if not self.is_completed and not self.is_active:
            pause_duration = time.time() - self.end_time
            self.start_time += pause_duration
            self.end_time = None
            self.is_active = True
    
            self.timer = threading.Thread(target=self.update_timer, daemon = True)
            self.timer.start()

    def end_session(self) -> None:
        """结束练习会话"""
        if self.is_active:
            self.is_active = False
            self.end_time = time.time()
            self.is_completed = True

    # ----------- 用户输入处理 ----------- #

    def process_input(self, char:str):
        """用户输入字符处理
        Args:
            char(str): 输入的字符
        """

        expected_char = self.text[self.current_position]
        is_correct = char == expected_char

        self.user_input += char

        if is_correct:
            self.correct_chars += 1
        else:
            self.error_counts += 1
            self.error_positions.add(self.current_position)
            self.error_analysis[expected_char] += 1

        self.current_position += 1
        self.status_update(self.get_current_status())



    # ----------- 状态记录与更新 ----------- #

    def update_timer(self) -> None:
        """计时器更新"""
        while self.is_active and not self.is_completed:
            time.sleep(0.1)
            self.status_update(self.get_current_status())

    def get_current_status(self) -> dict:
        """获取当前状态信息
        Returns:
            status(dict): 包含当前所有信息的字典
        """
        duration = self.get_duration()
        statistic_info = self.calculate_statistic_info()

        return {
            'current_position': self.current_position,
            'total_chars': self.total_chars,
            'progress': self.current_position / self.total_chars * 100,
            'correct_chars': self.correct_chars,
            'error_counts': self.error_counts,
            'duration_time': duration,
            'wpm': statistic_info['wpm'],
            'accuracy': statistic_info['accuracy']
        }



    def get_duration(self) -> float:
        """获取经过的时间
        Returns:
            duration(float): 已用时间
        """
        if self.start_time is None :
            return 0
        if self.end_time is not None :
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def calculate_statistic_info(self) -> dict:
        """计算统计信息
        Returns:
            statistic_info(dict): 包含统计信息的字典
        """
        duration_time = self.get_duration()

        # 计算WPM
        if duration_time > 0 and self.current_position > 0:
            minuntes = duration_time / 60
            wpm = (self.correct_chars / 5) / minuntes
        else:
            wpm = 0

        # 计算准确率
        if self.current_position > 0:
            accuracy = (self.correct_chars / self.current_position) * 100
        else:
            accuracy = 0
        
        return {
            'wpm': round(wpm, 1),
            'accuracy': round(accuracy,1)
        }

    def status_update(self, status: dict):
        print(
            f"\r进度: {status['progress']:.1f}% | "
            f"速度: {status['wpm']} WPM | "
            f"准确率: {status['accuracy']:.1f}% | "
            f"错误: {status['error_counts']} | "
            f"时间: {self.format_time(status['duration_time'])}"
            "   ",
            end=""
        )


    def format_time(self, seconds) -> str:
        """将秒数格式化为 MM:SS 格式"""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"


if __name__ == "__main__":
    engine = TypingEngine()

    # 加载练习文本
    sample_text = "The quick brown fox jumps over the lazy dog."
    engine.load_text(sample_text)
    
    print("打字练习开始!")
    print("文本:", sample_text)
    print("请输入上面的文本 (输入完成后按回车):\n")

    engine.start_session()

    # 模拟用户输入
    user_input = "The quick_brown fox jumps pver the lazy dog."
    for char in user_input:
        is_correct = engine.process_input(char)
        time.sleep(0.1)  # 模拟输入延迟