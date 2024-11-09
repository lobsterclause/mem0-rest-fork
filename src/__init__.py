"""
Mem0 REST API package.
"""
import os
import sys
import logging
import logging.config

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': sys.stdout,
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': os.path.join(project_root, 'logs', 'app.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'src': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
    }
})

# Create logs directory if it doesn't exist
logs_dir = os.path.join(project_root, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Create logger instance
logger = logging.getLogger(__name__)

__all__ = ["logger"]
