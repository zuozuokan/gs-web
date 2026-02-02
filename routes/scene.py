from flask import Blueprint, jsonify, request, render_template
from services.scene_service import SceneService
from services.history_service import HistoryService

scene_bp = Blueprint("scene", __name__)
scene_service = SceneService()
history_service = HistoryService()

@scene_bp.route("/view")
def view():
    """场景管理页面"""
    return render_template("scenes.html")

@scene_bp.route("/list", methods=["GET"])
def list_scenes():
    """
    获取用户的场景列表
    这里我们复用历史记录中的 train_model_path 作为场景来源
    """
    username = request.args.get("username")
    if not username:
        return jsonify({"success": False, "msg": "未提供用户名"})
    
    # 从历史记录中获取成功的训练任务
    records = history_service.get_user_history(username)
    
    # 过滤出有模型路径的记录，并去重（如果有重复训练同一个场景）
    scenes = []
    seen_paths = set()
    
    for record in records:
        path = record.get('train_model_path')
        if path and path not in seen_paths:
            seen_paths.add(path)
            # 提取场景名
            scene_name = "Unknown"
            if path:
                import os
                scene_name = os.path.basename(path)
                
            scenes.append({
                "scene_name": scene_name,
                "model_path": path,
                "created_at": record.get("id"), # 简化处理，用ID代替时间
                "task_id": record.get("task_id")
            })
            
    return jsonify({"success": True, "data": scenes})

@scene_bp.route("/preview", methods=["POST"])
def preview():
    """启动场景预览"""
    data = request.json
    model_path = data.get("model_path")
    
    if not model_path:
        return jsonify({"success": False, "msg": "未提供模型路径"})
        
    success, msg = scene_service.preview_scene(model_path)
    
    return jsonify({
        "success": success,
        "msg": msg
    })
