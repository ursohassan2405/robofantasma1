
import asyncio
import websockets
import json
from datetime import datetime
import logging

# Ativos a serem monitorados
ATIVOS = ["NEAR_USDT", "SOL_USDT", "RENDER_USDT"]

# Configuração do logger
logging.basicConfig(
    filename="log_operacoes.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

async def conectar_websocket(ativo):
    url = f"wss://open-api-swap.bingx.com/swap-market"
    async with websockets.connect(url) as ws:
        # Assinatura do canal de trade do ativo
        subscribe_msg = {
            "id": "tick_monitor",
            "reqType": "sub",
            "dataType": f"trade#symbol={ativo}",
        }
        await ws.send(json.dumps(subscribe_msg))
        logging.info(f"[{ativo}] Conectado e inscrito no WebSocket.")
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                if 'data' in data:
                    for tick in data['data']:
                        preco = tick['price']
                        volume = tick['size']
                        logging.info(f"[TICK] {ativo} | Preço: {preco} | Volume: {volume}")
                        # Simulação de sinal de entrada
                        if float(volume) > 1:
                            logging.info(f"[SINAL] {ativo} | Entrada simulada | Preço: {preco}")
            except Exception as e:
                logging.error(f"[ERRO] {ativo} | {e}")
                break

async def main():
    logging.info("Iniciando monitoramento tick-a-tick em todos os ativos.")
    await asyncio.gather(*(conectar_websocket(ativo) for ativo in ATIVOS))

if __name__ == "__main__":
    asyncio.run(main())
