#!/bin/sh
set -e

dnsmasq --conf-file=/etc/dnsmasq.conf &
nginx -g 'daemon off;'
