#!/bin/sh

# AWS 설정
aws configure set aws_access_key_id "$DEV_AWS_ACCESS_KEY_ID"
aws configure set aws_secret_access_key "$DEV_AWS_SECRET_ACCESS_KEY"
aws configure set default.region "$DEV_AWS_REGION"

# 애플리케이션 시작
exec "$@"
