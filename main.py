import time
from datetime import datetime
import requests
import csv

# ====== CONFIGURAÇÕES BÁSICAS ======
PAIR = "NEAR-USDT"
INTERVAL = "1m"
BINGX_API_KEY = "SUA_API_KEY"
BINGX_API_SECRET = "SUA_API_SECRET"
MODO_FANTASMA = True
VALOR_POR_TRADE = 10
SL_PCT = 0.02
BE_PCT = 0.01
TRIGGER_TRAIL_PCT = 0.036
LOCKIN_TRAIL_PCT = 0.03

# ====== ESTADO DA OPERAÇÃO ======
em_posicao = False
preco_entrada = 0
trailing_ativo = False
ponto_trailing = 0
log_operacoes = []

# ====== FUNÇÃO MOCK DE PREÇO DA BINGX ======
def obter_preco_atual():
    r = requests.get(f"https://api.bingx.com/api/v1/market/kline?symbol={PAIR}&interval=1m&limit=1")
    data = r.json()
    preco = float(data['data'][0]['close'])
    return preco

# ====== LOOP PRINCIPAL ======
while True:
    preco = obter_preco_atual()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not em_posicao:
        preco_entrada = preco
        em_posicao = True
        trailing_ativo = False
        ponto_trailing = 0
        log_operacoes.append(["ENTRADA", agora, preco])
        print(f"[{agora}] ENTRADA em {preco}")
    else:
        lucro_pct = (preco - preco_entrada) / preco_entrada

        if not trailing_ativo and lucro_pct >= TRIGGER_TRAIL_PCT:
            trailing_ativo = True
            ponto_trailing = preco * (1 - LOCKIN_TRAIL_PCT)
            print(f"[{agora}] TRAILING ativado. Stop inicial em {ponto_trailing:.4f}")

        if trailing_ativo:
            novo_trailing = preco * (1 - LOCKIN_TRAIL_PCT)
            if novo_trailing > ponto_trailing:
                ponto_trailing = novo_trailing
                print(f"[{agora}] TRAILING atualizado para {ponto_trailing:.4f}")

            if preco <= ponto_trailing:
                em_posicao = False
                log_operacoes.append(["SAIDA-TRAIL", agora, preco])
                print(f"[{agora}] SAÍDA pela trailing em {preco}")
        else:
            if preco <= preco_entrada * (1 - SL_PCT):
                em_posicao = False
                log_operacoes.append(["STOP LOSS", agora, preco])
                print(f"[{agora}] SAÍDA pelo STOP LOSS em {preco}")

    time.sleep(3)  # Espera 3 segundos entre os checks

# ====== SALVA O CSV ======
with open("operacoes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["TIPO", "DATA_HORA", "PRECO"])
    writer.writerows(log_operacoes)
