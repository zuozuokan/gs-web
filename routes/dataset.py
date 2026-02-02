# routes/dataset.py
from flask import Blueprint, request, jsonify
from services.dataset_service import dataset_service
import os
import uuid
import shutil
from werkzeug.utils import secure_filename

dataset_bp = Blueprint("dataset", __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'mp4', 'MP4'}
# 最大文件大小：3GB
MAX_CONTENT_LENGTH = 3 * 1024 * 1024 * 1024

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dataset_bp.route("/upload_video", methods=["POST"])
def upload_video():
    """
    上传视频文件（第一步：只上传文件）
    请求参数：
    - file: 视频文件
    - username: 用户名（从请求头或表单获取）
    """
    try:
        # 检查是否有文件在请求中
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "msg": "没有选择文件"
            }), 400
        
        file = request.files['file']
        
        # 如果用户没有选择文件，浏览器会提交一个空文件
        if file.filename == '':
            return jsonify({
                "success": False,
                "msg": "没有选择文件"
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "msg": "只支持MP4格式的视频文件"
            }), 400
        
        # 获取用户名（从前端传递）
        username = request.form.get('username')
        if not username:
            return jsonify({
                "success": False,
                "msg": "需要提供用户名"
            }), 400
        
        # 生成唯一的task_id
        task_id = str(uuid.uuid4())[:8]  # 取前8位作为简化的task_id
        
        # 创建目录结构
        user_dir = os.path.join("user", username)
        dataset_dir = os.path.join(user_dir, "dataset")
        task_dir = os.path.join(dataset_dir, task_id)
        
        # 确保目录存在
        os.makedirs(task_dir, exist_ok=True)
        
        # 安全地保存文件名
        filename = secure_filename(file.filename)
        # 确保文件扩展名是.mp4
        if not filename.lower().endswith('.mp4'):
            filename = f"{filename}.mp4"
        
        # 完整的文件路径
        file_path = os.path.join(task_dir, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 验证文件是否保存成功
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "msg": "文件保存失败"
            }), 500
        
        # 返回文件信息（不调用create_from_video）
        # 注意：这里使用相对路径，前端调用create_from_video时需要正确的路径
        video_path = f"./user/{username}/dataset/{task_id}/{filename}"
        
        return jsonify({
            "success": True,
            "msg": "视频上传成功",
            "data": {
                "username": username,
                "task_id": task_id,
                "filename": filename,
                "video_path": video_path,
                "full_path": file_path,
                "message": "文件上传成功，请点击'生成数据集'按钮开始创建数据集"
            }
        })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"上传失败: {str(e)}"
        }), 500

@dataset_bp.route("/create_from_video", methods=["POST"])

def create_dataset_from_video():
    """
    用户输入视频路径，生成数据集
    """
    data = request.json

    if not data or "video_path" not in data:
        return jsonify({
            "success": False,
            "msg": "缺少视频路径"
        }), 400

    video_path = data["video_path"].strip()

    if not video_path:
        return jsonify({
            "success": False,
            "msg": "视频路径不能为空"
        }), 400

    success, msg = dataset_service.create_from_video(video_path)

    if success:
        return jsonify({
            "success": True,
            "msg": msg
        })
    else:
        return jsonify({
            "success": False,
            "msg": msg
        }), 500
