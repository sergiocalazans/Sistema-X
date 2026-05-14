# Sistema-X
Sistema de Triagem Clinica para a Sindrome do X Fragil (SXF).

## Banco de dados

O projeto usa SQLAlchemy com MySQL. Configure a conexao pelo `DATABASE_URL`:

```powershell
$env:DATABASE_URL = "mysql+pymysql://usuario:senha@localhost:3306/sistema_x"
python run.py
```

Se `DATABASE_URL` nao for informado, sera usado:

```text
mysql+pymysql://root:root@localhost:3306/sistema_x
```

O comando `python run.py` cria o banco `sistema_x`, caso ele nao exista, e cria as tabelas conforme o modelo fisico.
