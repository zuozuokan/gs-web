import time

# 简化版：用内存存（毕业设计完全 OK）
tasks = {}

def create_task():
    task_id = str(int(time.time() * 1000))
    tasks[task_id] = {
        "status": "running",
        "model_path": None
    }
    return task_id

def finish_task(task_id, model_path):
    tasks[task_id]["status"] = "finished"
    tasks[task_id]["model_path"] = model_path
    print(f"[Task {task_id}] 训练完成")


def fail_task(task_id, error_msg):
    tasks[task_id]["status"] = "failed"
    tasks[task_id]["error"] = error_msg

def get_task(task_id):
    return tasks.get(task_id)
