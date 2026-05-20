# Sistema-X

Sistema web de triagem clínica para Síndrome do X Frágil (SXF). O projeto integra front-end, back-end Flask e banco de dados MySQL para cadastrar profissionais, pacientes, sintomas e avaliações clínicas.

## Funcionalidades

- Login e cadastro de profissionais com senha armazenada em hash.
- Cadastro e edição de pacientes.
- Checklist de sintomas associados a SXF.
- Cálculo automático do score clínico por soma ponderada.
- Comparacao do score com limiar por sexo.
- Recomendacao automatica de encaminhamento para teste genetico.
- Histórico de avaliações realizadas.
- Dashboard com totais e avaliações recentes.
- Relatórios com indicadores calculados em pandas e gráficos Plotly.
- Exportação de pacientes e histórico de avaliações para Excel.

## Tecnologias

- Python
- Flask
- SQLAlchemy
- MySQL
- PyMySQL
- HTML, CSS e JavaScript modular

## Estrutura

```text
Sistema-X/
  app/
    __init__.py              # Factory da aplicacao Flask
    database.py              # Engine, sessoes e criacao do banco/tabelas
    models.py                # Modelos SQLAlchemy
    controllers/
      main.py                # Rotas web e APIs JSON
    services/
      seed_data.py           # Dados padrao do MVP e seed
      reports.py             # Indicadores e gráficos dos relatórios
      exports.py             # Exportação Excel de pacientes e avaliações
    static/
      css/
        styles.css
      js/
        app.js               # Entrada principal do front-end
        core/                # Estado, icones e roteamento
        pages/               # Renderizacao das telas
        services/            # Chamadas HTTP e carregamento de dados
        ui/                  # Templates, formatadores, login e shell
    templates/
      index.html             # Pagina base
      partials/              # Templates HTML das telas
  config.py                  # Configuracoes e leitura do .env
  run.py                     # Inicializacao da aplicacao
  seed.py                    # Popula/sincroniza dados iniciais
  requirements.txt
  .env.example
```

## Configuracao

Crie um arquivo `.env` a partir do exemplo:

```powershell
copy .env.example .env
```

Edite o `.env` com os dados do seu MySQL:

```text
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sistema-x
SECRET_KEY=troque-essa-chave
```

Tambem e possivel configurar tudo por `DATABASE_URL`:

```powershell
$env:DATABASE_URL = "mysql+pymysql://usuario:senha@localhost:3306/sistema-x"
```

## Como Executar

Ative o ambiente virtual:

```powershell
.\venv\Scripts\activate
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Execute a aplicacao:

```powershell
python run.py
```

Acesse:

```text
http://127.0.0.1:5000
```

Ao iniciar, o sistema cria o banco, caso ele não exista, cria as tabelas e sincroniza os dados base do MVP.

## Dados Iniciais

Para popular pacientes demonstrativos, limiares, sintomas e pesos:

```powershell
python seed.py
```

Usuario demo:

```text
E-mail: contato@sxf.com
Senha: 123456
```

## Banco de Dados

Principais tabelas:

- `profissional`
- `paciente`
- `sintoma`
- `peso_sintoma`
- `limiar_decisao`
- `avaliacao`
- `avaliacao_sintoma`

Consultar todas:

```sql
SELECT * FROM profissional;
SELECT * FROM paciente;
SELECT * FROM sintoma;
SELECT * FROM peso_sintoma;
SELECT * FROM limiar_decisao;
SELECT * FROM avaliacao;
SELECT * FROM avaliacao_sintoma;
```

## Fluxo de Desenvolvimento

O desenvolvimento atual esta na branch `develop`. Depois de finalizar uma etapa:

```powershell
git status
git add .
git commit -m "Mensagem do commit"
git push origin develop
```

Depois disso, crie um Pull Request de `develop` para `main` no GitHub.
