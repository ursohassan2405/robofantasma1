
import os

def upload_to_github():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Token não encontrado. Verifique a variável de ambiente GITHUB_TOKEN.")
    print("Token obtido com sucesso (oculto por segurança).")
    # Aqui você continua com o restante da lógica de upload...

if __name__ == "__main__":
    upload_to_github()
