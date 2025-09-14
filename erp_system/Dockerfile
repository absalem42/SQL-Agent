FROM python:slim-trixie

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install uv and use it to install requirements (using pre-compiled wheels)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system --no-cache-dir --only-binary=all -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and fix permissions
RUN mkdir -p databases logs && \
    chmod +x frontend/start_streamlit.sh && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV DB_PATH=/app/databases/erp.db

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "backend/api.py"]