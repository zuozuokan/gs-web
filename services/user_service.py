import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import logging

logger = logging.getLogger(__name__)

class UserService:
    """用户服务类，处理用户相关的数据库操作"""
    
    def __init__(self):
        self.config = Config()
        self.connection = None

    def _get_connection(self):
        """获取数据库连接"""
        try:
            if self.connection is None or not self.connection.open:
                self.connection = pymysql.connect(
                    host=self.config.DB_HOST,
                    port=self.config.DB_PORT,
                    user=self.config.DB_USER,
                    password=self.config.DB_PASSWORD,
                    database=self.config.DB_NAME,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
            return self.connection
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
            self.connection = None
    
    def create_user(self, username, password, role='user'):
        """创建新用户"""
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # 检查用户名是否已存在 
                sql = "SELECT id FROM `user` WHERE username = %s"
                cursor.execute(sql, (username,))
                if cursor.fetchone():
                    return False, "用户名已存在"
                
                # 加密密码
                hashed_password = generate_password_hash(
                    password,
                    method=self.config.PASSWORD_HASH_METHOD,
                    salt_length=self.config.PASSWORD_SALT_LENGTH
                )
                
                # 插入新用户
                sql = """
                    INSERT INTO `user` (username, password, role) 
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (username, hashed_password, role))
                connection.commit()
                
                return True, "用户创建成功"
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            connection.rollback()
            return False, f"创建用户失败: {str(e)}"
    
    def verify_user(self, username, password):
        """验证用户登录"""
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id, username, password, role FROM `user` WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                
                if not user:
                    return False, "用户名或密码错误", None
                
                # # 验证密码
                if check_password_hash(user['password'], password):
                    return True, "登录成功", {
                        'id': user['id'],
                        'username': user['username'],
                        'role': user['role']
                    }
                else:
                    return False, "用户名或密码错误", None
        except Exception as e:
            logger.error(f"验证用户失败: {e}")
            return False, f"验证失败: {str(e)}", None
    
    def delete_user(self, username, admin_username):
        """删除用户（需要管理员权限）"""
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # 检查操作者是否为管理员
                sql = "SELECT role FROM `user` WHERE username = %s"
                cursor.execute(sql, (admin_username,))
                admin_user = cursor.fetchone()
                
                if not admin_user or admin_user['role'] != 'admin':
                    return False, "权限不足，需要管理员权限"
                
                # 检查要删除的用户是否存在
                sql = "SELECT id FROM `user` WHERE username = %s"
                cursor.execute(sql, (username,))
                target_user = cursor.fetchone()
                
                if not target_user:
                    return False, "用户不存在"
                
                # 执行删除
                sql = "DELETE FROM `user` WHERE username = %s"
                cursor.execute(sql, (username,))
                connection.commit()
                
                return True, "用户删除成功"
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            connection.rollback()
            return False, f"删除用户失败: {str(e)}"
    
    def get_user_by_username(self, username):
        """根据用户名获取用户信息"""
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id, username, role FROM `user` WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                return user
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def get_user_stats(self):
        """获取用户统计信息"""
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # 获取总用户数
                sql = "SELECT COUNT(*) as total_users FROM `user`"
                cursor.execute(sql)
                total_users = cursor.fetchone()['total_users']
                
                # 获取管理员数量
                sql = "SELECT COUNT(*) as admin_users FROM `user` WHERE role = 'admin'"
                cursor.execute(sql)
                admin_users = cursor.fetchone()['admin_users']
                
                # 活跃会话数 - 由于我们使用sessionStorage，这里返回0
                # 在实际项目中，这里可以查询session表或redis等
                active_sessions = 0
                
                return {
                    'total_users': total_users,
                    'admin_users': admin_users,
                    'active_sessions': active_sessions
                }
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {e}")
            return None
    
    def get_users_list(self, page=1, page_size=10, search='', sort_by='id', sort_order='desc'):
        """获取用户列表（支持分页、搜索、排序）"""
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # 构建基础查询
                base_sql = "FROM `user` WHERE 1=1"
                params = []
                
                # 添加搜索条件
                if search:
                    base_sql += " AND username LIKE %s"
                    params.append(f"%{search}%")
                
                # 获取总数
                count_sql = f"SELECT COUNT(*) as total {base_sql}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['total']
                
                # 计算分页
                total_pages = (total + page_size - 1) // page_size  # 向上取整
                offset = (page - 1) * page_size
                
                # 验证排序字段，防止SQL注入
                valid_sort_fields = ['id', 'username', 'role']
                if sort_by not in valid_sort_fields:
                    sort_by = 'id'
                
                # 验证排序顺序
                sort_order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
                
                # 构建查询语句
                query_sql = f"""
                    SELECT id, username, role, created_at 
                    {base_sql} 
                    ORDER BY {sort_by} {sort_order}
                    LIMIT %s OFFSET %s
                """
                
                # 添加分页参数
                params.extend([page_size, offset])
                
                cursor.execute(query_sql, params)
                users = cursor.fetchall()
                
                # 格式化日期字段
                for user in users:
                    if user.get('created_at'):
                        user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                return {
                    'users': users,
                    'pagination': {
                        'total': total,
                        'current_page': page,
                        'total_pages': total_pages,
                        'page_size': page_size
                    }
                }
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return None
    
    def __del__(self):
        """析构函数，确保连接关闭"""
        self.close_connection()


# 创建全局用户服务实例
user_service = UserService()