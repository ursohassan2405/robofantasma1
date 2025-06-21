
import websocket
import threading
import time
import json
import gzip
import ssl

# Lista de ativos para monitorar
symbols = ["BTC-USDT", "ETH-USDT", "NEAR-USDT", "SOL-USDT", "TIA-USDT", "RENDER-USDT", "ONDO-USDT", "AI16Z-USDT"]

def on_message(ws, message):
    try:
        if isinstance(message, bytes):
            message = gzip.decompress(message).decode('utf-8')
        data = json.loads(message)
        print("📥 Mensagem recebida:", data)
    except Exception as e:
        print("❌ Erro ao processar mensagem:", e)

def on_error(ws, error):
    print("⚠️ Erro na conexão:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 Conexão encerrada. Código:", close_status_code, "Mensagem:", close_msg)
    print("⏳ Tentando reconectar em 5 segundos...")
    time.sleep(5)
    start_websocket(symbols)  # reconectar

def on_open(ws):
    print("✅ Conexão WebSocket estabelecida com sucesso!")
    for symbol in symbols:
        subscribe_message = {
            "id": int(time.time()*1000),
            "event": "sub",
            "topic": f"/market/trade:{symbol}"
        }
        ws.send(json.dumps(subscribe_message))
        print(f"📡 Inscrito no par {symbol}")

def start_websocket(symbols):
    ws = websocket.WebSocketApp(
        "wss://open-api-swap.bingx.com/swap-market",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    # Rodar em thread separada com SSL desabilitado para ambiente Render
    wst = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
    wst.daemon = True
    wst.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        ws.close()

# Iniciar o WebSocket
start_websocket(symbols)
