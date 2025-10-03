# Vietnam Provinces API - Docker Deployment Guide

Hướng dẫn deploy Vietnam Provinces API lên Ubuntu 22.04.4 LTS sử dụng Docker.

## 📋 Yêu cầu hệ thống

-   Ubuntu 22.04.4 LTS (hoặc tương đương)
-   RAM: Tối thiểu 512MB, khuyến nghị 1GB+
-   CPU: 1 core trở lên
-   Disk: 2GB free space
-   Port: 8000 (hoặc 80/443 nếu dùng Nginx)

## 🚀 Phương pháp 1: Deploy tự động (Khuyên dùng)

### Bước 1: Upload code lên server

```bash
# Trên máy local, copy toàn bộ project lên server
scp -r vn-open-api-provinces user@your-server:/tmp/

# Hoặc dùng git
ssh user@your-server
cd /opt
sudo git clone <your-repo> vn-provinces-api
cd vn-provinces-api
```

### Bước 2: Chạy script deploy

```bash
cd /opt/vn-provinces-api
chmod +x deploy.sh
./deploy.sh
```

Script sẽ tự động:

-   ✅ Cài đặt Docker & Docker Compose
-   ✅ Build Docker image
-   ✅ Start containers
-   ✅ Cấu hình Nginx (optional)
-   ✅ Setup firewall

## 🔧 Phương pháp 2: Deploy thủ công

### Bước 1: Cài đặt Docker

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Bước 2: Upload và build

```bash
# Di chuyển vào thư mục project
cd /opt/vn-provinces-api

# Build image
docker-compose build

# Start containers
docker-compose up -d
```

### Bước 3: Kiểm tra

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Test API
curl http://localhost:8000/api/v2/
```

## 🌐 Cấu hình Nginx Reverse Proxy

### Cài đặt Nginx

```bash
sudo apt-get install -y nginx
```

### Copy config

```bash
sudo cp nginx.conf /etc/nginx/sites-available/vn-provinces-api

# Chỉnh sửa domain
sudo nano /etc/nginx/sites-available/vn-provinces-api
# Thay đổi: server_name your-domain.com

# Enable site
sudo ln -s /etc/nginx/sites-available/vn-provinces-api /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 🔒 Setup SSL với Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (certbot tự động setup)
sudo certbot renew --dry-run
```

## 📊 Quản lý Container

### Start/Stop/Restart

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build
```

### Xem logs

```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f vn-provinces-api
```

### Update code

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔍 Monitoring & Debugging

### Check container health

```bash
docker-compose ps
docker stats
```

### Enter container

```bash
docker-compose exec vn-provinces-api bash
```

### Check API health

```bash
curl http://localhost:8000/api/v2/
curl http://localhost:8000/docs
```

## 🛡️ Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

## ⚙️ Environment Variables

Chỉnh sửa `docker-compose.yml`:

```yaml
environment:
    - BLACKLISTED_CLIENTS=192.168.1.100,10.0.0.50
    - TRACKING=true
    - CDN_CACHE_INTERVAL=60
```

## 🎯 Production Best Practices

### 1. Resource Limits

Đã cấu hình trong `docker-compose.yml`:

-   CPU: 1 core max, 0.5 reserved
-   Memory: 512MB max, 256MB reserved

### 2. Security

-   ✅ Non-root user trong container
-   ✅ Health checks
-   ✅ Firewall rules
-   ✅ SSL/TLS encryption
-   ✅ Security headers trong Nginx

### 3. Logging

```bash
# Setup log rotation
sudo nano /etc/logrotate.d/vn-provinces-api
```

```
/var/log/nginx/vn-provinces-api*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### 4. Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker save vn-provinces-api > /backup/vn-provinces-api-$DATE.tar
```

## 🔄 Auto-restart on Boot

```bash
# Containers sẽ tự động restart (đã config trong docker-compose.yml)
restart: unless-stopped

# Ensure Docker starts on boot
sudo systemctl enable docker
```

## 📞 Troubleshooting

### Port already in use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Container won't start

```bash
# Check logs
docker-compose logs

# Remove and recreate
docker-compose down -v
docker-compose up -d
```

### Out of disk space

```bash
# Clean up Docker
docker system prune -a

# Check disk usage
df -h
du -sh /var/lib/docker
```

## 📈 Performance Tuning

### Nginx worker processes

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;
```

### Docker resources

Adjust in `docker-compose.yml` based on your needs.

## 🎉 Kết quả

Sau khi deploy thành công:

-   API v1: `http://your-domain.com/api/v1/`
-   API v2: `http://your-domain.com/api/v2/`
-   Docs: `http://your-domain.com/docs`
-   Health: `http://your-domain.com/health`

---

## 📝 Quick Reference

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Update code & restart
git pull && docker-compose up -d --build

# Check status
docker-compose ps
```
