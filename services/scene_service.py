import subprocess
import os
import threading
import logging

logger = logging.getLogger(__name__)

# SIBR Viewer 路径
GS_VIEWER = r"G:\xf\Improving-ADC-3DGS\viewers\bin\SIBR_gaussianViewer_app.exe"
GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"
GS_ROOT = r"G:\xf\Improving-ADC-3DGS"

class SceneService:
    def preview_scene(self, model_path):
        """
        启动 SIBR Viewer 预览场景
        """
        try:
            model_path = os.path.abspath(model_path)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型路径不存在: {model_path}")

            # SIBR Viewer 是一个 GUI 程序，我们使用 Popen 启动它而不等待它结束
            # 这样用户可以在服务器端看到窗口（假设是本地部署或有显示器连接）
            cmd = [
                GS_VIEWER,
                "-m",
                model_path
            ]
            
            logger.info(f"Starting preview for {model_path}")
            logger.info(f"CMD: {' '.join(cmd)}")
            
            # 使用 Popen 非阻塞启动
            subprocess.Popen(
                cmd,
                cwd=GS_ROOT,  # 设置工作目录
                stdout=subprocess.DEVNULL, # 忽略输出，避免缓冲区填满导致挂起
                stderr=subprocess.DEVNULL
            )
            
            return True, "预览已启动"
            
        except Exception as e:
            logger.error(f"启动预览失败: {e}")
            return False, str(e)
