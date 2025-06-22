import asyncio
import websockets
import json
import gzip
from io import BytesIO
from datetime import datetime

def decompress_gzip(data):
    buf = BytesIO(data)
    with gzip.GzipFile(fileobj=buf) as f:
        return f.read().decode('utf-8')

async def connect_bingx():
    uri = "wss://open-api-swap.bingx.com/swap-market"

    for attempt in range(3):  # até 3 tentativas
        try:
            print(f"[{datetime.now()}] 🔁 Tentativa {attempt+1}/3 - VERSÃO: v2 corrigida")

            async with websockets.connect(uri) as ws:
                subscribe_msg = {
                    "id": "ticker-sub",
                    "reqType": "sub",
                    "dataType": "market/ticker:NEAR-USDT"
                }
                await ws.send(json.dumps(subscribe_msg))
                print(f"[{datetime.now()}] Subscrito ao ticker NEAR-USDT.")

                tick_raw = await ws.recv()
                tick_decompressed = decompress_gzip(tick_raw) if isinstance(tick_raw, bytes) else tick_raw
                print(f"[{datetime.now()}] Tick recebido (legível): {tick_decompressed}")

                await ws.close()
                print(f"[{datetime.now()}] Conexão encerrada.")
                break

        except Exception as e:
            print(f"[{datetime.now()}] ⚠️ Erro na tentativa {attempt+1}: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(connect_bingx())