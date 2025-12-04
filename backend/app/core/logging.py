"""
Structured logging configuration for the application.
Provides JSON logging for production and human-readable logs for development.
"""
import logging
import sys
from datetime import datetime
from typing import Optional
import json
from pythonjsonlogger import jsonlogger
from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add environment
        log_record['environment'] = settings.ENVIRONMENT
        
        # Add service name
        log_record['service'] = 'contract-agent-api'
        
        # Move message to proper field
        if 'message' not in log_record:
            log_record['message'] = record.getMessage()


def setup_logging():
    """Configure logging for the application."""
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Choose formatter based on environment
    if settings.ENVIRONMENT == 'production':
        # Use JSON formatter in production
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        # Use human-readable format in development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


class RequestLogger:
    """Logger for HTTP requests with context."""
    
    def __init__(self):
        self.logger = get_logger('api.requests')
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Log an HTTP request."""
        log_data = {
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': round(duration_ms, 2),
            'user_id': user_id,
            'request_id': request_id,
            'client_ip': client_ip
        }
        
        if error:
            log_data['error'] = error
            self.logger.error('Request failed', extra=log_data)
        elif status_code >= 400:
            self.logger.warning('Request error', extra=log_data)
        else:
            self.logger.info('Request completed', extra=log_data)


class AuditLogger:
    """Logger for audit events."""
    
    def __init__(self):
        self.logger = get_logger('audit')
    
    def log_event(
        self,
        action: str,
        user_id: Optional[str],
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        success: bool = True
    ):
        """Log an audit event."""
        log_data = {
            'action': action,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {},
            'success': success
        }
        
        if success:
            self.logger.info(f'Audit: {action}', extra=log_data)
        else:
            self.logger.warning(f'Audit: {action} (failed)', extra=log_data)


# Initialize logging on module import
setup_logging()

# Create global logger instances
request_logger = RequestLogger()
audit_logger = AuditLogger()
