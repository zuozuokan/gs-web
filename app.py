from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json

from routes.train import train_bp

app = Flask(__name__)
app.config.from_object("config.Config")

CORS(app)

from routes.auth import auth_bp
from routes.scene import scene_bp
from routes.render import render_bp
from routes.user import user_bp
from routes.dataset import dataset_bp
from routes.metric import metric_bp
from routes.history import history_bp

# 历史记录
app.register_blueprint(history_bp, url_prefix="/api/history")



# 登录/注册
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# 把一段视频转化为可训练的数据集
app.register_blueprint(dataset_bp, url_prefix="/api/dataset")


app.register_blueprint(scene_bp, url_prefix="/api/scene")

# 渲染场景
app.register_blueprint(render_bp, url_prefix="/api/render")


app.register_blueprint(metric_bp, url_prefix="/api/metric")

# 训练
app.register_blueprint(train_bp, url_prefix="/api/train")

# 用户管理
app.register_blueprint(user_bp, url_prefix="/api/user")

# 前端页面路由

@app.route('/')
def index():
    """主页"""
    # 从sessionStorage获取用户信息（通过模板变量传递）
    # 实际项目中应该从session或token获取
    return render_template('index.html')

@app.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')

@app.route('/admin')
def admin_page():
    """用户管理页面"""
    return render_template('admin.html')

@app.route('/api/current-user', methods=['GET'])
def get_current_user():
    """获取当前用户信息（用于前端初始化）"""
    # 这里应该从session或token获取用户信息
    # 为了简化，我们从请求头或cookie获取
    # 实际项目中应该实现完整的认证机制
    return jsonify({
        'success': False,
        'msg': '请通过前端sessionStorage管理用户状态'
    })

# 下载模型文件接口
# 查看训练模型的历史记录
#
# 输入：视频-> 可训练的图片集

if __name__ == "__main__":
    app.run(debug=True,use_reloader=False, host='0.0.0.0', port=5000)
