#!/bin/bash

# Detect OS Type
if [[ -f /etc/debian_version ]]; then
    OS="debian"
elif [[ -f /etc/redhat-release ]]; then
    OS="rhel"
else
    echo "Unsupported OS. Exiting."
    exit 1
fi

# Function to Install Docker
install_docker() {
    echo "Installing Docker..."

    if [[ $OS == "debian" ]]; then
        sudo apt update
        sudo apt install -y ca-certificates curl gnupg

        # Add Docker’s official GPG key
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg | sudo tee /etc/apt/keyrings/docker.gpg > /dev/null
        sudo chmod a+r /etc/apt/keyrings/docker.gpg

        # Add the repository
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(. /etc/os-release && echo "$ID") $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    elif [[ $OS == "rhel" ]]; then
        sudo dnf install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    fi

    echo "Docker installation complete."
}

configure_docker() {
    echo "Configuring Docker..."

    # Check if Docker is installed before proceeding
    if ! command -v docker &> /dev/null; then
        echo "❌ Error: Docker is not installed or is not in PATH."
        echo "🧹 Cleaning up leftover Docker files before exiting..."
        
        # Remove Docker-related packages (for Debian/Ubuntu & RHEL)
        if [[ -f /etc/debian_version ]]; then
            sudo apt remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            sudo apt autoremove -y
        elif [[ -f /etc/redhat-release ]]; then
            sudo dnf remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        fi

        # Delete Docker directories
        sudo rm -rf /var/lib/docker /var/lib/containerd /etc/docker
        sudo rm -rf $HOME/.docker

        echo "✅ Docker files removed. Please try reinstalling Docker."
        exit 1
    fi

    # Enable and start Docker service
    echo "🔄 Enabling and starting Docker service..."
    sudo systemctl enable --now docker 2>/dev/null

    # Verify that Docker is running
    if systemctl is-active --quiet docker; then
        echo "✅ Docker is running successfully."
    else
        echo "❌ Error: Docker service failed to start. Checking logs..."
        sudo journalctl -xeu docker --no-pager | tail -n 20  # Show last 20 lines of Docker logs
        exit 1
    fi

    # Add current user to the Docker group (avoids needing sudo for Docker commands)
    if grep -q "^docker:" /etc/group; then
        sudo usermod -aG docker $USER
        echo "✅ User '$USER' added to the Docker group."
    else
        echo "❌ Error: Docker group does not exist. Please check your installation."
        exit 1
    fi

    echo "⚡ Please log out and log back in OR run: newgrp docker"
}

optimize_docker() {
    echo "🔧 Optimizing Docker configuration..."

    # Define the Docker configuration file path
    DOCKER_CONFIG_FILE="/etc/docker/daemon.json"

    # Ensure Docker config directory exists
    sudo mkdir -p /etc/docker

    # Backup existing configuration if it exists
    if [[ -f "$DOCKER_CONFIG_FILE" ]]; then
        echo "📂 Backing up existing Docker configuration..."
        sudo cp "$DOCKER_CONFIG_FILE" "$DOCKER_CONFIG_FILE.bak_$(date +%F_%T)"
    fi

    # Write optimized settings
    sudo tee "$DOCKER_CONFIG_FILE" > /dev/null <<EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "50m",
        "max-file": "3"
    },
    "exec-opts": ["native.cgroupdriver=systemd"],
    "storage-driver": "overlay2",
    "experimental": true
}
EOF

    # Restart Docker to apply changes
    echo "🔄 Restarting Docker to apply optimizations..."
    sudo systemctl restart docker

    # Check if Docker restarted successfully
    if systemctl is-active --quiet docker; then
        echo "✅ Docker optimization complete. Docker is running."
    else
        echo "❌ Docker failed to restart after optimization. Checking logs..."
        sudo journalctl -xeu docker --no-pager | tail -n 20
        exit 1
    fi
}
