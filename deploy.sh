#!/bin/bash

# Script để deploy lên Ubuntu server
# Chạy script này trên server Ubuntu

set -e  # Exit on error

echo "=========================================="
echo "Vietnam Provinces API - Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

# 1. Update system
echo -e "${YELLOW}[1/7] Updating system...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# 2. Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}[2/7] Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}Docker installed successfully${NC}"
else
    echo -e "${GREEN}[2/7] Docker already installed${NC}"
fi

# 3. Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}[3/7] Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose installed successfully${NC}"
else
    echo -e "${GREEN}[3/7] Docker Compose already installed${NC}"
fi

# 4. Create app directory
echo -e "${YELLOW}[4/7] Setting up application directory...${NC}"
APP_DIR="/opt/vn-provinces-api"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# 5. Clone or update repository
echo -e "${YELLOW}[5/7] Getting application code...${NC}"
if [ -d "$APP_DIR/.git" ]; then
    echo "Updating existing repository..."
    cd $APP_DIR
    git pull
else
    echo "Please manually copy your application files to $APP_DIR"
    echo "Or clone from git repository:"
    echo "  cd $APP_DIR"
    echo "  git clone <your-repo-url> ."
fi

# 6. Build and start Docker containers
echo -e "${YELLOW}[6/7] Building and starting Docker containers...${NC}"
cd $APP_DIR
docker-compose down
docker-compose build
docker-compose up -d

# 7. Setup Nginx reverse proxy (optional)
echo -e "${YELLOW}[7/7] Nginx setup (optional)...${NC}"
read -p "Do you want to setup Nginx reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! command -v nginx &> /dev/null; then
        sudo apt-get install -y nginx
    fi
    
    # Create Nginx config
    sudo tee /etc/nginx/sites-available/vn-provinces-api > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Thay đổi domain của bạn

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/vn-provinces-api /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    
    echo -e "${GREEN}Nginx configured successfully${NC}"
    echo -e "${YELLOW}Remember to update server_name in /etc/nginx/sites-available/vn-provinces-api${NC}"
fi

# 8. Setup firewall
echo -e "${YELLOW}Setting up firewall...${NC}"
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw --force enable

echo -e "${GREEN}=========================================="
echo -e "Deployment completed successfully!"
echo -e "==========================================${NC}"
echo ""
echo "API is running at: http://localhost:8000"
echo "Check status: docker-compose ps"
echo "View logs: docker-compose logs -f"
echo "Stop: docker-compose down"
echo "Restart: docker-compose restart"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update Nginx server_name if using reverse proxy"
echo "2. Setup SSL certificate with certbot (recommended)"
echo "3. Configure environment variables in docker-compose.yml"
