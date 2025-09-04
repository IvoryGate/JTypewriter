# import os
# import sqlite3
# DATABASE_PATH = 'JTypewriterDB'
# print(os.path.exists(DATABASE_PATH))

# print(type(sqlite3.connect(database=DATABASE_PATH)))

# import tkinter as tk

# root = tk.Tk()

# # 获取像素尺寸
# width_px = root.winfo_screenwidth()
# height_px = root.winfo_screenheight()

# # 获取毫米尺寸
# width_mm = root.winfo_screenmmwidth()
# height_mm = root.winfo_screenmmheight()

# print(f"屏幕尺寸(像素): {width_px} x {height_px}")
# print(f"屏幕尺寸(毫米): {width_mm} x {height_mm}")

# root.mainloop()

import time
import threading
from collections import defaultdict
from datetime import datetime

class TypingEngine:
    def __init__(self):
        # 练习文本相关
        self.text = ""  # 完整的练习文本
        self.expected_text = ""  # 期望输入的文本（可能包含格式化）
        
        # 用户输入相关
        self.user_input = ""  # 用户已输入的内容
        self.current_index = 0  # 当前输入位置
        
        # 统计相关
        self.start_time = None  # 开始时间
        self.end_time = None  # 结束时间
        self.errors = 0  # 错误次数
        self.total_chars = 0  # 总字符数
        self.correct_chars = 0  # 正确字符数
        self.error_positions = set()  # 错误位置集合
        self.error_analysis = defaultdict(int)  # 错误分析：字符 -> 错误次数
        
        # 状态标志
        self.is_active = False  # 是否处于活动状态
        self.is_completed = False  # 是否已完成
        
        # 回调函数
        self.on_update = None  # 状态更新回调
        self.on_complete = None  # 完成回调
        self.on_error = None  # 错误回调
    
    def load_text(self, text):
        """
        加载练习文本
        
        Args:
            text (str): 练习文本内容
        """
        self.text = text
        self.expected_text = text
        self.reset()
    
    def reset(self):
        """重置引擎状态"""
        self.user_input = ""
        self.current_index = 0
        self.start_time = None
        self.end_time = None
        self.errors = 0
        self.total_chars = len(self.text)
        self.correct_chars = 0
        self.error_positions.clear()
        self.error_analysis.clear()
        self.is_active = False
        self.is_completed = False
    
    def start_session(self):
        """开始练习会话"""
        if not self.text:
            raise ValueError("没有加载练习文本")
        
        self.reset()
        self.start_time = time.time()
        self.is_active = True
        
        # 启动计时器线程
        self.timer_thread = threading.Thread(target=self._update_timer, daemon=True)
        self.timer_thread.start()
    
    def pause_session(self):
        """暂停练习会话"""
        if self.is_active:
            self.is_active = False
            if self.start_time and not self.end_time:
                self.end_time = time.time()
    
    def resume_session(self):
        """恢复练习会话"""
        if not self.is_completed and not self.is_active:
            # 调整开始时间以考虑暂停时间
            pause_duration = time.time() - self.end_time
            self.start_time += pause_duration
            self.end_time = None
            self.is_active = True
            
            # 重新启动计时器线程
            self.timer_thread = threading.Thread(target=self._update_timer, daemon=True)
            self.timer_thread.start()
    
    def end_session(self):
        """结束练习会话"""
        if self.is_active:
            self.is_active = False
            self.end_time = time.time()
            self.is_completed = True
            
            # 触发完成回调
            if self.on_complete:
                self.on_complete(self.get_stats())
    
    def process_input(self, char):
        """
        处理用户输入的字符
        
        Args:
            char (str): 输入的字符
            
        Returns:
            bool: 输入是否正确
        """
        if not self.is_active or self.is_completed:
            return False
        
        # 如果是第一个字符，确保会话已开始
        if self.current_index == 0 and self.start_time is None:
            self.start_session()
        
        # 检查是否超出文本范围
        if self.current_index >= len(self.text):
            return False
        
        # 获取期望的字符
        expected_char = self.text[self.current_index]
        is_correct = char == expected_char
        
        # 更新用户输入
        self.user_input += char
        
        # 更新统计信息
        if is_correct:
            self.correct_chars += 1
        else:
            self.errors += 1
            self.error_positions.add(self.current_index)
            self.error_analysis[expected_char] += 1
            
            # 触发错误回调
            if self.on_error:
                self.on_error(self.current_index, char, expected_char)
        
        # 移动到下一个字符
        self.current_index += 1
        
        # 检查是否完成
        if self.current_index >= len(self.text):
            self.end_session()
        
        # 触发更新回调
        if self.on_update:
            self.on_update(self.get_current_status())
        
        return is_correct
    
    def backspace(self):
        """
        处理退格键
        
        Returns:
            bool: 是否成功回退
        """
        if not self.is_active or self.is_completed or self.current_index == 0:
            return False
        
        # 回退一个字符
        self.current_index -= 1
        last_char = self.user_input[-1]
        self.user_input = self.user_input[:-1]
        
        # 更新统计信息
        expected_char = self.text[self.current_index]
        if last_char == expected_char:
            self.correct_chars -= 1
        else:
            self.errors -= 1
            if self.current_index in self.error_positions:
                self.error_positions.remove(self.current_index)
            self.error_analysis[expected_char] = max(0, self.error_analysis[expected_char] - 1)
        
        # 触发更新回调
        if self.on_update:
            self.on_update(self.get_current_status())
        
        return True
    
    def skip_character(self):
        """
        跳过当前字符（标记为错误但不要求重新输入）
        
        Returns:
            bool: 是否成功跳过
        """
        if not self.is_active or self.is_completed or self.current_index >= len(self.text):
            return False
        
        # 获取期望的字符
        expected_char = self.text[self.current_index]
        
        # 更新统计信息
        self.errors += 1
        self.error_positions.add(self.current_index)
        self.error_analysis[expected_char] += 1
        
        # 移动到下一个字符
        self.current_index += 1
        
        # 检查是否完成
        if self.current_index >= len(self.text):
            self.end_session()
        
        # 触发更新回调
        if self.on_update:
            self.on_update(self.get_current_status())
        
        return True
    
    def get_current_status(self):
        """
        获取当前状态信息
        
        Returns:
            dict: 包含当前状态信息的字典
        """
        elapsed = self.get_elapsed_time()
        stats = self.calculate_stats()
        
        return {
            'current_index': self.current_index,
            'total_chars': self.total_chars,
            'progress': self.current_index / self.total_chars * 100 if self.total_chars > 0 else 0,
            'elapsed_time': elapsed,
            'wpm': stats['wpm'],
            'accuracy': stats['accuracy'],
            'errors': self.errors,
            'correct_chars': self.correct_chars,
            'remaining_chars': self.total_chars - self.current_index,
            'is_active': self.is_active,
            'is_completed': self.is_completed
        }
    
    def get_elapsed_time(self):
        """
        获取已用时间（秒）
        
        Returns:
            float: 已用时间（秒）
        """
        if self.start_time is None:
            return 0
        
        if self.end_time is not None:
            return self.end_time - self.start_time
        
        return time.time() - self.start_time
    
    def calculate_stats(self):
        """
        计算当前统计信息
        
        Returns:
            dict: 包含统计信息的字典
        """
        elapsed = self.get_elapsed_time()
        
        # 计算WPM（Words Per Minute）
        # 标准WPM计算：5个字符=1个单词
        if elapsed > 0 and self.current_index > 0:
            minutes = elapsed / 60
            wpm = (self.correct_chars / 5) / minutes
        else:
            wpm = 0
        
        # 计算准确率
        if self.current_index > 0:
            accuracy = (self.correct_chars / self.current_index) * 100
        else:
            accuracy = 0
        
        return {
            'wpm': round(wpm, 1),
            'accuracy': round(accuracy, 1),
            'errors': self.errors,
            'correct_chars': self.correct_chars,
            'total_chars': self.total_chars,
            'elapsed_time': round(elapsed, 1),
            'error_rate': round((self.errors / self.current_index * 100), 1) if self.current_index > 0 else 0
        }
    
    def get_stats(self):
        """
        获取完整的统计信息（包括错误分析）
        
        Returns:
            dict: 完整的统计信息
        """
        stats = self.calculate_stats()
        stats.update({
            'error_positions': list(self.error_positions),
            'error_analysis': dict(self.error_analysis),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'completion_time': round(self.get_elapsed_time(), 1) if self.is_completed else None
        })
        return stats
    
    def get_formatted_text(self, highlight_errors=True, current_position=True):
        """
        获取格式化文本，用于显示
        
        Args:
            highlight_errors (bool): 是否高亮错误
            current_position (bool): 是否标记当前位置
            
        Returns:
            str: 格式化后的文本
        """
        if not self.text:
            return ""
        
        formatted_text = ""
        
        for i, char in enumerate(self.text):
            # 处理已输入部分
            if i < self.current_index:
                if i in self.error_positions and highlight_errors:
                    # 错误字符：红色
                    formatted_text += f"[ERROR]{char}[/ERROR]"
                else:
                    # 正确字符：绿色
                    formatted_text += f"[CORRECT]{char}[/CORRECT]"
            elif i == self.current_index and current_position:
                # 当前位置：下划线
                formatted_text += f"[CURRENT]{char}[/CURRENT]"
            else:
                # 未输入部分：正常显示
                formatted_text += char
        
        return formatted_text
    
    def _update_timer(self):
        """定时更新计时器（内部方法）"""
        while self.is_active and not self.is_completed:
            time.sleep(0.1)  # 每100ms更新一次
            
            # 触发更新回调
            if self.on_update:
                self.on_update(self.get_current_status())
    
    def set_callbacks(self, on_update=None, on_complete=None, on_error=None):
        """
        设置回调函数
        
        Args:
            on_update: 状态更新回调函数
            on_complete: 完成回调函数
            on_error: 错误回调函数
        """
        self.on_update = on_update
        self.on_complete = on_complete
        self.on_error = on_error


