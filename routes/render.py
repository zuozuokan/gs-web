from flask import Blueprint, request, jsonify
from services.render_service import start_render
from tasks.task_store import create_task, get_task

render_bp = Blueprint("render", __name__, url_prefix="/api/render")


@render_bp.route("/start", methods=["POST"])
def start_render_api():
    """
    前端传：
    {
        "model_path": "训练数据的文件夹"
    }
    """
    try:
        data = request.json
        if not data or "model_path" not in data:
            return jsonify({
                "success": False,
                "msg": "缺少 model_path"
            }), 400

        model_path = data["model_path"]
        task_id = create_task()

        start_render(task_id, model_path)

        return jsonify({
            "success": True,
            "msg": "渲染已启动",
            "task_id": task_id
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "msg": str(e)
        }), 500


@render_bp.route("/status/<task_id>", methods=["GET"])
def get_render_status(task_id):
    task = get_task(task_id)
    if not task:
        return jsonify({
            "success": False,
            "msg": "任务不存在"
        }), 404
    return jsonify(task)
