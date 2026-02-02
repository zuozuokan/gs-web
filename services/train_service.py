# ---------------------------------------------------------------------------
import threading
import subprocess
import os
from tasks.task_store import finish_task, fail_task
from services.history_service import HistoryService

GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"
# GS_ROOT = r"G:\xf\Improving-ADC-3DGS"
GS_ROOT = r"G:\xf\gs_web\user"
GS_CODE_ROOT = r"G:\xf\Improving-ADC-3DGS"
GS_VIEWER = r"G:\xf\Improving-ADC-3DGS\viewers\bin\SIBR_remoteGaussian_app.exe"


def train_process(task_id, scene_dir, username, scene_name):
    try:
        # 1️⃣ 模型目录
        model_dir = os.path.abspath(
            os.path.join(GS_ROOT, username, "models",  scene_name)
        )
        os.makedirs(model_dir, exist_ok=True)

        # 记录到历史记录表
        try:
            history_service = HistoryService()
            history_service.add_train_record(
                username=username,
                task_id=task_id,
                dataset_path=scene_dir,
                train_model_path=model_dir
            )
        except Exception as e:
            print(f"[History Error] Failed to add train record: {e}")

        # 2️⃣ 训练命令
        train_cmd = [
            GS_PYTHON,
            os.path.join(GS_CODE_ROOT, "train.py"),
            "-s", scene_dir,
            "--model_path", model_dir,
            "--iterations", "600",
            "--resolution", "2"
        ]

        print("[Train CMD]")
        print(" ".join(train_cmd))

        # ✅ 非阻塞启动训练
        train_proc = subprocess.Popen(
            train_cmd,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
            text=True
        )

        # 3️⃣ 立即启动 viewer（无需等待）
        print("[Viewer] Launching viewer...")
        subprocess.Popen(
            [GS_VIEWER],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # 4️⃣ 等待训练结束
        train_proc.wait()

        if train_proc.returncode != 0:
            raise RuntimeError("Train failed")

        finish_task(task_id, model_dir)

    except Exception as e:
        print("[Train Error]", e)
        fail_task(task_id, str(e))


def start_training(task_id, scene_dir, username, scene_name):
    threading.Thread(
        target=train_process,
        args=(task_id, scene_dir, username, scene_name),
        daemon=True
    ).start()
