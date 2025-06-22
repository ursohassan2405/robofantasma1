import websocket

def on_message(ws, message):
    print(f"Mensagem recebida: {message}")

def on_error(ws, error):
    print(f"Erro: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Conexão encerrada")

def on_open(ws):
    print("Conexão aberta")
    ws.send("ping")

if __name__ == "__main__":
    socket = "wss://stream.binance.com:9443/ws/pendleusdt@trade"
    ws = websocket.WebSocketApp(socket,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()