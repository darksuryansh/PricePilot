# Gunicorn configuration for production
import os

# Binding
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Worker configuration
workers = 1  # Free tier - keep it light
worker_class = "sync"
timeout = 120  # 2 minutes for AI operations (Gemini can be slow)
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
