#!/bin/bash
# scripts/push-to-ecr.sh
# Run this every time you want to deploy updated images

set -e   # exit on any error

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=eu-west-2
ECR_BASE=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "→ Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION \
    | docker login --username AWS --password-stdin $ECR_BASE

echo "→ Building images..."
docker build -t bookstore/app-service      ./app-service
docker build -t bookstore/catalogue-service ./catalogue-service

echo "→ Tagging images..."
docker tag bookstore/app-service       $ECR_BASE/bookstore/app-service:latest
docker tag bookstore/catalogue-service $ECR_BASE/bookstore/catalogue-service:latest

echo "→ Pushing images..."
docker push $ECR_BASE/bookstore/app-service:latest
docker push $ECR_BASE/bookstore/catalogue-service:latest

echo "✅ Both images pushed to ECR successfully"
echo "app-service URI:      $ECR_BASE/bookstore/app-service:latest"
echo "catalogue-service URI: $ECR_BASE/bookstore/catalogue-service:latest"
