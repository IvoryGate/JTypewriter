import tkinter as tk
from tkinter import ttk, scrolledtext
from pynput import keyboard
import threading
import queue
import time

class GlobalKeyboardListener:
    def __init__(self):
        # 创建一个队列用于线程间通信
        self.event_queue = queue.Queue()
        self.listener = None
        self.listening = False
        
    def on_press(self, key):
        """按键按下时的回调函数"""
        try:
            # 将按键事件放入队列
            self.event_queue.put(('press', key, time.time()))
        except Exception as e:
            print(f"Error in on_press: {e}")
        
    def on_release(self, key):
        """按键释放时的回调函数"""
        try:
            # 将释放事件放入队列
            self.event_queue.put(('release', key, time.time()))
            
            # 如果按下ESC键，停止监听
            if key == keyboard.Key.esc:
                return False
        except Exception as e:
            print(f"Error in on_release: {e}")
            
    def start_listening(self):
        """开始监听键盘事件"""
        self.listening = True
        # 创建并启动键盘监听器
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()
        
    def stop_listening(self):
        """停止监听键盘事件"""
        self.listening = False
        if self.listener:
            self.listener.stop()
            
    def get_events(self):
        """从队列中获取所有可用的事件"""
        events = []
        while not self.event_queue.empty():
            try:
                events.append(self.event_queue.get_nowait())
            except queue.Empty:
                break
        return events


class KeyboardListenerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pynput键盘监听示例")
        self.root.geometry("600x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建全局键盘监听器
        self.keyboard_listener = GlobalKeyboardListener()
        
        # 设置样式
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 10))
        
        # 创建界面组件
        self.create_widgets()
        
        # 启动键盘监听
        self.start_listener()
        
        # 开始处理事件
        self.process_events()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="pynput全局键盘监听演示", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 状态显示
        ttk.Label(main_frame, text="监听状态:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="运行中")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="green").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 提示信息
        info_label = ttk.Label(main_frame, text="提示: 按ESC键可停止监听", foreground="blue")
        info_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 按键事件显示区域
        ttk.Label(main_frame, text="键盘事件:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        
        # 使用ScrolledText代替Listbox，以便显示更多信息
        self.event_text = scrolledtext.ScrolledText(
            main_frame, 
            width=70, 
            height=15,
            font=("Courier", 10)
        )
        self.event_text.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 开始/停止按钮
        self.toggle_btn = ttk.Button(button_frame, text="停止监听", command=self.toggle_listener)
        self.toggle_btn.grid(row=0, column=0, padx=5)
        
        # 清空按钮
        clear_btn = ttk.Button(button_frame, text="清空记录", command=self.clear_events)
        clear_btn.grid(row=0, column=1, padx=5)
        
        # 退出按钮
        exit_btn = ttk.Button(button_frame, text="退出", command=self.on_closing)
        exit_btn.grid(row=0, column=2, padx=5)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def start_listener(self):
        """启动键盘监听"""
        self.keyboard_listener.start_listening()
        self.status_var.set("运行中")
        self.toggle_btn.config(text="停止监听")
        
    def stop_listener(self):
        """停止键盘监听"""
        self.keyboard_listener.stop_listening()
        self.status_var.set("已停止")
        self.toggle_btn.config(text="开始监听")
        
    def toggle_listener(self):
        """切换监听状态"""
        if self.keyboard_listener.listening:
            self.stop_listener()
        else:
            self.start_listener()
            
    def clear_events(self):
        """清空事件记录"""
        self.event_text.delete(1.0, tk.END)
        
    def process_events(self):
        """处理键盘事件（定期调用）"""
        # 获取所有新事件
        events = self.keyboard_listener.get_events()
        
        # 处理每个事件
        for event_type, key, timestamp in events:
            # 格式化时间
            time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
            
            # 格式化按键信息
            try:
                if hasattr(key, 'char') and key.char is not None:
                    key_str = f"'{key.char}'"
                else:
                    key_str = str(key).replace("Key.", "")
            except:
                key_str = str(key)
                
            # 添加到事件显示区域
            event_str = f"[{time_str}] {event_type.upper():7} {key_str}\n"
            self.event_text.insert(tk.END, event_str)
            
            # 自动滚动到底部
            self.event_text.see(tk.END)
            
            # 如果按下ESC键，停止监听
            if event_type == 'release' and key == keyboard.Key.esc:
                self.stop_listener()
        
        # 每隔100毫秒再次检查事件
        self.root.after(100, self.process_events)
        
    def on_closing(self):
        """应用程序关闭时的清理工作"""
        self.keyboard_listener.stop_listening()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = KeyboardListenerApp(root)
    root.mainloop()