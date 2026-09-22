# Production Deployment & Operations Guide
## ADCRA — Autonomous Digital Campaign & Creative Production System

This guide outlines best practices for deploying ADCRA in production environments, covering Docker containerization, systemd Linux daemon service setup, Nginx reverse proxy configuration, security hardening, and continuous integration.

---

## 1. Docker Deployment (Recommended for Cloud)

ADCRA provides a production-ready `Dockerfile` and `docker-compose.yml` optimized for cloud servers and Kubernetes clusters.

### Quick Start with Docker Compose
```bash
# 1. Clone repository
git clone https://github.com/abludomotica-hue/ADCRA.git
cd ADCRA

# 2. Configure environment
cp .env.example .env
# Set your OPENAI_API_KEY, GEMINI_API_KEY, etc. in .env

# 3. Build and launch container in background
docker compose up -d --build

# 4. Check container health
docker compose ps
curl http://localhost:8080/api/health
```

### Useful Docker Commands:
```bash
# View live server logs
docker compose logs -f adcra

# Stop container
docker compose down

# Restart container
docker compose restart adcra
```

---

## 2. Bare-Metal Linux Deployment (Systemd Service)

If you are running ADCRA on a dedicated Linux workstation or server with native GPU drivers (e.g. for DaVinci Resolve or NVENC acceleration):

### Step 1: Create ADCRA System User & Setup Directory
```bash
sudo useradd -m -s /bin/bash adcra
sudo mkdir -p /opt/adcra
sudo chown -R adcra:adcra /opt/adcra
```

### Step 2: Create Systemd Service File
Create `/etc/systemd/system/adcra.service`:

```ini
[Unit]
Description=ADCRA Creative Operating System Server
After=network.target

[Service]
Type=simple
User=adcra
Group=adcra
WorkingDirectory=/opt/adcra
EnvironmentFile=/opt/adcra/.env
ExecStart=/opt/adcra/venv/bin/python3 /opt/adcra/dashboard_server.py --port 8080 --host 127.0.0.1
Restart=always
RestartSec=5s

# Security sandboxing
ProtectSystem=full
ProtectHome=read-only
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

### Step 3: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable adcra
sudo systemctl start adcra
sudo systemctl status adcra
```

---

## 3. Reverse Proxy Configuration (Nginx + Let's Encrypt SSL)

Never expose port `8080` directly to the public internet. Use a reverse proxy like Nginx or Caddy to handle SSL/TLS termination, HTTP byte-ranges, and connection timeouts.

### Nginx Virtual Host Configuration (`/etc/nginx/sites-available/adcra.conf`):
```nginx
server {
    listen 80;
    server_name adcra.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name adcra.yourdomain.com;

    # SSL Certificates (managed via Certbot)
    ssl_certificate /etc/letsencrypt/live/adcra.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/adcra.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Client upload size (for high-res video assets)
    client_max_body_size 500M;

    # Timeouts for heavy video rendering
    proxy_read_timeout 600s;
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Enable byte-ranges for video playback scrubbing
        proxy_force_ranges on;
    }
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/adcra.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 4. Backup & Disaster Recovery

ADCRA stores all campaign blueprints, rendered deliverables, and learned brand memories in the `campaign/` directory:

| Directory / File | Description | Backup Priority |
|---|---|---|
| `campaign/memory/` | Brand knowledge graph and episodic memory | **Critical** (Daily) |
| `campaign/campaign-manifest.json` | Master campaign registry | **Critical** (Daily) |
| `campaign/deliverables/` | Final rendered video masters and social cuts | **High** (Weekly) |
| `config/` | System schemas and validation rules | **High** (In Git) |

### Automated Daily Backup Script (`backup_adcra.sh`):
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/adcra"
mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_DIR/adcra_memory_$DATE.tar.gz" -C /opt/adcra campaign/memory campaign/*.json
# Prune backups older than 30 days
find "$BACKUP_DIR" -type f -name "*.tar.gz" -mtime +30 -delete
```

---

## 5. Continuous Integration (GitHub Actions)

Add this workflow to `.github/workflows/test.yml` to ensure every commit and PR is tested automatically:

```yaml
name: ADCRA CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install FFmpeg
        run: |
          sudo apt update
          sudo apt install -y ffmpeg libavcodec-extra

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Run Test Suite
        run: |
          python -m unittest discover -s tests -q
```
