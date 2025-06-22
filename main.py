import asyncio
import websockets
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque

SYMBOLS = ["NEAR-USDT", "RENDER-USDT", "SOL-USDT", "TIA-USDT", "PENDLE-USDT", "ONDO-USDT", "AI16Z-USDT"]
SL_PCT = 0.02
BE_PCT = 0.01
TRAILING_PCT = 0.036
VALOR_USDT = 10
LOG_FILE = "log_operacoes.csv"

price_history = {symbol: deque(maxlen=120) for symbol in SYMBOLS}
last_indicator_update = {symbol: None for symbol in SYMBOLS}
indicators_cache = {}
center_cache = {}
sma_cache = {}

trades = {symbol: [] for symbol in SYMBOLS}
last_entry_time = {symbol: None for symbol in SYMBOLS}
last_distance_reentry_time = {symbol: None for symbol in SYMBOLS}

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Token", "Timestamp_UTC", "Timestamp_BR", "Tipo", "Preco_Entrada",
                          "SL", "TP", "BE_Ativo", "Trailing_Ativo", "Preco_Saida", "Resultado_%"]
                ).to_csv(LOG_FILE, index=False)

def now_utc():
    return datetime.utcnow()

def now_br():
    return now_utc() - timedelta(hours=3)

def log_trade(symbol, entrada, saida, sl, tipo, be, trailing):
    resultado_pct = round((saida - entrada) / entrada * 100, 2) if tipo == "BUY" else round((entrada - saida) / entrada * 100, 2)
    row = {
        "Token": symbol.replace("-", "/"),
        "Timestamp_UTC": now_utc().strftime("%Y-%m-%d %H:%M:%S"),
        "Timestamp_BR": now_br().strftime("%Y-%m-%d %H:%M:%S"),
        "Tipo": tipo,
        "Preco_Entrada": round(entrada, 4),
        "SL": round(sl, 4),
        "TP": "",
        "BE_Ativo": int(be),
        "Trailing_Ativo": int(trailing),
        "Preco_Saida": round(saida, 4),
        "Resultado_%": resultado_pct
    }
    print(f"[{row['Timestamp_BR']}] SAÍDA {symbol} a {saida:.4f} | Resultado: {resultado_pct}%")
    pd.DataFrame([row]).to_csv(LOG_FILE, mode='a', header=False, index=False)

def calcular_indicadores(symbol):
    closes = np.array(price_history[symbol])
    if len(closes) < 50:
        return None
    rsi_period = 13
    delta = np.diff(closes)
    gain = np.mean(np.maximum(delta[-rsi_period:], 0))
    loss = np.mean(np.maximum(-delta[-rsi_period:], 0))
    rs = gain / loss if loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    sma = np.mean(closes[-1:])  # média de 1 período (último preço)
    center = (max(closes[-1], closes[-2]) + min(closes[-1], closes[-2]) + closes[-1]) / 3
    indicators_cache[symbol] = {
        "RSI": rsi,
        "MA1": sma,
        "CENTER": center
    }
    sma_cache[symbol] = sma
    center_cache[symbol] = center

def verificar_sinal(symbol, price, timestamp):
    if last_indicator_update[symbol] is None or (timestamp - last_indicator_update[symbol]).total_seconds() >= 14400:
        calcular_indicadores(symbol)
        last_indicator_update[symbol] = timestamp
    indic = indicators_cache.get(symbol, {})
    if not indic:
        return None
    dist1 = abs(price - indic["CENTER"]) / indic["CENTER"]
    dist2 = abs(price - indic["MA1"]) / indic["MA1"]
    if dist1 >= 0.02 and dist2 >= 0.02:
        if price > indic["MA1"] and 35 < indic["RSI"] < 73:
            return "BUY"
        if price < indic["MA1"] and 35 < indic["RSI"] < 73:
            return "SELL"
        if last_distance_reentry_time[symbol] is None or (timestamp - last_distance_reentry_time[symbol]).total_seconds() >= 900:
            last_distance_reentry_time[symbol] = timestamp
            return "BUY" if price > indic["MA1"] else "SELL"
    return None

def entrar_trade(symbol, tipo, price, timestamp):
    if tipo == "BUY" and any(pos["tipo"] == "BUY" for pos in trades[symbol]):
        return
    if tipo == "SELL" and any(pos["tipo"] == "SELL" for pos in trades[symbol]):
        return
    sl = price * (1 - SL_PCT) if tipo == "BUY" else price * (1 + SL_PCT)
    tp1 = price * (1 + BE_PCT) if tipo == "BUY" else price * (1 - BE_PCT)
    trade = {
        "tipo": tipo,
        "entrada": price,
        "sl": sl,
        "tp1": tp1,
        "be": False,
        "trailing": False,
        "max_price": price,
        "min_price": price
    }
    trades[symbol].append(trade)
    last_entry_time[symbol] = timestamp
    print(f"[{now_br().strftime('%Y-%m-%d %H:%M:%S')}] ENTRADA {tipo} {symbol} a {price:.4f}")

def atualizar_trades(symbol, price):
    ativos = trades[symbol]
    novos_ativos = []
    for pos in ativos:
        pos["max_price"] = max(pos["max_price"], price)
        pos["min_price"] = min(pos["min_price"], price)
        if not pos["be"] and ((pos["tipo"] == "BUY" and price >= pos["tp1"]) or (pos["tipo"] == "SELL" and price <= pos["tp1"])):
            pos["sl"] = pos["entrada"]
            pos["be"] = True
            print(f"[{now_br().strftime('%Y-%m-%d %H:%M:%S')}] BREAK-EVEN {symbol}")
        if pos["be"]:
            trailing_price = pos["max_price"] * (1 - TRAILING_PCT) if pos["tipo"] == "BUY" else pos["min_price"] * (1 + TRAILING_PCT)
            if (pos["tipo"] == "BUY" and trailing_price > pos["sl"]) or (pos["tipo"] == "SELL" and trailing_price < pos["sl"]):
                pos["sl"] = trailing_price
                pos["trailing"] = True
        stop_triggered = (price <= pos["sl"] if pos["tipo"] == "BUY" else price >= pos["sl"])
        if stop_triggered:
            log_trade(symbol, pos["entrada"], price, pos["sl"], pos["tipo"], pos["be"], pos["trailing"])
        else:
            novos_ativos.append(pos)
    trades[symbol] = novos_ativos

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
                print("[INFO] Conectado ao WebSocket da BingX")
                while True:
                    try:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if "data" in data and isinstance(data["data"], list) and "symbol" in data:
                            price = float(data["data"][0]["price"])
                            symbol = data["symbol"]
                            agora = datetime.utcnow()
                            price_history[symbol].append(price)
                            atualizar_trades(symbol, price)
                            direcao = verificar_sinal(symbol, price, agora)
                            if direcao:
                                entrar_trade(symbol, direcao, price, agora)
                    except Exception as e:
                        print("[ERRO INTERNO]", e)
        except Exception as e:
            print("[ERRO DE CONEXÃO]", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("[START] BOTTOMAN V1 - Entradas reais + RSI + trailing + distância + short e long")
    asyncio.run(stream_bingx())