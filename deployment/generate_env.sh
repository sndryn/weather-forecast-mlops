#!/bin/bash

INI_FILE="deployment/ssm-config.ini"
ENV_FILE=".env"

MLOPS_DB_INSTANCE_NAME=""

> "$ENV_FILE"


while IFS='=' read -r key ssm_path; do
    [[ "$key" =~ ^#.*$ || -z "$key" || -z "$ssm_path" ]] && continue

    key=$(echo "$key" | xargs)
    ssm_path=$(echo "$ssm_path" | xargs)

    value=$(aws ssm get-parameter --name "$ssm_path" \
        --with-decryption --query "Parameter.Value" \
        --output text 2>/dev/null)

    echo "$key=$value" >> "$ENV_FILE"

    if [[ "$key" == "MLOPS_DB_INSTANCE_NAME" ]]; then
        MLOPS_DB_INSTANCE_NAME="$value"
    fi

done < "$INI_FILE"

MLOPS_DB_HOSTNAME=$(aws rds describe-db-instances \
    --db-instance-identifier "$MLOPS_DB_INSTANCE_NAME" \
    --query "DBInstances[0].Endpoint.Address" \
    --output text 2>/dev/null)

echo "MLOPS_DB_HOSTNAME=$MLOPS_DB_HOSTNAME" >> "$ENV_FILE"

CFG="$HOME/.aws/config"
CREDS="$HOME/.aws/credentials"

AWS_DEFAULT_REGION=$(grep -m1 '^region' "$CFG" 2>/dev/null | cut -d '=' -f2 | xargs)
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-ap-southeast-1}
AWS_ACCESS_KEY_ID=$(awk -F '=' '/^\[default\]/{f=1} f==1 && /aws_access_key_id/{print $2; exit}' "$CREDS" 2>/dev/null | xargs)
AWS_SECRET_ACCESS_KEY=$(awk -F '=' '/^\[default\]/{f=1} f==1 && /aws_secret_access_key/{print $2; exit}' "$CREDS" 2>/dev/null | xargs)

# Append if found
[[ -n $AWS_DEFAULT_REGION ]] && echo "AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION" >> "$ENV_FILE"
[[ -n $AWS_ACCESS_KEY_ID ]] && echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" >> "$ENV_FILE"
[[ -n $AWS_SECRET_ACCESS_KEY ]] && echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> "$ENV_FILE"
