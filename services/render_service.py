import subprocess
import os
import threading
from tasks.task_store import finish_task, fail_task

# 3DGS Python 环境
GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"

# 3DGS 项目根目录
GS_ROOT = r"G:\xf\Improving-ADC-3DGS"


def render_process(task_id, model_path):
    """
    实际执行渲染的线程函数
    """
    try:
        model_path = os.path.abspath(model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型路径不存在: {model_path}")

        cmd = [
            GS_PYTHON,
            os.path.join(GS_ROOT, "render.py"),
            "-m",
            model_path
        ]

        print(f"[Render Task {task_id}] CMD: {' '.join(cmd)}")

        # 使用 subprocess.run 阻塞等待完成
        result = subprocess.run(
            cmd,
            cwd=GS_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print(f"[Render Task {task_id}] Error: {result.stderr}")
            raise RuntimeError(f"渲染脚本执行失败: {result.stderr[-200:]}") # 只截取最后200字符

        print(f"[Render Task {task_id}] Finished successfully.")
        finish_task(task_id, model_path)

    except Exception as e:
        print(f"[Render Task {task_id}] Exception: {e}")
        fail_task(task_id, str(e))


def start_render(task_id, model_path):
    """
    启动渲染任务（异步）
    """
    thread = threading.Thread(
        target=render_process,
        args=(task_id, model_path),
        daemon=True
    )
    thread.start()
