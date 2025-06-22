
import asyncio
import websockets
import json

symbols_to_test = [
    "trade.PENDLE-USDT",
    "market.trade.PENDLE-USDT",
    "spot.trade.PENDLEUSDT",
    "trade.PENDLEUSDT"
]

async def test_ws(symbol_format):
    uri = "wss://open-api-swap.bingx.com/swap-market"
    payload = {
        "dataType": symbol_format,
        "event": "sub"
    }

    print(f"🔄 Testando conexão com dataType: {symbol_format}")
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(payload))
            print("📤 Enviado:", payload)
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            print("✅ Sucesso! Resposta recebida:")
            print(response)
    except Exception as e:
        print(f"❌ Erro com dataType '{symbol_format}': {e}")

async def main():
    for symbol in symbols_to_test:
        await test_ws(symbol)
        print("-" * 50)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
