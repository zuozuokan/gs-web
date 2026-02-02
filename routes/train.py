from flask import Blueprint, request, jsonify
from services.train_service import start_training
from tasks.task_store import create_task, get_task

train_bp = Blueprint("train", __name__)

# controller层

@train_bp.route("/start", methods=["POST"])
def start():
    data = request.json
    task_id = create_task()
    
    # 获取 username，默认为 'default' 如果未提供
    username = data.get("username", "default")

    start_training(
        task_id=task_id,
        scene_dir=data["scene_dir"],
        username=username,
        scene_name=data["scene_name"]
    )

    return jsonify({
        "task_id": task_id
    })

@train_bp.route("/status/<task_id>", methods=["GET"])
def status(task_id):
    return jsonify(get_task(task_id))
