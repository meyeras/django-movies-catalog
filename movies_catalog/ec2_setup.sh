#!/bin/bash

set -e
trap 'echo "Error on line $LINENO"; exit 1' ERR

echo "Starting EC2 setup: Installing AWS CLI, Docker, and configuring user permissions."

# Install AWS CLI
sudo apt update
sudo apt install -y curl unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --update
rm -rf awscliv2.zip aws
export PATH=$PATH:/usr/local/bin
aws --version || { echo "AWS CLI installation failed"; exit 1; }

# Install Docker
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo docker run hello-world

# Add user to the docker group
if groups $USER | grep &>/dev/null "\bdocker\b"; then
    echo "User '$USER' is already in the 'docker' group. Proceeding..."
else
    sudo usermod -aG docker $USER
    echo "**************************************************************************"
    echo "Docker has been installed, and the user '$USER' has been added to the docker group."
    echo
    echo "To apply these changes, you need to start a new session with the updated permissions."
    echo
    echo "Since you're using the EC2 browser shell, you don't need to log out and log back in."
    echo "Instead, run the following command in your terminal:"
    echo
    echo "   newgrp docker"
    echo
    echo "This will open a new shell session where you can run Docker without sudo."
    echo
    echo "Once you've done that, proceed by running the second script:"
    echo
    echo "   ./ecr_pull.sh"
    echo "**************************************************************************"
    exit 0  # Stop execution here until the user runs newgrp docker
fi

echo "Setup complete! Now run 'newgrp docker' in your terminal, then execute './ecr_pull.sh' to continue."
