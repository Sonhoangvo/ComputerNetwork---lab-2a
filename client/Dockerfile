FROM alpine:latest
RUN apk add --no-cache curl bind-tools bash iproute2 iputils ca-certificates
COPY ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates
CMD ["sh"]
