import logging
import json
from config import settings
from utils.redaction import redact_log_data

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        
        if hasattr(record, "structured_data"):
             log_obj.update(redact_log_data(record.structured_data))
             
        return json.dumps(log_obj)

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File Handler
    log_file = settings.LOGS_DIR / "app.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger

logger = get_logger("rag_poc")
