import httpx
import time

from dotenv import load_dotenv
from typing import Optional


load_dotenv()
API_BASE = "http://ws.audioscrobbler.com/2.0/"

httpx_cli = httpx.Client(timeout=30)


def http_get(url: str, params: Optional[httpx._types.QueryParamTypes] = None):
    while True:
        try:
            return httpx_cli.get(url, params=params) if params else httpx_cli.get(url)
        except Exception as e:
            print(f"Error http_get: {e}")
            print("Retrying in 30 seconds...")
            time.sleep(30)
            continue
