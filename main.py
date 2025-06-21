
import requests

def obter_preco_atual():
    try:
        url = "https://api.bingx.com/api/v1/market/kline?symbol=NEAR-USDT&interval=1m&limit=1"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            preco = float(data['data'][0]['close'])
            return preco
        else:
            print("Formato inesperado de resposta da API:", data)
            return None
    except Exception as e:
        print("Erro ao obter preço atual:", e)
        return None

# Execução de teste para debug
if __name__ == "__main__":
    preco = obter_preco_atual()
    if preco is not None:
        print("Preço atual:", preco)
    else:
        print("Falha ao obter preço.")
