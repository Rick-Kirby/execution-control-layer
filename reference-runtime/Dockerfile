FROM python:3.11-slim

WORKDIR /app

# Install deps first (cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy runtime
COPY . .

# Ensure imports work (scripts + app package)
ENV PYTHONPATH=/app

# Default audit path inside container (override at run time if you want)
ENV AUDIT_LOG_PATH=/app/logs/ecl_audit_{pid}.log
RUN mkdir -p /app/logs

EXPOSE 8000

# Single worker by default (scale with --workers at runtime if desired)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
