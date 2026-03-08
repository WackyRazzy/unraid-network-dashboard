# WackyNAS — Unraid Network Dashboard

A real-time network monitoring plugin for Unraid.

## Features
- Public IP, ISP, ASN, location and proxy/VPN detection
- Ping latency to Cloudflare, Google, Quad9 and gateway
- Local port status (HTTP, HTTPS, SSH, DNS, Plex, etc)
- Network interface info (eth0, bond0, br0, Tailscale)
- Docker container stats
- Auto-starts on every boot
- Zero extra dependencies (uses Python3 built into Unraid)

## Install via Community Apps
Search for Network Dashboard or WackyNAS in the Unraid Apps tab.

## Manual Install
Plugins > Install Plugin, paste:
https://raw.githubusercontent.com/WackyRazzy/unraid-network-dashboard/main/plugin/network-dashboard.plg

## Access
- Dashboard: http://YOUR-UNRAID-IP:8888
- JSON API: http://YOUR-UNRAID-IP:8888/api/network

## Service Control
bash /boot/custom/network-dashboard/start.sh start|stop|restart|status

## Requirements
- Unraid 6.12.0+
- Port 8888 free

## License
MIT — built for the Unraid community by WackyRazzy
