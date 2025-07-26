#!/bin/bash
set -eux

# Update system and install basic tools
apt-get update
apt-get install -y software-properties-common curl unzip gnupg lsb-release ca-certificates make git docker.io libpq-dev python3-dev

# Install Python 3.11
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Install pipenv
python3.11 -m pip install --break-system-packages pipenv==2025.0.4

systemctl enable docker
usermod -aG docker ubuntu

# Add ~/.local/bin to PATH for ubuntu user
echo 'export PATH=$HOME/.local/bin:$PATH' >> /home/ubuntu/.bashrc

curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip -q awscliv2.zip && ./aws/install && rm -rf aws awscliv2.zip
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose
