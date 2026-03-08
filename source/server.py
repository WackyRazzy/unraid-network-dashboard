#!/usr/bin/env python3
"""
RazzyNet Network Dashboard - API Server
Serves live network data from the Unraid server on port 8888
"""

import json, subprocess, socket, time, os, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen
from urllib.error import URLError

PORT = 8888
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=10).decode().strip()
    except:
        return ""


def ping_ms(host):
    try:
        out = run(f"ping -c 2 -W 2 {host}")
        m = re.search(r'rtt min/avg/max.*?= [\d.]+/([\d.]+)/', out)
        if m: return round(float(m.group(1)))
        m = re.search(r'time=([\d.]+)', out)
        if m: return round(float(m.group(1)))
    except:
        pass
    return None


def check_port(host, port):
    try:
        s = socket.socket()
        s.settimeout(3)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except:
        return False


def get_network_data():
    data = {}

    # Hostname & system info
    data['hostname'] = run("hostname")
    ver = run("cat /etc/unraid-version")
    m = re.search(r'version="([^"]+)"', ver)
    data['unraid_version'] = m.group(1) if m else "Unknown"
    data['kernel'] = run("uname -r")
    data['cpu'] = run("grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2").strip()

    # Network - primary interface (br0)
    data['local_ip']  = run("ip -4 addr show br0 | grep -oP '(?<=inet )[\d.]+'")
    data['local_ip6'] = run("ip -6 addr show br0 scope global | grep -oP '(?<=inet6 )[^/]+' | head -1")
    data['mac']       = run("cat /sys/class/net/eth0/address")
    data['gateway']   = run("ip route | grep default | awk '{print $3}' | head -1")
    data['dns']       = ", ".join(run("grep nameserver /etc/resolv.conf | awk '{print $2}'").splitlines())
    data['mtu']       = run("cat /sys/class/net/br0/mtu")

    # Tailscale VPN
    data['tailscale_ip'] = run("ip -4 addr show tailscale1 | grep -oP '(?<=inet )[\d.]+'")

    # Interface states
    data['eth0_state'] = run("cat /sys/class/net/eth0/operstate")
    data['eth1_state'] = run("cat /sys/class/net/eth1/operstate")
    data['eth0_speed'] = run("cat /sys/class/net/eth0/speed 2>/dev/null") + " Mbps"
    data['bond_mode']  = run("cat /sys/class/net/bond0/bonding/mode 2>/dev/null")

    # Network RX/TX stats
    def iface_stats(iface):
        rx = run(f"cat /sys/class/net/{iface}/statistics/rx_bytes 2>/dev/null")
        tx = run(f"cat /sys/class/net/{iface}/statistics/tx_bytes 2>/dev/null")
        def fmt(b):
            try:
                b = int(b)
                if b > 1e9: return f"{b/1e9:.2f} GB"
                if b > 1e6: return f"{b/1e6:.2f} MB"
                return f"{b/1e3:.1f} KB"
            except:
                return "—"
        return {"rx": fmt(rx), "tx": fmt(tx)}

    data['stats_br0']  = iface_stats("br0")
    data['stats_eth0'] = iface_stats("eth0")

    # Public IP info via ipapi.co
    try:
        with urlopen("https://ipapi.co/json/", timeout=5) as r:
            pub = json.loads(r.read())
        data['public_ip']   = pub.get('ip', '—')
        org = pub.get('org', '')
        data['isp']         = re.sub(r'^AS\d+\s+', '', org) if org else '—'
        data['asn']         = pub.get('asn', '—')
        data['pub_city']    = pub.get('city', '')
        data['pub_region']  = pub.get('region', '')
        data['pub_country'] = pub.get('country_code', '')
        data['pub_lat']     = pub.get('latitude', 0)
        data['pub_lon']     = pub.get('longitude', 0)
        data['proxy']       = pub.get('proxy', False)
    except Exception as e:
        data['public_ip']   = f'Error: {e}'
        data['isp']         = data['asn'] = '—'
        data['pub_city']    = data['pub_region'] = data['pub_country'] = ''
        data['pub_lat']     = data['pub_lon'] = 0
        data['proxy']       = False

    # Ping latency to key targets
    targets = [
        ("1.1.1.1",         "Cloudflare"),
        ("8.8.8.8",         "Google"),
        ("9.9.9.9",         "Quad9"),
        (data['gateway'],   "Gateway"),
    ]
    data['latency'] = [{"host": h, "name": n, "ms": ping_ms(h)} for h, n in targets if h]

    # Local port checks
    ports = [
        (80,    "HTTP"),
        (443,   "HTTPS"),
        (22,    "SSH"),
        (53,    "DNS"),
        (8080,  "ALT-HTTP"),
        (32400, "PLEX"),
        (8888,  "DASHBOARD"),
    ]
    data['ports'] = [{"port": p, "label": l, "open": check_port("127.0.0.1", p)} for p, l in ports]

    # Docker container counts
    data['docker_running'] = run("docker ps -q 2>/dev/null | wc -l")
    data['docker_total']   = run("docker ps -aq 2>/dev/null | wc -l")

    data['timestamp'] = time.strftime("%a %d %b %Y %H:%M:%S %Z")
    return data


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress access logs

    def do_GET(self):
        if self.path == '/api/network':
            try:
                body = json.dumps(get_network_data()).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', len(body))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path in ('/', '/index.html'):
            try:
                with open(os.path.join(DASHBOARD_DIR, 'index.html'), 'rb') as f:
                    body = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', len(body))
                self.end_headers()
                self.wfile.write(body)
            except:
                self.send_response(404)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == '__main__':
    local_ip = run("ip -4 addr show br0 | grep -oP '(?<=inet )[\d.]+'") or "YOUR-UNRAID-IP"
    print(f"[RazzyNet] Network Dashboard running → http://{local_ip}:{PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
