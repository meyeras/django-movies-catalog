#!/bin/bash
# -----------------------------------------------------------------------------
# Script Name: ecr_pull.sh
#
# Description:
#   This script logs in to AWS ECR and pulls a specified Docker image.
#
# Prerequisites:
#   - AWS CLI must be installed and configured.
#   - Docker must be installed.
#
# Required Environment Variables:
#   AWS_ACCOUNT_ID       - Your AWS account ID.
#   ECR_REPOSITORY_NAME  - The name of your ECR repository.
#   ECR_IMAGE_TAG        - The Docker image tag to pull.
#
# Usage:
#   Option A: Use pre-set environment variables:
#       export AWS_ACCOUNT_ID=your_account_id
#       export ECR_REPOSITORY_NAME=your_repository_name
#       export ECR_IMAGE_TAG=your_image_tag
#       ./ecr_pull.sh
#
#   Option B: Let the script prompt you for any missing values:
#       ./ecr_pull.sh
#
# -----------------------------------------------------------------------------

set -e  # Exit immediately if a command exits with a non-zero status

# Function to prompt for a variable if it is not already set
prompt_if_empty() {
  local var_name="$1"
  local prompt_message="$2"
  if [ -z "${!var_name}" ]; then
    read -p "$prompt_message: " value
    export "$var_name"="$value"
  fi
}

# Prompt for missing environment variables
prompt_if_empty "AWS_ACCOUNT_ID" "Enter AWS Account ID"
prompt_if_empty "ECR_REPOSITORY_NAME" "Enter ECR Repository Name"
prompt_if_empty "ECR_IMAGE_TAG" "Enter ECR Image Tag"

echo "Using the following settings:"
echo "  AWS_ACCOUNT_ID      : $AWS_ACCOUNT_ID"
echo "  ECR_REPOSITORY_NAME : $ECR_REPOSITORY_NAME"
echo "  ECR_IMAGE_TAG       : $ECR_IMAGE_TAG"

# Log in to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com"

# Pull the Docker image from AWS ECR
docker pull "${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG}"
