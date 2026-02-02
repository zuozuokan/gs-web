class Config:
    SECRET_KEY = "gs_secret_key"
    OUTPUT_DIR = "static/output"
    
    # MySQL数据库配置
    DB_HOST = "115.191.43.249"
    DB_PORT = 3306
    DB_NAME = "gs_web"
    DB_USER = "gs_web"
    DB_PASSWORD = "admin"
    
    # 密码加密配置
    PASSWORD_HASH_METHOD = "pbkdf2:sha256"
    PASSWORD_SALT_LENGTH = 8
