import ctypes
import subprocess
import os

# 隐藏当前控制台窗口
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 启动Streamlit应用
subprocess.Popen(
    ["streamlit", "run", "vehicle_management_system.py"],
    cwd=current_dir,
    creationflags=subprocess.CREATE_NEW_CONSOLE  # 为Streamlit创建独立的可见控制台窗口
)