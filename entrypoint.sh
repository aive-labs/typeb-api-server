#!/bin/sh

# AWS 설정
aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
aws configure set default.region "$AWS_REGION"


# alembic 버전 적용
alembic upgrade head

# 애플리케이션 시작
exec "$@"
