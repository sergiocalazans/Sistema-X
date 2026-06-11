# Sistema-X - Sistema de Triagem Clínica para Síndrome do X Frágil (SXF)

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-2563eb)
![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-16a34a)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-web-000000?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-banco%20de%20dados-4479A1?logo=mysql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-interface-7952B3?logo=bootstrap&logoColor=white)

Sistema web de triagem clínica para apoio à identificação de sinais relacionados à Síndrome do X Frágil (SXF). A aplicação foi desenvolvida para auxiliar profissionais da saúde no cadastro de pacientes, registro de avaliações, acompanhamento de encaminhamentos e geração de relatórios administrativos.

O projeto organiza informações clínicas, histórico familiar, documentos, fotos e indicadores em uma interface web construída com Flask. A partir das respostas da avaliação, o sistema calcula um score ponderado por sexo, aplica limiares configurados e sugere se o caso deve ser priorizado para encaminhamento.

## 🧭 Sumário

- [✨ Funcionalidades](#funcionalidades)
- [🔐 Regras de acesso](#regras-de-acesso)
- [🩺 Regras de triagem](#regras-de-triagem)
- [🛠️ Tecnologias](#tecnologias)
- [🏗️ Arquitetura](#arquitetura)
- [▶️ Como executar](#como-executar)
- [🔑 Acessos de demonstração](#acessos-de-demonstração)
- [🗄️ Modelo de dados](#modelo-de-dados)
- [📊 Relatórios](#relatórios)
- [✅ Validação local](#validação-local)
- [🚀 Fluxo de desenvolvimento](#fluxo-de-desenvolvimento)
- [🎥 Vídeo tutorial do sistema](#vídeo-tutorial-do-sistema)
- [🎬 Vídeo de explicação do projeto](#vídeo-de-explicação-do-projeto)
- [👥 Colaboradores](#colaboradores)
- [📄 Licença](#licença)
- [🎓 Projeto universitário](#projeto-universitário)

## ✨ Funcionalidades

- Autenticação de usuários com controle de sessão.
- Níveis de acesso por perfil: administrador, profissional da saúde e visualizador.
- Cadastro administrativo de usuários, disponível apenas para administradores.
- Exclusão de usuários com mensagem de confirmação.
- Cadastro de usuários com senha padrão e obrigatoriedade de troca no primeiro acesso.
- Remoção de dados preenchidos automaticamente nas telas de login e cadastro.
- Cadastro completo de pacientes, incluindo dados pessoais, dados de contato, informações clínicas, familiares, fotos e documentos.
- Registro de avaliações de triagem com sintomas, score calculado, recomendação e observações.
- Registro e acompanhamento de encaminhamentos.
- Dashboard com indicadores, gráficos e análises dos dados cadastrados.
- Tela de relatórios com tabelas completas, gráficos, indicadores e exportação.
- Geração de relatório em PDF com tabelas estruturadas, texto em preto e bordas em preto.
- Exportação de dados tabulares para planilhas.
- Banco de dados populado com dados de demonstração para testes e apresentação.
- Layout responsivo para uso em desktop, tablet e celular.

## 🔐 Regras de acesso

| Perfil                | Permissões principais                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------- |
| Administrador         | Acessa todos os dados do sistema, gerencia usuários, visualiza dashboards globais, relatórios e cadastros. |
| Profissional da saúde | Registra pacientes, avaliações e encaminhamentos vinculados ao seu uso profissional.                       |
| Visualizador          | Consulta dashboards e relatórios, sem alterar dados sensíveis do sistema.                                  |

Usuários cadastrados pelo administrador recebem uma senha padrão. No primeiro acesso, o sistema direciona o usuário para a tela de atualização de senha antes de liberar as demais funcionalidades.

## 🩺 Regras de triagem

- Cada sintoma possui peso definido na aplicação.
- O score final é calculado a partir dos sintomas marcados durante a avaliação.
- O limiar de priorização varia conforme o sexo do paciente.
- Quando o score atinge ou ultrapassa o limiar, o sistema recomenda encaminhamento.
- Quando o score fica abaixo do limiar, o caso permanece como não prioritário, mas ainda pode ser acompanhado pela equipe.

## 🛠️ Tecnologias

| Camada           | Tecnologias                                                                                                                                                                                                                                                                                                                                         |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Backend          | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)                                                                                      |
| Banco de dados   | ![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white) ![PyMySQL](https://img.shields.io/badge/PyMySQL-003B57)                                                                                                                                                                                                              |
| Interface        | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=white) |
| Gráficos e dados | ![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white) ![OpenPyXL](https://img.shields.io/badge/OpenPyXL-217346)                                                                                                                       |
| Relatórios       | ![ReportLab](https://img.shields.io/badge/ReportLab-PDF-b91c1c)                                                                                                                                                                                                                                                                                     |

## 🏗️ Arquitetura

O projeto foi modularizado seguindo boas práticas de desenvolvimento web com Flask. As rotas foram organizadas em blueprints, os serviços concentram regras reutilizáveis e os templates foram separados por contexto funcional.

```text
Sistema-X/
├── app/
│   ├── __init__.py              # Fábrica da aplicação Flask
│   ├── blueprints.py            # Registro central dos blueprints
│   ├── config.py                # Configurações da aplicação
│   ├── database.py              # Instância do SQLAlchemy
│   ├── models.py                # Modelos do banco de dados
│   ├── security.py              # Regras de acesso e autenticação
│   ├── template_context.py      # Contexto compartilhado dos templates
│   ├── auth/                    # Login, logout e troca de senha
│   ├── dashboard/               # Indicadores e visões analíticas
│   ├── patients/                # Cadastro e consulta de pacientes
│   ├── referrals/               # Encaminhamentos
│   ├── reports/                 # Relatórios, exportações e PDF
│   ├── triage/                  # Avaliações de triagem
│   ├── users/                   # Gestão administrativa de usuários
│   ├── services/
│   │   ├── dashboard.py         # Dados para painéis e gráficos
│   │   ├── pdf_reports.py       # Montagem dos relatórios em PDF
│   │   └── triage.py            # Cálculo de score e recomendação
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   └── templates/
│       ├── auth/
│       ├── dashboard/
│       ├── patients/
│       ├── referrals/
│       ├── reports/
│       ├── triage/
│       └── users/
├── run.py                       # Ponto de entrada da aplicação
├── requirements.txt             # Dependências do projeto
└── seed.py                      # Popular banco com dados de exemplo
```

## ▶️ Como executar

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar banco de dados

Crie um banco MySQL e configure as variáveis de ambiente conforme a sua máquina:

```bash
set FLASK_SECRET_KEY=sua-chave-secreta
set DB_USER=root
set DB_PASSWORD=sua-senha
set DB_HOST=localhost
set DB_PORT=3306
set DB_NAME=sxf_triagem
```

Quando as variáveis não forem informadas, a aplicação usa os valores padrão definidos em `app/config.py`.

### 4. Popular dados de demonstração

```bash
python seed.py
```

Esse comando cria dados iniciais de usuários, pacientes, avaliações e encaminhamentos para testes e apresentação.

### 5. Iniciar aplicação

```bash
python run.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

## 🔑 Acessos de demonstração

| Perfil                | E-mail               | Senha    |
| --------------------- | -------------------- | -------- |
| Administrador         | `contato@sxf.com`    | `123456` |
| Profissional da saúde | `triagem@sxf.com`    | `123456` |
| Visualizador          | `relatorios@sxf.com` | `123456` |

Usuários criados pela tela administrativa também iniciam com a senha padrão `123456` e devem atualizar a senha no primeiro acesso.

## 🗄️ Modelo de dados

| Entidade       | Descrição                                                                                       |
| -------------- | ----------------------------------------------------------------------------------------------- |
| Usuário        | Representa os usuários do sistema, seus perfis, status e controle de primeiro acesso.           |
| Paciente       | Armazena dados pessoais, contato, documentos, fotos, informações clínicas e histórico familiar. |
| Avaliação      | Registra sintomas, score, limiar, recomendação, etapa, resultado e observações da triagem.      |
| Encaminhamento | Controla solicitações, prioridades, status e acompanhamento dos pacientes encaminhados.         |

## 📊 Relatórios

A tela de relatórios apresenta indicadores gerais, análises por período, distribuição de resultados, sintomas frequentes, lista de avaliações e dados de encaminhamentos.

O sistema permite gerar PDF com:

- Indicadores principais.
- Gráficos analíticos.
- Tabelas completas de avaliações e encaminhamentos.
- Texto e bordas em preto para melhorar legibilidade na impressão.

Também há exportação de dados para planilhas quando a análise precisar ser complementada fora do sistema.

## ✅ Validação local

Antes de entregar alterações, recomenda-se executar:

```bash
python -m compileall app
python seed.py
python run.py
```

Depois, validar no navegador:

- Login e logout.
- Troca obrigatória de senha no primeiro acesso.
- Cadastro, edição e exclusão de usuários pelo administrador.
- Cadastro e consulta de pacientes.
- Registro de avaliações.
- Registro de encaminhamentos.
- Dashboard e relatórios.
- Impressão e exportação de PDF.
- Responsividade em diferentes tamanhos de tela.

## 🚀 Fluxo de desenvolvimento

1. Criar uma branch para a funcionalidade ou correção.
2. Implementar a alteração respeitando a modularização existente.
3. Validar manualmente as telas afetadas.
4. Executar verificações locais.
5. Registrar commits com mensagens claras, iniciadas por `feat`, `fix`, `docs`, `refactor`, `style` ou `chore`.

## 🎥 Vídeo tutorial do sistema

Adicione aqui o link do vídeo tutorial de uso do sistema:

[Link do vídeo tutorial do sistema](#)

## 🎬 Vídeo de explicação do projeto

Adicione aqui o link do vídeo de explicação do projeto:

[Link do vídeo de explicação do projeto](#)

## 👥 Colaboradores

| Nome                 | GitHub                                               |
| -------------------- | ---------------------------------------------------- |
| Gabriel Schwerdt     | [@StringSchwerdt](https://github.com/StringSchwerdt) |
| Millena Gurczakovski | [@MillenaGur](https://github.com/MillenaGur)         |
| Sérgio Calazans      | [@sergiocalazans](https://github.com/sergiocalazans) |

## 📄 Licença

Distribuído conforme a licença disponível em [LICENSE](LICENSE).

## 🎓 Projeto universitário

Projeto acadêmico desenvolvido para a disciplina **Experiência Criativa: Criando Soluções Computacionais**, da **Pontifícia Universidade Católica do Paraná (PUCPR)**.
