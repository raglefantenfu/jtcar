import subprocess
import sys
import os
import webbrowser
import time

def start_system():
    # 获取环境变量中的端口号，默认为8501
    port = os.environ.get('PORT', '8501')
    
    # 构建Streamlit启动命令
    command = [
        sys.executable,
        '-m', 'streamlit',
        'run',
        'vehicle_management_system.py',
        '--server.address', '0.0.0.0',  # 绑定所有网络接口，支持云部署
        '--server.port', port,
        '--server.headless', 'false'  # 禁用无头模式，允许自动打开浏览器
    ]
    
    try:
        print(f"正在启动车辆管理系统，端口：{port}...")
        # 执行命令
        # 启动服务器在后台运行
        process = subprocess.Popen(command)
        
        # 等待服务器启动
        time.sleep(3)
        
        # 自动打开浏览器
        webbrowser.open(f"http://localhost:{port}")
        
        # 等待进程结束
        process.wait()
    except subprocess.CalledProcessError as e:
        print(f"启动失败，错误代码：{e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("错误：未找到Streamlit或Python解释器")
        sys.exit(1)

if __name__ == "__main__":
    start_system()