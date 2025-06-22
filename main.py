
import time
from datetime import datetime, timedelta

# Simula análise de sinais
def detectar_sinais():
    return ["SOL/USDT", "RENDER/USDT", "TIA/USDT", "ONDO/USDT", "AI16Z/USDT", "NEAR/USDT", "PENDLE/USDT"]

# Parâmetros
stop_loss = 2.0
quantidade = 10
intervalo_reentrada_min = 10

# Histórico dos últimos sinais (em memória)
historico_sinais = {}

print("Robô iniciado em", datetime.now())

while True:
    sinais = detectar_sinais()
    agora = datetime.now()

    for par in sinais:
        ultimo = historico_sinais.get(par)

        if not ultimo or (agora - ultimo) > timedelta(minutes=intervalo_reentrada_min):
            print(f"[BUY] {par} - Qtd: {quantidade} - SL: {stop_loss}%")
            historico_sinais[par] = agora
        else:
            tempo_restante = intervalo_reentrada_min - (agora - ultimo).seconds // 60
            print(f"[IGNORADO] {par} - aguardando {tempo_restante} min para nova entrada")

    time.sleep(1)
