import pymysql
import logging
from config import Config

logger = logging.getLogger(__name__)

class HistoryService:
    """训练历史记录服务类"""
    
    def __init__(self):
        self.config = Config()
        self.connection = None
        self._ensure_table_exists()

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

    def _ensure_table_exists(self):
        """确保history表存在"""
        sql = """
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
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()
        except Exception as e:
            logger.error(f"初始化history表失败: {e}")

    def add_train_record(self, username, task_id, dataset_path, train_model_path):
        """添加训练记录"""
        sql = """
        INSERT INTO `history` (username, task_id, dataset_path, train_model_path)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            dataset_path = VALUES(dataset_path),
            train_model_path = VALUES(train_model_path)
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, (username, task_id, dataset_path, train_model_path))
            connection.commit()
            logger.info(f"添加训练历史记录成功: task_id={task_id}")
            return True
        except Exception as e:
            logger.error(f"添加训练历史记录失败: {e}")
            return False

    def update_eval_record(self, train_model_path, eval_output_path):
        """更新评估结果路径"""
        # 根据 train_model_path 查找并更新
        sql = """
        UPDATE `history` 
        SET eval_output_path = %s 
        WHERE train_model_path = %s
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                result = cursor.execute(sql, (eval_output_path, train_model_path))
                if result == 0:
                    logger.warning(f"未找到对应的训练记录，无法更新评估路径: {train_model_path}")
            connection.commit()
            logger.info(f"更新评估记录成功: {train_model_path}")
            return True
        except Exception as e:
            logger.error(f"更新评估记录失败: {e}")
            return False

    def get_user_history(self, username):
        """获取用户的训练历史记录"""
        sql = """
        SELECT * FROM `history` 
        WHERE username = %s 
        ORDER BY id DESC
        """
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, (username,))
                results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"获取用户历史记录失败: {e}")
            return []

    def get_record_by_task_id(self, task_id):
        """根据task_id获取记录"""
        sql = "SELECT * FROM `history` WHERE task_id = %s"
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, (task_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"获取历史记录失败: {e}")
            return None

    def get_record_by_model_path(self, model_path):
        """根据模型路径获取记录"""
        sql = "SELECT * FROM `history` WHERE train_model_path = %s"
        try:
            connection = self._get_connection()
            with connection.cursor() as cursor:
                cursor.execute(sql, (model_path,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"获取历史记录失败: {e}")
            return None
