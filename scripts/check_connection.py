import os
import socket
from urllib.parse import urlparse
from pathlib import Path
from dotenv import load_dotenv

# Load env manually since we might not want to depend on app.config if it has side effects
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

url = os.getenv("R2D2_VERTEX_BASE_URL")
print(f"Checking URL: {url}")

if not url:
    print("Error: R2D2_VERTEX_BASE_URL is not set.")
    exit(1)

if "<" in url or ">" in url:
    print("Error: URL contains placeholders (< or >). Please fill in the actual host.")
    exit(1)

try:
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        print(f"Error: Could not parse hostname from {url}")
        exit(1)
        
    print(f"Resolving hostname: {hostname}")
    ip = socket.gethostbyname(hostname)
    print(f"Success! Resolved {hostname} to {ip}")
except socket.gaierror as e:
    print(f"Connection Failed: [Errno {e.errno}] {e.strerror}")
    print("This indicates the hostname cannot be resolved. Check your VPN, Proxy, or the URL itself.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
