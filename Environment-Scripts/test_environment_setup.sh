#!/bin/bash

# Define messages
declare -A MSG=(
    ["PYTHON_CHECK"]="Checking if Python3 is installed..."
    ["PYTHON_INSTALL"]="Python3 is not installed. Installing..."
    ["PYTHON_INSTALLED"]="Python3 is already installed."

    ["PIP_CHECK"]="Checking if pip3 is installed..."
    ["PIP_INSTALL"]="pip3 is not installed. Installing..."
    ["PIP_INSTALLED"]="pip3 is already installed."

    ["LIB_CHECK"]="Checking if Python libraries are installed..."
    ["LIB_INSTALL"]="Installing missing Python libraries..."

    ["OS_DETECT"]="Detecting OS..."
    ["OS_UNSUPPORTED"]="Unsupported OS. Exiting."
)

# List of common Python libraries for API development & data engineering
declare -A PYTHON_LIBRARIES=(
    ["faker"]="Generates fake data"
    ["requests"]="HTTP requests (API interaction)"
    ["Flask"]="Lightweight web framework"
    ["FastAPI"]="High-performance API framework"
    ["pandas"]="Data analysis and manipulation"
    ["numpy"]="Numerical computing"
    ["boto3"]="AWS SDK for Python"
    ["SQLAlchemy"]="Database ORM"
    ["pyarrow"]="Columnar data processing (e.g., Parquet files)"
)

# Function to detect OS
detect_os() {
    echo "${MSG["OS_DETECT"]}"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        echo "Detected OS: $OS"
    else
        echo "${MSG["OS_UNSUPPORTED"]}"
        exit 1
    fi
}

# Function to install Python3 and pip
install_python() {
    echo "${MSG["PYTHON_CHECK"]}"
    if ! command -v python3 &> /dev/null; then
        echo "${MSG["PYTHON_INSTALL"]}"
        if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
            sudo apt update && sudo apt install -y python3 python3-pip
        elif [[ "$OS" == "rhel" || "$OS" == "fedora" || "$OS" == "centos" || "$OS" == "amzn" ]]; then
            sudo yum update -y && sudo yum install -y python3 python3-pip
        else
            echo "${MSG["OS_UNSUPPORTED"]}"
            exit 1
        fi
    else
        echo "${MSG["PYTHON_INSTALLED"]}"
    fi
}

# Function to install pip3 if missing
install_pip() {
    echo "${MSG["PIP_CHECK"]}"
    if ! command -v pip3 &> /dev/null; then
        echo "${MSG["PIP_INSTALL"]}"
        pip3 install --upgrade pip --user
    else
        echo "${MSG["PIP_INSTALLED"]}"
    fi
}

# Function to check and install Python libraries
install_python_libraries() {
    echo "${MSG["LIB_CHECK"]}"
    for lib in "${!PYTHON_LIBRARIES[@]}"; do
        if ! python3 -c "import $lib" &> /dev/null; then
            echo "Installing $lib (${PYTHON_LIBRARIES[$lib]})..."
            pip3 install "$lib" --user
        else
            echo "$lib (${PYTHON_LIBRARIES[$lib]}) is already installed."
        fi
    done
}

# Main execution
detect_os
install_python
install_pip
install_python_libraries

echo "✅ Setup completed! Your Python environment is ready."
