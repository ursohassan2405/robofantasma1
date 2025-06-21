import time
import datetime

print("[01] Inicializando robô fantasma...")

ativos = ["NEAR/USDT", "TIA/USDT", "RNDR/USDT"]
while True:
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for ativo in ativos:
        print(f"[{agora}] Escaneando ativo: {ativo}")
        # Simulação de entrada/saída
        print(f"[{agora}] Nenhum sinal encontrado para {ativo} no momento.")
    time.sleep(60)
