# Gunicorn configuration for production
import os

# Binding - Cloud Run uses PORT env variable (default 8080)
# bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# for huggingface space
bind = f"0.0.0.0:{os.environ.get('PORT', '7860')}"

# Worker configuration
workers = 1  # Cloud Run - single worker for free tier
worker_class = "sync"
timeout = 200  # 3 minutes for AI operations (Gemini can be slow)
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
