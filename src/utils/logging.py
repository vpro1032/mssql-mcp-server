import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime
from src.utils.config import get_settings

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra_data"):
            log_obj.update(record.extra_data) # type: ignore
            
        return json.dumps(log_obj)

def setup_logging():
    settings = get_settings()
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)
    
    # Silence noisy libraries
    logging.getLogger("pydantic").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

