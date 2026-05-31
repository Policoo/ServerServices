# Raspberry Pi Home Server

This project sets up a home server on a Raspberry Pi with Docker Compose, featuring:
- **Pi-hole**: Network-wide ad blocking and DNS server
- **Caddy**: Reverse proxy with LAN-only HTTPS using an internal CA

## Quick Setup

### 1. Environment Configuration

```bash
# Copy the environment template and configure your variables
cp .env.example .env
```

## Service Setup

### Caddy (Reverse Proxy)

Caddy handles routing requests to different services based on subdomains and
issues LAN-only HTTPS certificates using its internal certificate authority.

**Current Configuration:**
- Routes `pihole.${DOMAIN}` to the Pi-hole container
- Routes `filebrowser.${DOMAIN}` to the File Browser container
- Routes `netdata.${DOMAIN}` to the Netdata container
- Routes `couchdb.${DOMAIN}` to the CouchDB container
- Listens on ports 80 and 443

For mobile apps that require HTTPS, install Caddy's local root certificate on
the device and fully trust it. With the default storage layout, the certificate
is created after Caddy starts at:

```bash
${DATA_STORAGE_BASE_DIR}/caddy/data/caddy/pki/authorities/local/root.crt
```

**Adding New Services:**
1. Add your new service to `docker-compose.yml`
2. Create a new site block in `caddy/Caddyfile`:

```caddyfile
newservice.{$DOMAIN} {
  tls internal
  reverse_proxy newservice:port
}
```

3. Restart Caddy: `docker compose restart caddy`

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
- Web interface accessible at `https://pihole.inshellgagici.lan/admin/`
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
