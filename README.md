# RazzyNet — Unraid Network Dashboard

> **Real-time network monitoring for your Unraid server.** A lightweight plugin that adds a live dashboard widget and a full cyberpunk-style diagnostic panel showing everything happening on your network — right from your Unraid UI.

![Unraid](https://img.shields.io/badge/Unraid-6.12%2B-orange?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Version](https://img.shields.io/badge/Version-2025.03.08-purple?style=flat-square)

---

## What Is This?

**RazzyNet Network Dashboard** is an Unraid plugin that gives you instant visibility into your server's network status — without needing to SSH in or run commands manually.

It installs two things:

1. **A widget on your Unraid Dashboard** — always visible on the main page, showing your public IP, ISP, latency, local server info and Tailscale VPN status
2. **A full-page diagnostic panel** at `http://YOUR-IP:8888` — a sleek dark cyberpunk-style interface with detailed real-time network diagnostics

Everything runs automatically. No Docker containers, no npm, no extra packages. It uses Python 3 which is already included with Unraid, and auto-starts every time your server boots.

---

## Features

| Feature | Description |
|---|---|
| 🌍 **Public IP & ISP** | Your current public IP, ISP name and ASN number |
| 📍 **Location** | City, region and country of your internet connection |
| 🛡️ **Proxy / VPN Detection** | Detects if a proxy or VPN is active on your connection |
| ⚡ **Latency Bars** | Live ping times to Cloudflare (1.1.1.1), Google (8.8.8.8), Quad9 (9.9.9.9) and your gateway |
| 🔌 **Port Checker** | Checks which ports are open locally: HTTP, HTTPS, SSH, DNS, Plex, and more |
| 📡 **Network Interfaces** | Full table of eth0, eth1, bond0, br0 and Tailscale with state and IP |
| 🐳 **Docker Stats** | Running vs stopped container count and network RX/TX totals |
| 🔐 **Tailscale VPN** | Shows your Tailscale IP if active, or flags it as inactive |
| 🔄 **Auto-refresh** | Dashboard widget refreshes every 5 minutes automatically |
| 🚀 **Auto-start on Boot** | Starts with Unraid — no manual steps ever needed after install |
| 🧹 **Zero Dependencies** | Uses Python 3 already on your Unraid — nothing extra to install |

---

## Installation

### Option 1: Community Apps Store (Recommended)
Coming Soon. Please use opition 2 untill this message is removed

1. In your Unraid web UI, click the **Apps** tab
2. Search for **RazzyNet Network Dashboard**
3. Click **Install**
4. Done — the widget appears on your Dashboard and the full panel is at `http://YOUR-IP:8888`

### Option 2: Manual Plugin Install

1. In Unraid, go to **Plugins** → **Install Plugin**
2. Paste this URL:
   ```
   https://raw.githubusercontent.com/WackyRazzy/unraid-network-dashboard/main/plugin/network-dashboard.plg
   ```
3. Click **Install**

---

## Accessing the Dashboard

After installation, open your browser and go to:

- **Full dashboard panel:** `http://YOUR-UNRAID-IP:8888`
- **Raw JSON API:** `http://YOUR-UNRAID-IP:8888/api/network`
- **Unraid widget:** Automatically shown on your Unraid Dashboard page

Replace `YOUR-UNRAID-IP` with your server's local IP address, e.g. `192.168.1.100`.

---

## How It Works

The plugin installs a small **Python 3 HTTP server** on port 8888. Every time the widget or panel loads, this server:

1. Reads your network interfaces, IP addresses and gateway from the system
2. Checks your DNS servers and Tailscale VPN status
3. Fetches your public IP and ISP info from [ipapi.co](https://ipapi.co)
4. Runs ping tests to Cloudflare, Google, Quad9 and your gateway
5. Checks which local ports are currently listening
6. Counts your Docker containers and reads network transfer stats
7. Returns everything as JSON and serves the dashboard UI

The server is added to Unraid's `/boot/config/go` script so it restarts automatically after every reboot.

---

## Requirements

- **Unraid 6.12.0** or newer
- **Python 3** — already included with Unraid, no install needed
- **Port 8888** must be free (not used by another service)
- Internet access for public IP lookup (ipapi.co)

---

## Service Management

You can control the dashboard server manually over SSH:

```bash
# Start
bash /boot/custom/network-dashboard/start.sh start

# Stop
bash /boot/custom/network-dashboard/start.sh stop

# Restart
bash /boot/custom/network-dashboard/start.sh restart

# Check status
bash /boot/custom/network-dashboard/start.sh status

# View logs
cat /var/log/network-dashboard.log
```

---

## Repository Structure

```
unraid-network-dashboard/
├── plugin/
│   └── network-dashboard.plg       ← Install this in Unraid Plugins tab
├── template/
│   └── network-dashboard.xml       ← Community Apps store listing
├── source/
│   ├── server.py                   ← Python3 API server
│   ├── index.html                  ← Full-page dashboard UI
│   └── network-dashboard.page      ← Unraid dashboard widget
├── .github/
│   └── workflows/
│       └── release.yml             ← Auto-creates GitHub releases on new tags
└── README.md                       ← This file
```

---

## Troubleshooting

**Widget says "API unavailable"**
→ The server isn't running. SSH in and run:
```bash
bash /boot/custom/network-dashboard/start.sh start
```

**Port 8888 already in use**
→ Find what's using it: `fuser 8888/tcp`
→ Edit `PORT = 8888` in `/boot/custom/network-dashboard/server.py` and restart

**Public IP shows an error**
→ Check internet access from the server: `curl https://ipapi.co/json/`

**Widget not showing on Dashboard**
→ Refresh Unraid UI with Ctrl+Shift+R (hard refresh)

---

## License

MIT License — free to use, modify and share.

---

Built for Unraid by **WackyRazzy** — drop a ⭐ if it's useful!

**Issues and pull requests welcome:** https://github.com/WackyRazzy/unraid-network-dashboard/issues
