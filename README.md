# 🧬 Sistema-X — Sistema de Triagem Clínica para Síndrome do X Frágil (SXF)

Sistema web para apoio à triagem clínica da Síndrome do X Frágil (SXF) e ao acompanhamento da jornada do paciente no contexto do Instituto IBK.

O Sistema-X permite cadastrar pacientes, registrar familiares, anexar documentos anteriores, conduzir pré-avaliação, calcular score clínico, registrar encaminhamento para exame genético, acompanhar o recebimento do resultado e documentar o suporte pós-diagnóstico.

## 📌 Objetivo

Apoiar profissionais da saúde e equipes técnicas na organização da jornada do paciente com suspeita de SXF, reduzindo perda de informações entre cadastro, triagem, exame, resultado e suporte familiar.

O sistema também busca manter registros compatíveis com boas práticas de proteção de dados, com campos para consentimento, autorização de comunicação e documentação de finalidade assistencial.

## 🧭 Jornada Atendida

O fluxo implementado segue a jornada levantada para o Instituto:

1. Cadastro do paciente.
2. Recepção pela equipe técnica.
3. Avaliação da requisição médica.
4. Triagem clínica e socioeconômica.
5. Encaminhamento para realização do exame.
6. Recebimento do resultado.
7. Suporte pós-diagnóstico.

Para resultados positivos, o sistema permite registrar:

- Acolhimento familiar.
- Aconselhamento genético.
- Inserção em atividades do Programa Eu Digo X.

Para resultados negativos, o sistema permite registrar:

- Orientações sobre outras possibilidades diagnósticas.
- Encaminhamento para grupos de apoio ou assessoramento.

## ✨ Funcionalidades

### 👤 Autenticação

- Login de profissionais.
- Cadastro de usuários.
- Senhas armazenadas com hash.
- Controle de acesso às áreas internas.

### 🩺 Gestão de Pacientes

- Dados cadastrais e de contato.
- Nome social.
- Origem do encaminhamento.
- Endereço.
- Status atual na jornada.
- Avaliação da requisição médica.
- Triagem clínica.
- Triagem socioeconômica.
- Características físicas.
- Fotos de rosto, perfil e lado.
- Registro de conformidade LGPD.
- Autorização para envio de e-mails.

### 👥 Familiares

- Cadastro de familiares vinculados ao paciente.
- Indicação de cadastro antes ou após avaliação.
- Contato telefônico e e-mail.
- Observações por familiar.

### 📁 Documentos Anteriores

- Registro de avaliações anteriores.
- Requisições médicas.
- Resultados de exames.
- Outros documentos relevantes.
- Upload de arquivos associados ao paciente.

### 📋 Avaliação Clínica

- Checklist de sintomas associados à SXF.
- Registro de sintomas cognitivos, físicos e comportamentais.
- Cálculo automático do score clínico.
- Aplicação de pesos por sintoma e por sexo.
- Comparação automática com limiar de decisão.

### 🧠 Triagem Inteligente

- Registro do resultado do exame.
- Classificação do tipo do resultado.
- Registro de encaminhamento para exame.
- Plano pós-diagnóstico.
- Suporte pós-diagnóstico.
- Geração de documento textual da jornada do paciente.
- Envio de e-mail via SMTP quando configurado.

### 📊 Histórico e Relatórios

- Dashboard com métricas gerais.
- Histórico de avaliações.
- Relatórios analíticos com gráficos Plotly.
- Exportação de pacientes para Excel.
- Exportação de avaliações para Excel.

# ⚙️ Regras de Negócio

O score é calculado pela soma ponderada dos sintomas presentes:

```text
Score = soma(peso do sintoma presente)
```

Limiares padrão:

| Sexo      | Limiar |
| --------- | -----: |
| Masculino |   0.56 |
| Feminino  |   0.55 |

Quando o score é maior ou igual ao limiar, o sistema recomenda encaminhamento para teste genético confirmatório.

# 🛠 Tecnologias Utilizadas

- Python
- Flask
- SQLAlchemy
- MySQL
- PyMySQL
- Pandas
- Plotly
- OpenPyXL
- HTML
- CSS
- JavaScript

# 🏗️ Arquitetura do Projeto

