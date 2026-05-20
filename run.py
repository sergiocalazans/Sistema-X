# run.py
import os
from app import create_app

# Cria a instância da aplicação através da Factory
app = create_app()

if __name__ == "__main__":
    # Obtém configurações de ambiente ou usa padrões para desenvolvimento
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")

    print(f"\n >>> Iniciando o Sistema-X em http://{host}:{port}")
    print(" >>> Pressione CTRL+C para encerrar.\n")

    app.run(
        host=host,
        port=port,
        debug=debug
    )