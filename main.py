
import time
import csv
import os
from datetime import datetime
import random

ativos = ["NEAR/USDT", "RENDER/USDT", "SOL/USDT", "TIA/USDT", "PENDLE/USDT", "ONDO/USDT", "AI16Z/USDT"]
ativos_em_operacao = set()

valor_operacao = 10  # USDT
stop_loss_pct = 2.0  # %
trailing_stop_ativo = False
breakeven_ativo = False

log_file = "log_operacoes.csv"

# Inicializa CSV se não existir
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Token", "Timestamp", "Tipo", "Preco_Entrada", "SL", "TP", "BE_Ativo", "Trailing_Ativo", "Preco_Saida", "Resultado_%"])

def simula_preco():
    return round(random.uniform(1.5, 4.0), 4)

while True:
    for ativo in ativos:
        if ativo not in ativos_em_operacao:
            preco_entrada = simula_preco()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Simulação de saída aleatória
            resultado_pct = round(random.uniform(-3, 5), 2)
            preco_saida = round(preco_entrada * (1 + resultado_pct / 100), 4)

            # Salva no CSV
            with open(log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    ativo,
                    timestamp,
                    "BUY",
                    preco_entrada,
                    round(preco_entrada * (1 - stop_loss_pct / 100), 4),
                    "",  # TP não fixo
                    int(breakeven_ativo),
                    int(trailing_stop_ativo),
                    preco_saida,
                    resultado_pct
                ])

            # Marca como operando (poderia sair depois de N segundos, aqui é instantâneo para simulação)
            ativos_em_operacao.add(ativo)
            print(f"[BUY] {ativo} - {timestamp} - Entrada: {preco_entrada} - Resultado: {resultado_pct}%")

            # Libera o ativo para nova operação
            ativos_em_operacao.remove(ativo)

    # Atualiza no GitHub
    os.system("git add log_operacoes.csv")
    os.system('git commit -m "update log"')
    os.system("git push origin main")

    time.sleep(1)
