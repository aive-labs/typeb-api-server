# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# AWS CLI 설치
RUN apt-get update && \
    apt-get install -y awscli && \
    rm -rf /var/lib/apt/lists/* \

# AWS CLI
RUN pip install awscli

ENV DEV_AWS_ACCESS_KEY_ID=${DEV_AWS_ACCESS_KEY_ID}
ENV DEV_AWS_SECRET_ACCESS_KEY=${DEV_AWS_SECRET_ACCESS_KEY}
ENV DEV_AWS_REGION=${DEV_AWS_REGION}

# AWS 설정
RUN aws configure set aws_access_key_id "$DEV_AWS_ACCESS_KEY_ID" && \
    aws configure set aws_secret_access_key "$DEV_AWS_SECRET_ACCESS_KEY" && \
    aws configure set default.region "$DEV_AWS_REGION"

# Create and set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
