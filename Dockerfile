# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# aws-cli 설치
# weasyprint 라이브러리를 위한 설치
RUN apt-get update && \
    apt-get install -y \
    awscli \
#    libcairo2-dev \
#    libpango1.0-dev \
#    libgdk-pixbuf2.0-dev \
#    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \

# AWS CLI
RUN pip install awscli

ENV DEV_AWS_ACCESS_KEY_ID=${DEV_AWS_ACCESS_KEY_ID}
ENV DEV_AWS_SECRET_ACCESS_KEY=${DEV_AWS_SECRET_ACCESS_KEY}
ENV DEV_AWS_REGION=${DEV_AWS_REGION}

# Create and set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the application port
EXPOSE 8000

# Entrypoint 스크립트 복사
COPY entrypoint.sh /app/

# Entrypoint 스크립트 실행 권한 부여
RUN chmod +x /app/entrypoint.sh

# Entrypoint 설정
ENTRYPOINT ["/app/entrypoint.sh"]

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
