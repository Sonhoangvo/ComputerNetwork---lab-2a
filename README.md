# Internal Lab - HTTPS Load Balancing Setup

This project demonstrates a complete HTTPS load balancing setup using Docker Compose, featuring SSL termination, DNS resolution, and round-robin load distribution.

## Architecture

- **Gateway**: Nginx reverse proxy with SSL termination and load balancing
- **Backend A & B**: Simple Python HTTP servers
- **Client**: Alpine Linux container for testing requests
- **DNS**: Dnsmasq for local DNS resolution

## Components

### Gateway
- Runs Nginx with custom configuration for HTTPS and load balancing
- Uses self-signed SSL certificates
- Provides DNS resolution for `app.groupx.lab`
- Load balances between backend-a and backend-b

### Backends
- Two identical Python servers running on port 3000
- Backend A responds with "Hello from Backend A"
- Backend B responds with "Hello from Backend B"

### Client
- Alpine Linux container with curl and networking tools
- Pre-configured to trust the self-signed CA certificate
- Connected to internal networks for testing

## Prerequisites

- Docker
- Docker Compose

## Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd /path/to/internal-lab
   ```

2. **Start the services**
   ```bash
   docker compose up -d
   ```

3. **Verify services are running**
   ```bash
   docker compose ps
   ```

## Usage

### Testing Load Balancing

Execute requests from the client container to test load balancing:

```bash
docker compose exec client sh -c 'for i in $(seq 1 10); do curl -s https://app.groupx.lab; done'
```

Expected output alternates between:
```
Hello from Backend A
Hello from Backend B
Hello from Backend A
...
```

### Manual Testing

Access the client container for interactive testing:

```bash
docker compose exec client sh
```

From within the container:
```bash
curl https://app.groupx.lab
nslookup app.groupx.lab
```

### SSL Certificate Details

- **CA Certificate**: `certs/ca.crt`
- **Gateway Certificate**: `certs/gateway.crt`
- **Client trusts the CA automatically** (no need for `--cacert` or `--insecure`)

## Configuration Files

- `docker-compose.yml`: Service definitions and networking
- `gateway/nginx.conf`: Nginx configuration with upstream load balancing
- `gateway/dnsmasq.conf`: DNS configuration
- `backend-a/app.py` & `backend-b/app.py`: Simple Python servers
- `certs/`: Self-signed certificates and keys

## Networks

- **frontend**: Client and gateway communication
- **backend**: Gateway to backend servers

## Ports

- **8080** (host): Gateway HTTP port (redirects to HTTPS)
- **443** (internal): Gateway HTTPS port
- **3000** (internal): Backend servers

## Troubleshooting

### Certificate Issues
If you encounter SSL errors, ensure the client container has been rebuilt with the CA certificate:
```bash
docker compose up -d --build client
```

### DNS Resolution
The client uses the gateway (172.20.0.10) as DNS server. Verify with:
```bash
docker compose exec client nslookup app.groupx.lab
```

### Load Balancing Not Working
Check nginx configuration and ensure backends are healthy:
```bash
docker compose logs gateway
docker compose logs backend-a
docker compose logs backend-b
```

## Development

### Rebuilding Services
```bash
docker compose up -d --build
```

### Viewing Logs
```bash
docker compose logs -f [service-name]
```

### Stopping Services
```bash
docker compose down
```

## Security Notes

- Uses self-signed certificates for demonstration
- Not suitable for production without proper certificates
- Internal networking only; no external access configured</content>
<parameter name="filePath">/home/son/internal-lab/README.md