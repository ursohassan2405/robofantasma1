
import time
import requests

# Função para obter o último candle 4h da BingX com retry
def obter_candle_4h_bingx(symbol="NEAR-USDT"):
    url = "https://open-api.bingx.com/openApi/quote/v1/kline"
    params = {
        "symbol": symbol,
        "interval": "4h",
        "limit": 1
    }
    while True:
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    candle = data["data"][0]
                    print(f"[{datetime.now()}] Candle 4h capturado com sucesso: {candle}")
                    return candle
                else:
                    print(f"[{datetime.now()}] Nenhum dado retornado. Repetindo em 60s...")
            else:
                print(f"[{datetime.now()}] Erro HTTP {response.status_code}. Repetindo em 60s...")
        except Exception as e:
            print(f"[{datetime.now()}] Erro ao conectar com a API da BingX: {e}. Tentando novamente em 60s...")
        time.sleep(60)

# Exemplo de uso
if __name__ == "__main__":
    candle = obter_candle_4h_bingx("NEAR-USDT")
    # Aqui seguiria a lógica para iniciar o robô após obter o candle