```text
Sistema-X/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── assessments/
│   ├── auth/
│   ├── dashboard/
│   ├── patients/
│   ├── reports/
│   ├── settings/
│   ├── services/
│   │   ├── exports.py
│   │   ├── reports.py
│   │   └── seed_data.py
│   ├── shared/
│   ├── static/
│   ├── templates/
│   └── uploads/
├── config.py
├── requirements.txt
├── run.py
├── seed.py
└── .env.example
```

# 🔐 Configuração do Ambiente

Crie e ative o ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

# ⚙️ Configuração do Banco

Copie o arquivo de exemplo:

```powershell
copy .env.example .env
```

Configure o `.env` com os dados do MySQL:

```env
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sistema-x
SECRET_KEY=sua_chave_secreta
```

Também é possível informar a URL completa:

```env
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/sistema-x
```

Ao iniciar a aplicação, o sistema cria o banco se ele não existir, cria as tabelas necessárias e aplica migrações simples para colunas novas.

# 📎 Configuração de Uploads

Por padrão, arquivos enviados ficam em:

```text
app/uploads/
```

É possível alterar o diretório com:

```env
UPLOAD_FOLDER=C:\caminho\para\uploads
```

O limite padrão de upload é 16 MB e pode ser alterado com:

```env
MAX_CONTENT_LENGTH=16777216
```

# ✉️ Configuração de E-mail

Para habilitar envio direto de e-mails, configure:

```env
SMTP_HOST=smtp.exemplo.com
SMTP_PORT=587
SMTP_USER=usuario
SMTP_PASSWORD=senha
SMTP_FROM=sistema-x@exemplo.com
```

Sem SMTP configurado, a tela de resultado ainda pode abrir o cliente de e-mail do usuário com assunto e corpo preenchidos.

# ▶️ Executando

Inicie a aplicação:

```powershell
python run.py
```

Acesse:

```text
http://127.0.0.1:5000
```

# 🌱 Dados Iniciais

Use o seed Python para popular o MySQL configurado no `.env`:

```powershell
python seed.py
```

O seed cria ou atualiza:

- profissional demonstrativo;
- sintomas;
- pesos por sexo;
- limiares de decisão;
- pacientes demonstrativos;
- familiares;
- documentos anteriores.

Usuário demonstrativo:

```text
E-mail: contato@sxf.com
Senha: 123456
```

# 🗄 Modelo de Dados

Principais entidades:

- `profissional`
- `paciente`
- `familiar_paciente`
- `documento_paciente`
- `sintoma`
- `peso_sintoma`
- `limiar_decisao`
- `avaliacao`
- `avaliacao_sintoma`

Consultas úteis:

```sql
SELECT * FROM profissional;
SELECT * FROM paciente;
SELECT * FROM familiar_paciente;
SELECT * FROM documento_paciente;
SELECT * FROM avaliacao;
SELECT * FROM sintoma;
```

# 📈 Requisitos Não Funcionais

O Sistema-X trabalha com dados pessoais e dados sensíveis de saúde. Por isso, o projeto inclui registros de:

- consentimento para tratamento de dados sensíveis;
- autorização para comunicação por e-mail;
- observações sobre finalidade e contexto do tratamento;
- controle de acesso por login;
- senhas com hash;
- documentação da jornada do paciente.

Em ambiente real, recomenda-se complementar a aplicação com políticas institucionais de retenção, backup, auditoria, revisão de acessos e descarte seguro de dados.

# ✅ Validação Local

Com o ambiente virtual ativo:

```powershell
python -m compileall app
```

Também é recomendado executar o seed e abrir as principais telas:

- Dashboard.
- Pacientes.
- Cadastro de paciente.
- Nova triagem.
- Histórico.
- Relatórios.

# 🚀 Fluxo de Desenvolvimento

Fluxo sugerido:

```powershell
git checkout develop
git pull
git checkout -b nome-da-branch
git add .
git commit -m "Descrição da alteração"
git push origin nome-da-branch
```

Depois, abrir Pull Request para revisão.

# 👥 Equipe

| Integrante           | GitHub                            |
| -------------------- | --------------------------------- |
| Gabriel Schwerdt     | https://github.com/StringSchwerdt |
| Millena Gurczakovski | https://github.com/MillenaGur     |
| Sérgio Calazans      | https://github.com/sergiocalazans |

# 📄 Licença

Projeto acadêmico desenvolvido para a disciplina Experiência Criativa: Criando Soluções Computacionais, PUCPR.
