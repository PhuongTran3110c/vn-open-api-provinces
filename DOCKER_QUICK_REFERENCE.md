# 🐳 Docker Deployment - Quick Reference

## Files Created

### Core Docker Files

-   ✅ `Dockerfile` - Multi-stage build image
-   ✅ `.dockerignore` - Exclude unnecessary files
-   ✅ `docker-compose.yml` - Development setup
-   ✅ `docker-compose.prod.yml` - Production setup with more resources
-   ✅ `.env.example` - Environment variables template

### Deployment Scripts

-   ✅ `deploy.sh` - Full automated deployment script
-   ✅ `quick-start.sh` - Quick start for testing
-   ✅ `Makefile` - Convenient make commands

### Configuration

-   ✅ `nginx.conf` - Nginx reverse proxy config
-   ✅ `DEPLOYMENT.md` - Full deployment documentation

## 🚀 Quick Commands

### Local Testing

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production Deployment on Ubuntu 22.04

#### Method 1: Automated (Recommended)

```bash
# 1. Upload files to server
scp -r vn-open-api-provinces user@server:/opt/

# 2. SSH to server
ssh user@server

# 3. Run deployment script
cd /opt/vn-open-api-provinces
chmod +x deploy.sh
./deploy.sh
```

#### Method 2: Quick Start

```bash
# On server
cd /opt/vn-open-api-provinces
chmod +x quick-start.sh
./quick-start.sh
```

#### Method 3: Manual

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Build and run
docker-compose -f docker-compose.prod.yml up -d
```

## 📦 Using Makefile

```bash
make help      # Show all commands
make build     # Build image
make up        # Start containers
make down      # Stop containers
make logs      # View logs
make restart   # Restart containers
make deploy    # Build + Start
make clean     # Clean up
make test      # Test API
```

## 🌐 Setup Nginx Reverse Proxy

```bash
# 1. Install Nginx
sudo apt-get install -y nginx

# 2. Copy config
sudo cp nginx.conf /etc/nginx/sites-available/vn-provinces-api

# 3. Edit domain
sudo nano /etc/nginx/sites-available/vn-provinces-api
# Change: server_name your-domain.com

# 4. Enable site
sudo ln -s /etc/nginx/sites-available/vn-provinces-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Setup SSL (HTTPS)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is setup automatically
```

## 🔧 Environment Variables

Create `.env` file from example:

```bash
cp .env.example .env
nano .env
```

```env
BLACKLISTED_CLIENTS=192.168.1.100,10.0.0.50
TRACKING=false
CDN_CACHE_INTERVAL=30
```

## 📊 Monitoring

### Check Status

```bash
docker-compose ps
docker stats
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific time
docker-compose logs --since 30m
```

### Health Check

```bash
curl http://localhost:8000/api/v2/
curl http://localhost:8000/health
```

## 🔄 Updates

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or use Makefile
make deploy
```

## 🛡️ Security

### Firewall

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Resource Limits

Already configured in `docker-compose.prod.yml`:

-   CPU: 2 cores max
-   Memory: 1GB max

## 🐛 Troubleshooting

### Container won't start

```bash
docker-compose logs
docker-compose down -v
docker-compose up -d
```

### Port already in use

```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Out of disk space

```bash
docker system prune -a
df -h
```

## 📈 Performance

### Production Settings

-   Use `docker-compose.prod.yml` for production
-   Enable Nginx caching
-   Setup CDN if needed
-   Monitor with tools like Grafana/Prometheus

## 🎯 Endpoints

After deployment, your API will be available at:

-   **API v1**: http://your-domain.com/api/v1/
-   **API v2**: http://your-domain.com/api/v2/
-   **Docs**: http://your-domain.com/docs
-   **Health**: http://your-domain.com/api/v2/

## 📞 Support

For issues:

1. Check logs: `docker-compose logs -f`
2. Check container status: `docker-compose ps`
3. Restart: `docker-compose restart`
4. Full rebuild: `docker-compose down && docker-compose up -d --build`

---

**Happy Deploying! 🚀**
