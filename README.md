# Raspberry Pi Home Server

This project sets up a home server on a Raspberry Pi with Docker Compose, featuring:
- **Pi-hole**: Network-wide ad blocking and DNS server
- **Nginx**: Reverse proxy for routing services to containers

## Quick Setup

### 1. Environment Configuration

```bash
# Copy the environment template and configure your variables
cp .env.example .env
```

## Service Setup

### Nginx (Reverse Proxy)

Nginx handles routing requests to different services based on subdomains.

**Current Configuration:**
- Routes `pihole.inshellgagici.localhost` to the Pi-hole container
- Listens on ports 80 (HTTP) and 443 (HTTPS ready)

**Adding New Services:**
1. Add your new service to `docker-compose.yml`
2. Create a new server block in `nginx/inshellgagici.conf.template`:

```nginx
server {
  listen 80;
  server_name newservice.${DOMAIN};

  location / {
    proxy_pass         http://newservice:port;
    proxy_set_header   Host $host;
    proxy_set_header   X-Real-IP $remote_addr;
    proxy_http_version 1.1;
    proxy_set_header   Connection "";
  }
}
```

3. Restart nginx: `docker-compose restart proxy`

### Pi-hole (DNS & Ad Blocking)

Pi-hole requires persistent directories for configuration and data.

**Setup Commands:**
```bash
# Create required directories for Pi-hole data persistence
mkdir -p pihole/etc-pihole
mkdir -p pihole/etc-dnsmasq.d

# Set proper permissions (recommended)
sudo chown -R $USER:$USER pihole/
```

**Configuration Notes:**
- Web interface accessible at `http://pihole.inshellgagici.localhost/admin/`
- DNS server runs on port 53 (TCP/UDP)

> **⚠️ IMPORTANT: Manual DNS Entry Fix**
> 
> If the domain routing breaks and you can't access pihole.inshellgagici.lan, use these commands to manually add the DNS entry:
> 
> ```bash
> # Access the Pi-hole container
> docker-compose exec pihole /bin/bash
> 
> # Add the DNS entry (replace YOUR_PI_IP with your actual Pi's IP address)
> echo "YOUR_PI_IP inshellgagici.lan" >> /etc/pihole/hosts/custom.list
> echo "YOUR_PI_IP pihole.inshellgagici.lan" >> /etc/pihole/custom.list
> 
> # Restart Pi-hole's DNS service
> pihole reloaddns
> pihole reloadlists
### Start All Services

```bash
# Start the entire stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Service Access

Once running, you can access:

- **Pi-hole Admin**: `http://pihole.your-domain.local/admin/`
  - Use the password you set in `PIHOLE_WEBPASS`
- **DNS Server**: Point your devices to your Pi's IP address (port 53)

## Future Services

This setup is ready for additional services like:
- Media servers (Plex, Jellyfin)
- Home automation (Home Assistant)
- Monitoring (Grafana, Prometheus)
- File sharing (Nextcloud)
- And more! 