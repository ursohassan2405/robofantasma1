import time
import requests

def executar_ordem_bingx(tipo, par, quantidade, sl, api_key, api_secret):
    print(f"[{tipo.upper()}] {par} - Qtd: {quantidade} - SL: {sl}%")
    # Aqui entra a lógica real da BingX com envio de ordens

ativos = ['NEAR/USDT', 'PENDLE/USDT', 'SOL/USDT', 'RENDER/USDT', 'TIA/USDT', 'ONDO/USDT', 'AI16Z/USDT']

while True:
    for par in ativos:
        # Simulação de lógica: leitura de sinal (ex: RSI, Pivot, etc.)
        # Entrada (exemplo) se condição atender:
        executar_ordem_bingx('buy', par, 10, 2.0, 'SUA_API_KEY', 'SUA_API_SECRET')
    time.sleep(1)  # Executa a cada segundo
