import logging
from pythonjsonlogger import jsonlogger
from app.core.config import settings

def setup_logger():
    """配置日志记录器"""
    logger = logging.getLogger()
    
    # 设置日志级别
    logger.setLevel(logging.INFO)
    
    # 创建JSON格式的日志处理器
    json_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    json_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(json_handler)
    
    # 添加文件处理器
    log_file = settings.DATA_DIR / "debug.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()