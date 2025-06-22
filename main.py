
import websocket
import gzip
import json
import time
from datetime import datetime

symbol = "PENDLE-USDT"
stream_url = f"wss://open-api.bingx.com/market/ws"

mm1_4h = None

def atualizar_mm1(candle_timestamp, close_price):
    global mm1_4h
    if candle_timestamp % 14400 == 0:
        mm1_4h = close_price
        print(f"✅ MM1 atualizada para: {mm1_4h} às {datetime.utcfromtimestamp(candle_timestamp)}")

def on_message(ws, message):
    try:
        decompressed_data = gzip.decompress(message)
        data = json.loads(decompressed_data.decode('utf-8'))
        if "data" in data and "kline" in data["data"]:
            kline = data["data"]["kline"]
            ts = int(kline["t"]) // 1000
            close = float(kline["c"])
            atualizar_mm1(ts, close)
    except Exception as e:
        print("Erro ao processar mensagem:", e)

def on_error(ws, error):
    print("Erro:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 Conexão encerrada.")

def on_open(ws):
    print("✅ Conectado e inscrito no canal trade." + symbol)
    subscribe_msg = {
        "id": "mm1",
        "reqType": "sub",
        "dataType": f"kline_{symbol}_14400"
    }
    ws.send(json.dumps(subscribe_msg))

def run():
    while True:
        try:
            ws = websocket.WebSocketApp(stream_url,
                                        on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever(ping_interval=20)
        except Exception as e:
            print("Erro na conexão websocket:", e)
        time.sleep(5)

if __name__ == "__main__":
    run()
