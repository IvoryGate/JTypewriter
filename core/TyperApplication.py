import tkinter as tk

class TyperApplication:
    def __init__(self):
        """初始化程序及初始化配置"""
        self.root = tk.Tk()
        self.root.title("JTypewriter")
        self.root.geometry(
            f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}"
        )
        self.root.minsize(
            int(self.root.winfo_screenwidth()/2), 
            int(self.root.winfo_screenheight()/2)
        )
        self.root.maxsize(
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight()
        )
    def run(self) -> None:
        """运行应用"""
        self.root.mainloop()