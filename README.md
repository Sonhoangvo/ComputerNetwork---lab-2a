# Internal Lab - HTTPS Load Balancing Setup

This document is divided into two sections:

- Section 1: Without Securing the Gateway with HTTPS/TLS (baseline model)
- Section 2: With Securing the Gateway with HTTPS/TLS (current implementation in this repository)

## Section 1 - Without Securing the Gateway with HTTPS/TLS

In the baseline model, the gateway is HTTP only and does not terminate TLS.

- Client -> Gateway: HTTP
- Gateway -> Backend: HTTP (or internal plaintext)

Security implications of this baseline:

- Traffic can be read on the frontend and/or backend network segments.
- Traffic can be modified in transit by a network attacker.
- No cryptographic server identity verification is performed.

This section is a conceptual reference for comparison. The active repository configuration is Section 2.

## Section 2 - With Securing the Gateway with HTTPS/TLS (Current Implementation)

This project demonstrates a complete HTTPS load balancing setup using Docker Compose, featuring DNS resolution and round-robin load distribution with TLS on both hops:

- Client -> Gateway (HTTPS)
- Gateway -> Backend services (HTTPS)

## Architecture

- **Gateway**: Nginx reverse proxy with TLS termination and HTTPS upstream proxying
- **Backend A & B**: Simple Python HTTPS servers
- **Client**: Alpine Linux container for testing requests
- **DNS**: Dnsmasq for local DNS resolution

## Components

### Gateway
- Runs Nginx with custom configuration for HTTPS and load balancing
- Uses self-signed SSL certificates
- Provides DNS resolution for `app.groupx.lab`
- Load balances between backend-a and backend-b over verified HTTPS

### Backends
- Two identical Python servers running on port 3000 with TLS enabled
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

### Testing Backend Certificates From Inside Gateway

Run this to verify gateway can establish TLS directly to each backend using the lab CA:

```bash
docker compose exec -T gateway sh -lc 'curl -sS --http1.0 --cacert /certs/ca.crt https://backend-a:3000; echo; curl -sS --http1.0 --cacert /certs/ca.crt https://backend-b:3000; echo'
```

Optional sanity check for CA path inside the gateway container:

```bash
docker compose exec -T gateway sh -lc 'ls -l /certs/ca.crt'
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
- **Backend Certificate**: `certs/backend.crt` (presented by backend-a and backend-b)
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

### Upstream TLS Verification Errors
If gateway logs show SSL verify failures, verify that:

- `certs/backend.crt` is signed by `certs/ca.crt`
- backend certificates include SAN entries for `backend_pool`, `backend-a`, and `backend-b`
- `gateway/nginx.conf` has `proxy_ssl_verify on` and `proxy_ssl_trusted_certificate /certs/ca.crt`

### curl (56) unexpected eof while reading
When testing backends directly with curl, you may see:

```text
curl: (56) OpenSSL SSL_read: ... unexpected eof while reading
```

In this lab, that can happen because Python's simple `http.server` TLS shutdown is not always as graceful as production web servers. If response text is still returned, handshake and certificate validation were successful. Use `--http1.0` in the test command above to avoid this noisy EOF behavior.

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
- Internal networking only; no external access configured

## Why End-to-End TLS Is Stronger

Encrypting only client -> gateway protects traffic on the frontend network, but leaves gateway -> backend traffic exposed in plaintext on the backend network. Any attacker with access to that internal segment (compromised container, misconfigured network policy, packet capture on host bridges) could read or alter backend traffic.

With HTTPS on both hops:

- **Confidentiality**: Request and response bodies stay encrypted across the entire path.
- **Integrity**: TLS record protection prevents in-flight tampering between gateway and backends.
- **Authentication**: The gateway verifies backend certificates against the CA, reducing the risk of proxying to a spoofed service.

This removes the "internal network is trusted" assumption and provides defense in depth.