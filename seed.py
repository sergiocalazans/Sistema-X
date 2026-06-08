import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.database import init_db
from app.services.seed_data import sync_mvp_defaults


def run_seed():
    print("--- Iniciando popular banco de dados (seed) ---")
    flask_app = create_app()

    with flask_app.app_context():
        init_db()
        result = sync_mvp_defaults(include_demo_patients=True)

        if result["profissional_created"]:
            print("Usuários demonstrativos criados.")
        else:
            print("Usuários demonstrativos encontrados. Atualizando credenciais.")

        print("--- Sucesso: banco sincronizado com usuários, pacientes, avaliações e encaminhamentos. ---")


if __name__ == "__main__":
    run_seed()
