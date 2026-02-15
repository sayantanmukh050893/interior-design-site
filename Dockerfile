# Dockerfile for Interior Design Image Transformation API
# Supports both GPU and CPU deployments

FROM pytorch/pytorch:2.0-cuda11.8-runtime-ubuntu22.04

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    git \
    libopenjp2-7 \
    libtiff6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY image_service.py .
COPY styles.css .
COPY index.html .
COPY script.js .

# Create necessary directories
RUN mkdir -p prompt_history generated_images uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# For production, use gunicorn
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-"]
