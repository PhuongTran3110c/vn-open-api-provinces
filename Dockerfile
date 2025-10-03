# Sử dụng Python 3.12 slim image để giảm kích thước
FROM python:3.12-slim

# Thiết lập working directory
WORKDIR /app

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Cài đặt system dependencies nếu cần
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml và uv.lock để cài dependencies
COPY pyproject.toml uv.lock* ./

# Cài đặt uv và dependencies
RUN pip install uv && \
    uv pip install --system -r pyproject.toml

# Copy toàn bộ source code
COPY api ./api
COPY README.rst .

# Tạo non-root user để chạy app (security best practice)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/ || exit 1

# Command để chạy application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
