
import asyncio
import websockets
import json
from datetime import datetime, timedelta
from collections import deque

SYMBOLS = ["NEAR-USDT", "SOL-USDT"]
price_history = {symbol: deque(maxlen=1000) for symbol in SYMBOLS}
last_entry_time = {}
last_distance_reentry_time = {}

DISTANCE_THRESHOLD = 0.02
RSI_MIN = 35
RSI_MAX = 73
TIMEFRAME_RESTRICTION_MINUTES = 120
DISTANCE_REENTRY_INTERVAL_MINUTES = 15

def rsi(prices, period=13):
    if len(prices) < period + 1:
        return None
    gains = [max(0, prices[i] - prices[i - 1]) for i in range(1, period + 1)]
    losses = [max(0, prices[i - 1] - prices[i]) for i in range(1, period + 1)]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def verificar_sinal(symbol, price, agora):
    prices = list(price_history[symbol])
    if len(prices) < 14:
        return None

    rsi_valor = rsi(prices[-14:])
    if rsi_valor is None or not (RSI_MIN < rsi_valor < RSI_MAX):
        return None

    center = sum(prices[-14:]) / len(prices[-14:])
    sma = prices[-1]  # média de 1 período (último preço)
    distancia = abs(center - sma) / sma

    ultima_entrada = last_entry_time.get(symbol)
    ultima_reentrada = last_distance_reentry_time.get(symbol)

    if distancia >= DISTANCE_THRESHOLD:
        if ultima_reentrada is None or (agora - ultima_reentrada) >= timedelta(minutes=DISTANCE_REENTRY_INTERVAL_MINUTES):
            last_distance_reentry_time[symbol] = agora
            print(f"[REENTRADA] {symbol} | Preço: {price:.4f} | RSI: {rsi_valor:.2f} | Distância: {distancia:.4f}")
            return "BUY"

    if prices[-2] < center and prices[-1] > center:
        if ultima_entrada is None or (agora - ultima_entrada) >= timedelta(minutes=TIMEFRAME_RESTRICTION_MINUTES):
            last_entry_time[symbol] = agora
            print(f"[ENTRADA CROSS] {symbol} | Preço: {price:.4f} | RSI: {rsi_valor:.2f}")
            return "BUY"

    return None

def entrar_trade(symbol, direcao, preco, agora):
    print(f"[SINAL] {symbol} | {direcao} | Entrada: {preco:.4f} | Horário: {agora}")

def atualizar_trades(symbol, price):
    price_history[symbol].append(price)

async def stream_bingx():
    uri = "wss://open-api-swap.bingx.com/swap-market"
    while True:
        try:
            async with websockets.connect(uri, ping_interval=None) as ws:
                for symbol in SYMBOLS:
                    sub_msg = {
                        "id": symbol,
                        "reqType": "sub",
                        "dataType": f"trade.{symbol}",
                        "dataSize": 1
                    }
                    await ws.send(json.dumps(sub_msg))
                print("[INFO] Conectado ao WebSocket da BingX")

                while True:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=30)
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
                    except asyncio.TimeoutError:
                        print("[TIMEOUT] Sem mensagem por 30s. Enviando ping...")
                        await ws.ping()
                    except Exception as e:
                        print("[ERRO INTERNO]", e)
        except Exception as e:
            print("[ERRO DE CONEXÃO]", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(stream_bingx())
