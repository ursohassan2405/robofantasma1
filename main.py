import asyncio
import websockets
import json
import datetime
import pandas as pd
import os

SYMBOL = "PENDLE-USDT"
LOG_FILE = "log_operacoes.csv"

# Inicializar CSV se não existir
def inicializar_csv():
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=["timestamp", "price"])
        df.to_csv(LOG_FILE, index=False)

# Processar cada mensagem recebida
async def processar_mensagem(msg):
    try:
        data = json.loads(msg)
        if "data" in data:
            trades = data["data"]
            for trade in trades:
                timestamp = datetime.datetime.fromtimestamp(trade["T"] / 1000)
                price = float(trade["p"])
                print(f"[{timestamp}] Preço: {price}")
                df = pd.DataFrame([[timestamp, price]], columns=["timestamp", "price"])
                df.to_csv(LOG_FILE, mode='a', header=False, index=False)
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

# Loop principal de conexão
async def conectar():
    uri = "wss://open-api-swap.bingx.com/swap-market"
    async with websockets.connect(uri) as ws:
        msg_sub = json.dumps({
            "op": "subscribe",
            "args": [f"trade.{SYMBOL}"]
        })
        await ws.send(msg_sub)

        print(f"✅ Conectado e inscrito no canal trade.{SYMBOL}")

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=20)
                await processar_mensagem(message)
            except asyncio.TimeoutError:
                print("⏳ Timeout. Enviando ping para manter conexão...")
                try:
                    await ws.send("ping")
                except:
                    print("❌ Falha ao enviar ping.")
                    break
            except websockets.ConnectionClosed:
                print("🔌 Conexão encerrada.")
                break
            except Exception as e:
                print(f"⚠️ Erro inesperado: {e}")
                continue

if __name__ == "__main__":
    inicializar_csv()
    asyncio.run(conectar())
