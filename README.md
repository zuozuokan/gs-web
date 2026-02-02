# 3DGS训练系统Web界面

## 概述

基于Flask的3D高斯泼溅（3D Gaussian Splatting）训练系统Web界面，提供完整的视频处理、数据集生成、3D模型训练、渲染和评估功能。系统集成了外部3DGS项目，提供用户友好的Web界面来管理整个训练流程。

### 核心功能
- **用户认证系统**：注册、登录、管理员管理
- **视频数据集生成**：MP4视频上传 → 自动抽帧 → 转换为3DGS训练格式
- **3DGS训练**：调用外部3DGS项目进行3D高斯泼溅训练
- **场景渲染**：训练后模型的渲染和可视化
- **质量评估**：PSNR、SSIM、LPIPS指标计算
- **历史管理**：训练记录追踪和文件下载
- **场景管理**：已训练场景的预览和管理

### 技术栈
- **后端**：Python Flask, MySQL, PyMySQL
- **前端**：HTML5, CSS3, JavaScript, Bootstrap 5
- **数据处理**：FFmpeg, COLMAP
- **3D核心**：Improving-ADC-3DGS项目
- **可视化**：SIBR Viewer

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Web前端 (Templates)                      │
│  index.html ── login.html ── register.html ── admin.html    │
└──────────────────────────────────┬──────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────┐
│                    Flask后端 (app.py)                         │
│    ┌─────────────┬─────────────┬──────────────────┐        │
│    │ 路由层      │  服务层     │   数据库/外部调用  │        │
│    │ routes/     │ services/   │  MySQL + 3DGS    │        │
│    └─────┬───────┴──────┬──────┴─────────┬────────┘        │
│          │              │                │                  │
│    HTTP请求处理        业务逻辑          数据持久化/计算      │
└──────────┼──────────────┼────────────────┼──────────────────┘
           │              │                │
┌──────────▼──────────────▼────────────────▼──────────────────┐
│                 数据存储与外部依赖                            │
│   MySQL数据库  +  用户数据目录  +  外部3DGS项目              │
└─────────────────────────────────────────────────────────────┘
```

### 数据流向
1. **用户上传视频** → 保存到`user/{username}/dataset/{task_id}/`
2. **生成数据集** → 调用FFmpeg抽帧 → 调用convert.py处理
3. **启动训练** → 调用train.py → 模型保存到`user/{username}/models/{scene_name}/`
4. **渲染评估** → 调用render.py + evaluate.py → 生成指标报告
5. **记录历史** → 保存到MySQL数据库

---

## 项目结构

```
gs_web/
├── app.py                    # Flask主应用入口
├── config.py                 # 配置文件（数据库、密钥等）
├── routes/                   # API路由模块
│   ├── auth.py              # 用户认证接口（注册、登录、删除用户）
│   ├── dataset.py           # 数据集管理接口（视频上传、数据集生成）
│   ├── train.py             # 训练控制接口（启动训练、状态查询）
│   ├── render.py            # 渲染控制接口（启动渲染、状态查询）
│   ├── metric.py            # 评估指标接口（PSNR、SSIM、LPIPS计算）
│   ├── scene.py             # 场景管理接口（场景列表、预览）
│   ├── history.py           # 历史记录接口（历史列表、文件下载）
│   └── user.py              # 用户管理接口（用户统计、列表查询）
├── services/                 # 业务逻辑层
│   ├── dataset_service.py   # 数据集生成服务（调用FFmpeg和convert.py）
│   ├── train_service.py     # 训练执行服务（调用train.py和SIBR viewer）
│   ├── render_service.py    # 渲染执行服务（调用render.py）
│   ├── metric_service.py    # 评估计算服务（调用evaluate.py）
│   ├── scene_service.py     # 场景预览服务（启动SIBR viewer）
│   ├── history_service.py   # 历史记录服务（数据库操作）
│   └── user_service.py      # 用户管理服务（用户CRUD操作）
├── templates/               # 前端HTML模板
│   ├── base.html           # 基础模板（导航栏、公共样式）
│   ├── index.html          # 主页（功能入口、状态显示）
│   ├── login.html          # 登录页
│   ├── register.html       # 注册页
│   ├── admin.html          # 管理员页（用户管理）
│   ├── history.html        # 历史记录页
│   └── scenes.html         # 场景管理页
├── tasks/                   # 任务管理模块
│   └── task_store.py       # 任务状态存储（内存存储，简化实现）
├── sql/                    # 数据库脚本
├── user/                   # 用户数据存储目录（运行时动态生成）
│   └── {username}/         # 用户专属目录
│       ├── dataset/        # 数据集存储
│       │   └── {task_id}/  # 任务专属数据集
│       │       ├── input/  # 抽帧图片
│       │       ├── images/ # 处理后的图片
│       │       ├── sparse/ # COLMAP稀疏重建
│       │       └── *.mp4   # 原始视频文件
│       └── models/         # 训练模型存储
│           └── {scene_name}/ # 场景专属模型
│               ├── cameras.json
│               ├── params/
│               ├── point_cloud/
│               └── metrics.md
└── README.md               # 项目说明文档
```

---

## 部署指南（Windows环境）

### 环境要求

#### 必需软件
1. **Python 3.8+**：建议使用Anaconda环境管理
2. **MySQL 8.0+**：数据库服务
3. **FFmpeg**：视频处理工具
4. **Git**：代码版本控制

#### 外部依赖项目
1. **Improving-ADC-3DGS**：3D高斯泼溅核心算法
2. **SIBR Viewer**：3D场景可视化工具

### 步骤1：克隆项目
```bash
git clone https://github.com/zuozuokan/gs-web.git
cd gs-web
```

### 步骤2：Python环境配置
```bash
# 创建并激活Python环境（推荐使用Anaconda）
conda create -n gs_web python=3.8
conda activate gs_web

