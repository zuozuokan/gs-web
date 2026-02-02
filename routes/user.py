from flask import Blueprint, request, jsonify
from services.user_service import user_service

user_bp = Blueprint("user", __name__)

@user_bp.route("/stats", methods=["GET"])
def get_user_stats():
    """获取用户统计信息接口"""
    try:
        # 获取统计信息
        stats = user_service.get_user_stats()
        
        if stats is None:
            return jsonify({
                "success": False,
                "msg": "获取统计信息失败"
            }), 500
        
        return jsonify({
            "success": True,
            "data": stats
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"获取统计信息失败: {str(e)}"
        }), 500

@user_bp.route("/list", methods=["GET"])
def get_users_list():
    """获取用户列表接口（支持分页、搜索、排序）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        search = request.args.get('search', '', type=str)
        sort_by = request.args.get('sort_by', 'id', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)
        
        # 验证参数
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:  # 限制每页最多100条
            page_size = 10
        
        # 获取用户列表
        result = user_service.get_users_list(
            page=page,
            page_size=page_size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        if result is None:
            return jsonify({
                "success": False,
                "msg": "获取用户列表失败"
            }), 500
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "msg": f"获取用户列表失败: {str(e)}"
        }), 500