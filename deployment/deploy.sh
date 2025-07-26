KEY_PATH=${1}
TAG_NAME=ec2-mlops
USER=ubuntu

chmod 600 $KEY_PATH

DNS=$(aws ec2 describe-instances \
  --filters "Name=tag:name,Values=$TAG_NAME" "Name=instance-state-name,Values=running" \
  --query "Reservations[0].Instances[0].PublicDnsName" \
  --output text)

ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no $USER@$DNS << 'EOF'
set -e
REPO_DIR="weather-forecast-mlops"
REPO_URL="https://github.com/sndryn/weather-forecast-mlops.git"
BRANCH="master"

if [ ! -d "$REPO_DIR" ]; then
  echo "Cloning repo..."
  git clone "$REPO_URL"
fi

cd "$REPO_DIR"

echo "Fetching latest updates..."
git fetch origin

echo "Checking out branch $BRANCH..."
git checkout "$BRANCH"

echo "Pulling latest changes..."
git pull origin "$BRANCH"

echo "Building and running..."

make generate_env
make build_and_run
EOF
