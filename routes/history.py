from flask import Blueprint, render_template, request, jsonify, send_file, Response
from services.history_service import HistoryService
import os
import zipfile
import io
import time

history_bp = Blueprint("history", __name__)
history_service = HistoryService()

@history_bp.route("/view")
def view():
    """历史记录页面"""
    return render_template("history.html")

@history_bp.route("/list", methods=["GET"])
def list_history():
    """获取历史记录列表"""
    username = request.args.get("username")
    if not username:
        return jsonify({"success": False, "msg": "未提供用户名"})
    
    records = history_service.get_user_history(username)
    return jsonify({"success": True, "data": records})

@history_bp.route("/download/<type>/<task_id>", methods=["GET"])
def download(type, task_id):
    """下载文件或文件夹
    type: dataset | model | eval
    task_id: 任务ID
    """
    record = history_service.get_record_by_task_id(task_id)
    if not record:
        return "记录不存在", 404

    file_path = None
    download_name = f"{type}_{task_id}"
    
    if type == "dataset":
        file_path = record.get("dataset_path")
        download_name += ".zip"
    elif type == "model":
        file_path = record.get("train_model_path")
        download_name += ".zip"
    elif type == "eval":
        file_path = record.get("eval_output_path")
        download_name += ".md"
    else:
        return "无效的下载类型", 400

    if not file_path or not os.path.exists(file_path):
        return "文件或目录不存在", 404

    # 如果是目录，打包下载
    if os.path.isdir(file_path):
        try:
            zip_name = "dataset.zip" if type == "dataset" else "model.zip"
            zip_path = os.path.join(file_path, zip_name)
            if not os.path.exists(zip_path):
                with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_STORED) as zf:
                    for root, dirs, files in os.walk(file_path):
                        for file in files:
                            if file in ("dataset.zip", "model.zip"):
                                continue
                            file_abs_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_abs_path, file_path)
                            zf.write(file_abs_path, rel_path)
            return send_file(zip_path, as_attachment=True, download_name=download_name)
        except Exception as e:
            return f"打包失败: {str(e)}", 500
            
    # 如果是文件，直接下载
    else:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name
        )
