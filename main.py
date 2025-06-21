
import asyncio
import websockets
import json
from datetime import datetime
import csv

# Configurações
SYMBOLS = ["NEAR-USDT", "FETCH-USDT", "SOL-USDT", "RENDER-USDT", "TIA-USDT", "ONDO-USDT", "AI16Z-USDT"]
LOG_FILE = "log_operacoes.csv"

# Parâmetros de entrada e controle
SL_PERCENT = 0.02
TP_TRAIL_START = 0.036
TRAIL_OFFSET = 0.03
BE_AT = 0.02

# Estado das posições
posicoes_abertas = {}

# Inicialização do arquivo de log
with open(LOG_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Token", "Timestamp", "Tipo", "Preco_Entrada", "SL", "TP", "BE_Ativo",
        "Trailing_Ativo", "Preco_Saida", "Resultado_%"
    ])

# Estratégia simplificada para teste: entra em compra se não há posição e registra simulação
async def processar_tick(symbol, price):
    global posicoes_abertas

    agora = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    token = symbol.replace("-", "/")

    if token not in posicoes_abertas:
        preco_entrada = float(price)
        sl = preco_entrada * (1 - SL_PERCENT)
        tp_inicial = preco_entrada * (1 + TP_TRAIL_START)
        posicoes_abertas[token] = {
            "entrada": preco_entrada,
            "sl": sl,
            "tp": tp_inicial,
            "tipo": "BUY",
            "be_ativo": False,
            "trailing_ativo": False,
            "max_price": preco_entrada
        }
        with open(LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                token, agora, "BUY", round(preco_entrada, 6), round(sl, 6),
                round(tp_inicial, 6), "N", "N", "", ""
            ])
    else:
        pos = posicoes_abertas[token]
        preco_atual = float(price)

        if not pos["be_ativo"] and preco_atual >= pos["entrada"] * (1 + BE_AT):
            pos["be_ativo"] = True
            pos["sl"] = pos["entrada"]

        if preco_atual > pos["max_price"]:
            pos["max_price"] = preco_atual

        if preco_atual >= pos["entrada"] * (1 + TP_TRAIL_START):
            pos["trailing_ativo"] = True
            trailing_sl = pos["max_price"] * (1 - TRAIL_OFFSET)
            pos["sl"] = max(pos["sl"], trailing_sl)

        if preco_atual <= pos["sl"]:
            resultado = (preco_atual - pos["entrada"]) / pos["entrada"]
            with open(LOG_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    token, agora, "SAIDA", round(pos["entrada"], 6), round(pos["sl"], 6),
                    round(pos["tp"], 6), "Y" if pos["be_ativo"] else "N",
                    "Y" if pos["trailing_ativo"] else "N", round(preco_atual, 6),
                    f"{round(resultado * 100, 2)}%"
                ])
            del posicoes_abertas[token]

# Conexão WebSocket BingX
async def websocket_bingx():
    uri = "wss://open-api-swap.bingx.com/swap-market"
    async with websockets.connect(uri) as ws:
        # Subscrição nos pares
        subs = [{"event": "subscribe", "topic": f"trade:{symbol}"} for symbol in SYMBOLS]
        for sub in subs:
            await ws.send(json.dumps(sub))

        print("Conectado ao WebSocket da BingX. Aguardando ticks...")
        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if "data" in data and "price" in data["data"]:
                symbol = data["symbol"]
                price = data["data"]["price"]
                await processar_tick(symbol, price)

asyncio.run(websocket_bingx())