# 辅助函数：格式化时间显示
def format_time(seconds):
    """将秒数格式化为 MM:SS 格式"""
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"


# 示例使用
if __name__ == "__main__":
    # 创建打字引擎实例
    engine = TypingEngine()
    
    # 设置回调函数
    def on_update(status):
        print(f"\r进度: {status['progress']:.1f}% | "
              f"速度: {status['wpm']} WPM | "
              f"准确率: {status['accuracy']:.1f}% | "
              f"错误: {status['errors']} | "
              f"时间: {format_time(status['elapsed_time'])}", end="")
    
    def on_complete(stats):
        print(f"\n\n练习完成!")
        print(f"最终速度: {stats['wpm']} WPM")
        print(f"最终准确率: {stats['accuracy']:.1f}%")
        print(f"总错误数: {stats['errors']}")
        print(f"用时: {format_time(stats['elapsed_time'])}")
        
        # 显示错误分析
        if stats['error_analysis']:
            print("\n错误分析:")
            for char, count in stats['error_analysis'].items():
                print(f"  '{char}': {count}次错误")
    
    def on_error(position, input_char, expected_char):
        print(f"\n错误: 输入了 '{input_char}'，应为 '{expected_char}'")
    
    engine.set_callbacks(on_update, on_complete, on_error)
    
    # 加载练习文本
    sample_text = "The quick brown fox jumps over the lazy dog."
    engine.load_text(sample_text)
    
    print("打字练习开始!")
    print("文本:", sample_text)
    print("请输入上面的文本 (输入完成后按回车):\n")
    
    # 开始练习
    engine.start_session()
    
    # 模拟用户输入
    user_input = "The quick_brown fox jumps pver the lazy dog."
    for char in user_input:
        # 模拟用户输入（这里直接使用正确字符，实际应用中应从键盘获取）
        is_correct = engine.process_input(char)
        time.sleep(0.1)  # 模拟输入延迟
    
    # 等待练习完成
    while not engine.is_completed:
        time.sleep(0.1)