# 安装Python依赖
pip install -r requirements.txt
```

如果缺少requirements.txt，手动安装：
```bash
pip install flask flask-cors pymysql werkzeug
```

### 步骤3：数据库配置
1. **安装MySQL 8.0+**并启动服务
2. **创建数据库和用户**：
```sql
CREATE DATABASE gs_web CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gs_web'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON gs_web.* TO 'gs_web'@'%';
FLUSH PRIVILEGES;
```

3. **创建用户表**：
```sql
CREATE TABLE `user` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '用户ID，自增主键',
  `username` VARCHAR(20) NOT NULL COMMENT '用户名',
  `password` VARCHAR(100) NOT NULL COMMENT '密码（加密后的）',
  `role` VARCHAR(10) NOT NULL COMMENT '用户角色，如 admin / user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

4. **创建历史记录表**（可选，首次运行会自动创建）：
```sql
CREATE TABLE if not exists `history` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '记录ID，自增主键',
  `username` VARCHAR(20) NOT NULL COMMENT '用户名（关联 user.username）',
  `task_id` VARCHAR(20) NOT NULL COMMENT '训练任务ID',
  `dataset_path` VARCHAR(100) DEFAULT NULL COMMENT '数据集路径',
  `2d_outputs_path` VARCHAR(100) DEFAULT NULL COMMENT '2D 输出路径',
  `eval_output_path` VARCHAR(100) DEFAULT NULL COMMENT '评估结果路径',
  `train_model_path` VARCHAR(100) DEFAULT NULL COMMENT '训练模型输出路径',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_task_id` (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='训练历史记录表';
```

### 步骤4：外部依赖安装（关键步骤）

#### 4.1 安装Improving-ADC-3DGS
```bash
# 克隆Improving-ADC-3DGS项目
git clone https://github.com/your-org/Improving-ADC-3DGS.git "G:\xf\Improving-ADC-3DGS"

# 安装其依赖（根据原项目README）
cd "G:\xf\Improving-ADC-3DGS"
# 按照原项目说明安装依赖
```

#### 4.2 配置特定Python环境
系统需要访问特定的Python环境来运行3DGS代码：
```bash
# 创建专用环境
conda create -n improving_3dgs python=3.8
conda activate improving_3dgs

# 安装3DGS所需依赖（根据Improving-ADC-3DGS要求）
pip install torch torchvision torchaudio
# 安装其他3DGS依赖...
```

#### 4.3 安装SIBR Viewer
确保SIBR Viewer可执行文件位于：
```
G:\xf\Improving-ADC-3DGS\viewers\bin\
```
包含以下文件：
- `SIBR_gaussianViewer_app.exe`
- `SIBR_remoteGaussian_app.exe`

### 步骤5：路径配置（重要！）

本系统包含多个硬编码路径，部署时必须修改以下文件：

#### 5.1 修改服务文件中的路径
需要修改`services/`目录下的文件：

**services/dataset_service.py**：
```python
# 修改为你的实际路径
GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"  # 3DGS Python环境
GS_ROOT = r"G:\xf\Improving-ADC-3DGS"  # 3DGS项目根目录
```

**services/train_service.py**：
```python
# 修改为你的实际路径
GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"
GS_ROOT = r"G:\xf\gs_web\user"  # 用户数据存储根目录
GS_CODE_ROOT = r"G:\xf\Improving-ADC-3DGS"  # 3DGS代码目录
GS_VIEWER = r"G:\xf\Improving-ADC-3DGS\viewers\bin\SIBR_remoteGaussian_app.exe"
```

**services/render_service.py**：
```python
GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"
GS_ROOT = r"G:\xf\Improving-ADC-3DGS"
```

**services/metric_service.py**：
```python
GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"
GS_ROOT = r"G:\xf\Improving-ADC-3DGS"
```

**services/scene_service.py**：
```python
GS_VIEWER = r"G:\xf\Improving-ADC-3DGS\viewers\bin\SIBR_gaussianViewer_app.exe"
GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"
GS_ROOT = r"G:\xf\Improving-ADC-3DGS"
```

#### 5.2 修改配置文件
**config.py**：
```python
class Config:
    SECRET_KEY = "your_secret_key_here"  # 修改为强密钥
    OUTPUT_DIR = "static/output"
    
    # MySQL数据库配置（根据实际修改）
    DB_HOST = "115.191.43.249"  # 数据库服务器地址
    DB_PORT = 3306
    DB_NAME = "gs_web"
    DB_USER = "gs_web"
    DB_PASSWORD = "admin"  # 修改为安全密码
    
    # 密码加密配置
    PASSWORD_HASH_METHOD = "pbkdf2:sha256"
    PASSWORD_SALT_LENGTH = 8
```

#### 5.3 路径映射表
| 变量名 | 默认路径 | 说明 | 必须修改 |
|--------|----------|------|----------|
| `GS_PYTHON` | `D:\Anaconda\envs\improving_3dgs\python.exe` | 3DGS专用Python环境 | 是 |
| `GS_ROOT` | `G:\xf\Improving-ADC-3DGS` | 3DGS项目根目录 | 是 |
| `GS_CODE_ROOT` | `G:\xf\Improving-ADC-3DGS` | 3DGS代码目录 | 是 |
| `GS_VIEWER` | `G:\xf\Improving-ADC-3DGS\viewers\bin\*.exe` | SIBR查看器路径 | 是 |
| `GS_ROOT` (train_service) | `G:\xf\gs_web\user` | 用户数据存储目录 | 根据部署位置修改 |
| `DB_HOST` | `115.191.43.249` | MySQL服务器地址 | 根据数据库位置修改 |

### 步骤6：运行应用
```bash
# 激活Python环境
conda activate gs_web

# 启动Flask应用
python app.py

# 或直接运行（调试模式）
python app.py --debug
```

应用将在`http://localhost:5000`启动。

### 步骤7：创建第一个管理员用户
访问`http://localhost:5000/register`，使用以下信息注册：
- 用户名：admin
- 密码：自定义安全密码
- 角色：选择"管理员"

或通过API创建：
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password","role":"admin"}'
```

---

## 配置说明

### 环境变量配置（可选）
可以创建`.env`文件或设置系统环境变量：
```
FLASK_SECRET_KEY=your_secret_key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gs_web
DB_USER=gs_web
DB_PASSWORD=your_db_password
```

然后在`config.py`中读取：
```python
import os
class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'gs_secret_key')
    DB_HOST = os.getenv('DB_HOST', '115.191.43.249')
    # ... 其他配置
