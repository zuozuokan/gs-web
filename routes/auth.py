from flask import Blueprint, request, jsonify
from services.user_service import user_service

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """用户注册接口"""
    try:
        data = request.json
        
        # 基本参数检查
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"success": False, "msg": "缺少用户名或密码"}), 400
        
        username = data["username"].strip()
        password = data["password"].strip()
        
        if not username or not password:
            return jsonify({"success": False, "msg": "用户名和密码不能为空"}), 400
        
        # 可选参数：角色
        role = data.get("role", "user")
        if role not in ["admin", "user"]:
            role = "user"
        
        # 创建用户
        success, message = user_service.create_user(username, password, role)
        
        if success:
            return jsonify({
                "success": True,
                "msg": message,
                "data": {
                    "username": username,
                    "role": role
                }
            })
        else:
            return jsonify({"success": False, "msg": message}), 400
            
    except Exception as e:
        return jsonify({"success": False, "msg": f"注册失败: {str(e)}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """用户登录接口"""
    try:
        data = request.json
        
        # 基本参数检查
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"success": False, "msg": "缺少用户名或密码"}), 400
        
        username = data["username"].strip()
        password = data["password"].strip()
        
        if not username or not password:
            return jsonify({"success": False, "msg": "用户名和密码不能为空"}), 400
        
        # 验证用户
        success, message, user_info = user_service.verify_user(username, password)
        
        if success:
            return jsonify({
                "success": True,
                "msg": message,
                "data": user_info
            })
        else:
            return jsonify({"success": False, "msg": message}), 401
            
    except Exception as e:
        return jsonify({"success": False, "msg": f"登录失败: {str(e)}"}), 500

@auth_bp.route("/delete/<username>", methods=["DELETE"])
def delete_user(username):
    """删除用户接口（需要管理员权限）"""
    try:
        data = request.json
        
        # 检查管理员用户名
        if not data or 'admin_username' not in data:
            return jsonify({"success": False, "msg": "需要提供管理员用户名"}), 400
        
        admin_username = data["admin_username"].strip()
        
        if not admin_username:
            return jsonify({"success": False, "msg": "管理员用户名不能为空"}), 400
        
        # 执行删除
        success, message = user_service.delete_user(username, admin_username)
        
        if success:
            return jsonify({
                "success": True,
                "msg": message
            })
        else:
            return jsonify({"success": False, "msg": message}), 403  # 403 Forbidden
            
    except Exception as e:
        return jsonify({"success": False, "msg": f"删除失败: {str(e)}"}), 500
