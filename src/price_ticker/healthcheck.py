import sys
import urllib.request

urllib.request.urlopen(
    f"http://127.0.0.1:{sys.argv[1]}/api/v1/ready", timeout=3
)