```

### 文件存储配置
- **用户数据**：默认存储在`user/`目录，按用户名和任务ID组织
- **最大文件大小**：视频上传限制为3GB
- **支持格式**：目前仅支持MP4视频格式

---

## 使用指南

### 1. 用户注册与登录
1. 访问`http://localhost:5000/register`注册新账户
2. 注册后访问`http://localhost:5000/login`登录
3. 管理员可以访问`http://localhost:5000/admin`管理用户

### 2. 视频上传与数据集生成
1. 登录后进入主页
2. 在"创建训练数据集"卡片中选择MP4视频文件
3. 点击"上传视频"按钮
4. 上传成功后点击"生成数据集"按钮
5. 等待数据集生成完成（可能需要几分钟）

### 3. 3DGS训练流程
1. 确保数据集已生成成功
2. 在"3DGS训练"卡片中输入场景名称
3. 点击"开始训练"按钮
4. 系统将自动启动训练和SIBR viewer
5. 可以在浏览器中查看训练状态

### 4. 渲染与评估
1. 训练完成后，在"场景渲染"卡片中输入相同的场景名称
2. 点击"开始渲染"按钮
3. 系统将执行渲染并自动进行质量评估
4. 查看弹出的评估报告（PSNR、SSIM、LPIPS指标）

