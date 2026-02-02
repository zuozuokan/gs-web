from flask import Blueprint, request, jsonify
from services.metric_service import run_metric
import os

metric_bp = Blueprint("metric", __name__)

@metric_bp.route("/evaluate", methods=["POST"])
def evaluate_metric():
    """
    输入：
    {
        "model_path": "与render相同的训练数据的文件夹"
    }

    输出：
    {
        "success": true,
        "data": {
            "PSNR": 28.31,
            "SSIM": 0.912,
            "LPIPS": 0.084
        }
    }
    """
    try:
        data = request.json or {}
        model_path = data.get("model_path")

        if not model_path:
            return jsonify({
                "success": False,
                "msg": "缺少 model_path"
            }), 400

        if not os.path.exists(model_path):
            return jsonify({
                "success": False,
                "msg": f"model_path 不存在: {model_path}"
            }), 400

        metrics = run_metric(model_path)

        return jsonify({
            "success": True,
            "data": metrics
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "msg": str(e)
        }), 500
