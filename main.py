import asyncio
import websockets
import json

async def bingx_websocket():
    url = "wss://open-api-swap.bingx.com/swap-market"
    symbol = "BTC-USDT"  # Pode ser trocado por qualquer símbolo suportado

    async with websockets.connect(url) as websocket:
        subscribe_msg = {
            "id": "1",
            "reqType": "sub",
            "dataType": f"trade.{symbol}",
            "dataSize": 1
        }
        await websocket.send(json.dumps(subscribe_msg))
        print(f"Subscribed to {symbol} trades on BingX")

        while True:
            try:
                message = await websocket.recv()
                print(f"Received message: {message}")
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    asyncio.run(bingx_websocket())