### 5. 历史记录与下载
1. 点击"查看历史"进入历史记录页面
2. 查看所有训练任务的记录
3. 可以下载数据集、模型文件和评估报告

### 6. 场景管理
1. 点击"查看场景"进入场景管理页面
2. 查看所有已训练的场景
3. 点击"预览场景"启动SIBR viewer查看3D场景

---

## API接口概览

### 用户认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `DELETE /api/auth/delete/<username>` - 删除用户（管理员）

### 数据集管理
- `POST /api/dataset/upload_video` - 上传视频文件
- `POST /api/dataset/create_from_video` - 从视频生成数据集

### 训练控制
- `POST /api/train/start` - 启动训练任务
- `GET /api/train/status/<task_id>` - 查询训练状态

### 渲染控制
- `POST /api/render/start` - 启动渲染任务
- `GET /api/render/status/<task_id>` - 查询渲染状态

### 评估指标
- `POST /api/metric/evaluate` - 计算模型评估指标

### 场景管理
- `GET /api/scene/list` - 获取用户场景列表
- `POST /api/scene/preview` - 预览场景

### 历史记录
- `GET /api/history/list` - 获取用户历史记录
- `GET /api/history/download/<type>/<task_id>` - 下载文件

### 用户管理
- `GET /api/user/stats` - 获取用户统计信息
- `GET /api/user/list` - 获取用户列表（分页、搜索、排序）

---

## 常见问题与故障排除

### 1. 数据库连接失败
**症状**：应用启动时报数据库连接错误
**解决方案**：
- 确认MySQL服务正在运行
- 检查`config.py`中的数据库配置
- 验证用户名和密码是否正确
- 确保数据库用户有远程连接权限（如需要）

### 2. 3DGS执行失败
**症状**：训练或渲染时报"python.exe找不到"或"路径不存在"
**解决方案**：
- 确认所有`services/*.py`文件中的路径已正确修改
- 检查`D:\Anaconda\envs\improving_3dgs\python.exe`是否存在
- 确认`G:\xf\Improving-ADC-3DGS`目录存在且包含必要文件

### 3. 视频上传失败
**症状**：上传大文件时报错或进度卡住
**解决方案**：
- 检查Flask的`MAX_CONTENT_LENGTH`设置（默认3GB）
- 确认服务器有足够磁盘空间
- 检查文件权限

### 4. SIBR Viewer无法启动
**症状**：场景预览时无反应
**解决方案**：
- 确认`SIBR_gaussianViewer_app.exe`路径正确
- 检查Windows防火墙是否阻止了应用
- 确保系统有图形界面（SIBR需要显示窗口）

### 5. 路径包含中文或空格
**症状**：各种文件操作失败
**解决方案**：
- 确保所有路径不包含中文或特殊字符
- 使用英文路径和文件名
- 避免路径中有空格

### 6. 内存不足
**症状**：处理大视频或复杂场景时崩溃
**解决方案**：
- 增加系统虚拟内存
- 使用较小的视频分辨率
- 减少训练迭代次数（修改`train_service.py`中的参数）

---

## 开发说明

### 扩展功能建议
1. **JWT认证**：替换当前sessionStorage认证
2. **任务队列**：使用Celery处理长时间任务
3. **进度反馈**：实时训练进度显示
4. **多用户并发**：改进资源管理和隔离
5. **Docker部署**：简化环境配置

### 代码规范
- 遵循PEP 8 Python代码规范
- 服务层负责业务逻辑，路由层负责HTTP处理
- 使用类型提示提高代码可读性

### 安全注意事项
1. 生产环境务必修改`SECRET_KEY`
2. 数据库密码不要使用默认值
3. 考虑添加HTTPS支持
4. 实施输入验证和防SQL注入

---

## 许可证与版权

本项目为闭源项目，仅供授权使用。未经许可，不得复制、修改或分发。

---

## 更新日志

### v1.0 (当前版本)
- 完整的用户认证系统
- 视频上传和数据集生成
- 3DGS训练集成
- 场景渲染和评估
- 历史记录管理
- Web界面管理

---

**注意**：本系统包含多个硬编码路径，部署时务必根据实际环境修改`services/`目录下的路径配置。如有问题，请参考"路径配置"章节。