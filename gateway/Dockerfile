FROM debian:stable-slim

RUN apt-get update && \
    apt-get install -y nginx dnsmasq curl iputils-ping && \
    rm -rf /var/lib/apt/lists/*

COPY dnsmasq.conf /etc/dnsmasq.conf
COPY nginx.conf /etc/nginx/nginx.conf
COPY start.sh /start.sh

RUN chmod +x /start.sh

EXPOSE 80 53

CMD ["/start.sh"]
