# 🧬 Sistema-X — Sistema de Triagem Clínica para Síndrome do X Frágil (SXF)

O **Sistema-X** é uma aplicação web desenvolvida para auxiliar profissionais da saúde na **triagem clínica da Síndrome do X Frágil (SXF)**, contribuindo para a identificação precoce de pacientes com maior probabilidade de apresentar a condição e apoiando decisões sobre encaminhamento para testes genéticos confirmatórios.

A plataforma permite o cadastro de pacientes, realização de avaliações clínicas com base em sintomas associados à SXF, cálculo automatizado de score clínico e armazenamento do histórico de triagens realizadas.

---

## 📌 Objetivo

Reduzir o subdiagnóstico da **Síndrome do X Frágil**, padronizando avaliações clínicas e auxiliando profissionais da saúde na priorização de encaminhamentos para exames genéticos.

---

## ✨ Funcionalidades

### 👤 Autenticação

- Login de profissionais da saúde
- Cadastro de usuários
- Senhas armazenadas com hash
- Controle de acesso ao sistema

### 🩺 Gestão de Pacientes

- Cadastro de pacientes
- Edição de informações cadastrais
- Registro de:
  - Nome
  - Idade
  - Sexo biológico

### 📋 Avaliação Clínica

- Checklist de sintomas associados à SXF
- Registro de sintomas cognitivos, físicos e comportamentais
- Cálculo automático do score clínico
- Aplicação de pesos específicos por sintoma
- Comparação automática com limiares definidos por sexo

### 🧠 Triagem Inteligente

- Recomendação automática de encaminhamento para teste genético
- Classificação do paciente:
  - Prioritário
  - Não prioritário

### 📊 Histórico e Relatórios

- Histórico de avaliações realizadas
- Dashboard com métricas gerais
- Indicadores estatísticos
- Relatórios analíticos com gráficos Plotly
- Exportação para Excel

---

# ⚙️ Regras de Negócio

O sistema segue as seguintes regras principais:

### Cálculo do Score Clínico

O score é obtido pela soma ponderada dos sintomas:

```text
Score = Σ(peso × presença_do_sintoma)
```

Onde:

- Sintoma presente → `1`
- Sintoma ausente → `0`

### Limiares de decisão

| Sexo      | Limiar |
| --------- | ------ |
| Masculino | 0.56   |
| Feminino  | 0.55   |

### Encaminhamento

Se:

```text
Score ≥ limiar
```

Resultado:

```text
Encaminhar para teste genético confirmatório
```

Caso contrário:

```text
Paciente não prioritário no momento
```

---

# 🏗️ Arquitetura do Projeto

O sistema segue arquitetura modular baseada em Flask:

```text
Sistema-X/
│
├── app/
│   ├── __init__.py              # Factory Flask
│   ├── database.py              # Configuração banco
│   ├── models.py                # Modelos SQLAlchemy
│   │
│   ├── controllers/
│   │      main.py               # Rotas/API
│   │
│   ├── services/
│   │      seed_data.py          # Dados iniciais
│   │      reports.py            # Relatórios
│   │      exports.py            # Exportação
│   │
│   ├── templates/
│   │      index.html
│   │      partials/
│   │
│   └── static/
│          ├── css/
│          └── js/
│                ├── core/
│                ├── pages/
│                ├── services/
│                └── ui/
│
├── config.py
├── run.py
├── seed.py
├── requirements.txt
└── .env.example
```

---

# 🛠 Tecnologias Utilizadas

## Back-end

- Python
- Flask
- SQLAlchemy
- PyMySQL

## Banco de Dados

- SQL
- MySQL

## Front-end

- HTML5
- CSS3
- JavaScript Modular

## Relatórios e Dados

- Pandas
- Plotly
- OpenPyXL

## Desenvolvimento

- VS Code
- Git
- GitHub

---

# 🔐 Configuração do Ambiente

Clone o projeto:

```bash
git clone URL_DO_REPOSITORIO
```

Entre na pasta:

```bash
cd Sistema-X
```

Crie o ambiente virtual:

Windows:

```powershell
python -m venv venv
```

Ative:

```powershell
.\venv\Scripts\activate
```

Instale dependências:

```powershell
pip install -r requirements.txt
```

---

# ⚙️ Configuração do Banco

Copie:

```powershell
copy .env.example .env
```

Configure:

```env
MYSQL_USER=root
MYSQL_PASSWORD=senha

MYSQL_HOST=localhost
MYSQL_PORT=3306

MYSQL_DATABASE=sistema_x

SECRET_KEY=sua_chave
```

Ou:

```env
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/sistema_x
```

---

# ▶️ Executando

Inicie:

```powershell
python run.py
```

Acesse:

```text
http://127.0.0.1:5000
```

Ao iniciar:

✅ Cria banco automaticamente  
✅ Cria tabelas  
✅ Sincroniza dados iniciais  
✅ Configura ambiente do MVP

---

# 🌱 Dados Iniciais

Popular banco:

```powershell
python seed.py
```

Usuário demonstrativo:

```text
Email:
contato@sxf.com

Senha:
123456
```

---

# 🗄 Modelo de Dados

Principais entidades:

- profissional
- paciente
- sintoma
- peso_sintoma
- avaliacao
- avaliacao_sintoma
- limiar_decisao

Consultar:

```sql
SELECT * FROM profissional;
SELECT * FROM paciente;
SELECT * FROM avaliacao;
SELECT * FROM sintoma;
```

---

# 📈 Requisitos Não Funcionais

O sistema deve:

- Executar cálculos em até **2 segundos**
- Garantir confidencialidade dos dados
- Possuir interface intuitiva
- Permitir manutenção modular
- Suportar backups periódicos
- Possibilitar expansão futura

---

# 🚀 Fluxo de Desenvolvimento

Desenvolvimento ocorre em:

```text
develop
```

Fluxo:

```powershell
git checkout develop

git add .

git commit -m "Descrição"

git push origin develop
```

Após concluir:

Criar Pull Request:

```text
develop → main
```

---

# 👥 Equipe

| Integrante           | GitHub                            |
| -------------------- | --------------------------------- |
| Gabriel Schwerdt     | https://github.com/StringSchwerdt |
| Millena Gurczakovski | https://github.com/MillenaGur     |
| Sérgio Calazans      | https://github.com/sergiocalazans |

---

# 📄 Licença

Projeto acadêmico desenvolvido para a disciplina **Experiência Criativa: Criando Soluções Computacionais** — PUCPR.
