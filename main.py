import asyncio
import websockets
import hmac
import hashlib
import base64
import json
import time
import os
import gzip
from io import BytesIO
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("BINGX_API_KEY")
SECRET_KEY = os.getenv("BINGX_SECRET_KEY")

def get_signature(timestamp, api_key, secret_key):
    pre_sign = f"timestamp={timestamp}&apiKey={api_key}"
    signature = hmac.new(secret_key.encode(), pre_sign.encode(), hashlib.sha256).hexdigest()
    return signature

def decompress_gzip(data):
    buf = BytesIO(data)
    with gzip.GzipFile(fileobj=buf) as f:
        return f.read().decode('utf-8')

async def connect_bingx():
    uri = "wss://open-api-swap.bingx.com/swap-market"

    async with websockets.connect(uri) as ws:
        timestamp = int(time.time() * 1000)
        signature = get_signature(timestamp, API_KEY, SECRET_KEY)

        login_msg = {
            "id": "auth",
            "reqType": "login",
            "apiKey": API_KEY,
            "timestamp": timestamp,
            "sign": signature
        }
        await ws.send(json.dumps(login_msg))
        print(f"[{datetime.now()}] Enviando login...")

        login_response = await ws.recv()
        login_decompressed = decompress_gzip(login_response) if isinstance(login_response, bytes) else login_response
        print(f"[{datetime.now()}] Login (legível): {login_decompressed}")

        subscribe_msg = {
            "id": "ticker-sub",
            "reqType": "sub",
            "dataType": "ticker",
            "symbol": "NEAR-USDT"
        }
        await ws.send(json.dumps(subscribe_msg))
        print(f"[{datetime.now()}] Subscrito ao ticker NEAR-USDT.")

        first_tick = await ws.recv()
        tick_decompressed = decompress_gzip(first_tick) if isinstance(first_tick, bytes) else first_tick
        print(f"[{datetime.now()}] Tick recebido (legível): {tick_decompressed}")

        await ws.close()
        print(f"[{datetime.now()}] Conexão encerrada.")

if __name__ == "__main__":
    asyncio.run(connect_bingx())