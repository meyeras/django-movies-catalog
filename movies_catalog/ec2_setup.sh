# Install Docker on Ubuntu

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

sudo docker run hello-world

#Install AWS CLI
sudo apt install curl unzip -y
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version





#Tag docker image
#docker buildx build --platform linux/amd64,linux/arm64 --network="host" --load -t <repository-name>:<tag> .
#docker tag <app>:<version> <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/<app>:<version>
#aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
#docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/<tagged-app>:<tagged-version>


#Inside the EC2 instance
#sudo usermod -aG docker $USER
#newgrp docker  # Apply group changes without logging out
#aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
#aws ecr describe-images --repository-name <repository-name> --region <your-region>
#docker pull <aws-account-id>.dkr.ecr.<your-region>.amazonaws.com/<repository-name>:<tag>

