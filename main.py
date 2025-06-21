import asyncio
import websockets
import json
from datetime import datetime, timedelta
from core import (
    SYMBOLS, price_history, last_indicator_update, now_br, now_utc,
    calcular_indicadores, atualizar_trades, verificar_sinal, entrar_trade
)

async def stream_bingx():
    uri = "wss://open-api-swap.bingx.com/swap-market"
    while True:
        try:
            async with websockets.connect(uri) as ws:
                for symbol in SYMBOLS:
                    sub_msg = {
                        "id": symbol,
                        "reqType": "sub",
                        "dataType": f"trade.{symbol}",
                        "dataSize": 1
                    }
                    await ws.send(json.dumps(sub_msg))
                print(f"[{now_br().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Conectado ao WebSocket da BingX")
                while True:
                    try:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if "data" in data and isinstance(data["data"], list):
                            price = float(data["data"][0]["price"])
                            symbol = data["symbol"]
                            agora = datetime.utcnow()
                            price_history[symbol].append(price)
                            atualizar_trades(symbol, price)
                            direcao = verificar_sinal(symbol, price, agora)
                            if direcao:
                                entrar_trade(symbol, direcao, price, agora)
                    except Exception as e:
                        print(f"[{now_br().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Erro interno na leitura de dados:", e)
                        await asyncio.sleep(1)
        except Exception as e:
            print(f"[{now_br().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Erro de conexão. Tentando reconectar...", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    print(f"[{now_br().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 BOTTOMAN V1 iniciado - Robô ativo com WebSocket + RSI + Reentrada por distância")
    asyncio.run(stream_bingx())
