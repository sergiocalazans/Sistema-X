# Roteiro explicativo: instalacao, Docker, Git e Railway

Duracao sugerida: ate 10 minutos

## 0:00 a 0:40 - Apresentacao

**Cena:** mostrar o README ou o sistema aberto.

**Narracao:**
Neste video vou demonstrar como instalar, executar e publicar o Sistema-X usando Git, Docker e Railway. O Sistema-X e uma aplicacao Flask com banco MySQL para triagem clinica da Sindrome do X Fragil, com cadastro de pacientes, avaliacoes, dashboard e relatorios.

## 0:40 a 1:40 - Instalando Git e Docker

**Cena:** mostrar os sites oficiais do Git e Docker Desktop.

**Narracao:**
Para executar o projeto com Docker, precisamos instalar duas ferramentas. A primeira e o Git, usado para clonar o repositorio do projeto. A segunda e o Docker Desktop, que vai executar os containers da aplicacao e do banco de dados.

No Windows, o Docker Desktop utiliza WSL 2 como backend. Depois da instalacao, abrimos o terminal e validamos:

```powershell
git --version
docker --version
docker compose version
```

Se esses comandos retornarem as versoes instaladas, o ambiente esta pronto.

## 1:40 a 2:30 - Clonando o projeto

**Cena:** terminal no VS Code ou PowerShell.

**Narracao:**
Agora clonamos o projeto do GitHub:

```powershell
git clone https://github.com/seu-usuario/Sistema-X.git
cd Sistema-X
```

Para usar a versao preparada com Docker, acessamos a branch:

```powershell
git checkout feature/docker
```

Dentro da pasta do projeto, temos arquivos importantes como `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `seed.py` e `run.py`.

## 2:30 a 4:00 - Executando localmente com Docker

**Cena:** mostrar o `docker-compose.yml` e executar o comando no terminal.

**Narracao:**
Com Docker, nao precisamos instalar Python, MySQL nem as bibliotecas manualmente. O Compose sobe dois servicos: o container `web`, com a aplicacao Flask rodando via Gunicorn, e o container `mysql`, com o banco MySQL.

Para construir e subir tudo, executamos:

```powershell
docker compose up --build
```

Na primeira execucao, o Docker baixa as imagens e instala as dependencias. Quando os containers estiverem ativos, abrimos outro terminal e populamos o banco:

```powershell
docker compose exec web python seed.py
```

Esse comando cria os dados demonstrativos, incluindo usuarios, pacientes, avaliacoes e encaminhamentos.

## 4:00 a 5:00 - Acessando o sistema

**Cena:** navegador em `http://localhost:5000`.

**Narracao:**
Depois que o container web estiver rodando, acessamos:

```text
http://localhost:5000
```

Para entrar como administrador:

```text
E-mail: contato@sxf.com
Senha: 123456
```

Tambem existem os acessos:

```text
triagem@sxf.com
relatorios@sxf.com
Senha: 123456
```

O administrador consegue visualizar os pacientes, incluindo o profissional vinculado. O visualizador consegue acessar dashboard e relatorios com os dados gerais do sistema.

## 5:00 a 6:10 - Publicando a branch no GitHub

**Cena:** terminal com comandos Git.

**Narracao:**
Antes de publicar no Railway, enviamos a branch com Docker para o GitHub:

```powershell
git status
git add .
git commit -m "feat: add docker deployment support"
git push -u origin feature/docker
```

O arquivo `.env` nao deve ser enviado ao GitHub, porque pode conter senhas e chaves secretas. As variaveis de producao serao cadastradas diretamente no Railway.

## 6:10 a 7:20 - Criando o banco MySQL no Railway

**Cena:** painel do Railway.

**Narracao:**
No Railway, criamos um novo projeto. Dentro dele, clicamos em `+ New`, selecionamos `Database` e escolhemos `MySQL`.

Quando o banco for criado, o Railway disponibiliza variaveis como:

```env
MYSQLHOST
MYSQLPORT
MYSQLUSER
MYSQLPASSWORD
MYSQLDATABASE
MYSQL_URL
```

Essas informacoes serao usadas pelo servico web para se conectar ao banco.

## 7:20 a 8:30 - Publicando o site no Railway

**Cena:** criar servico conectado ao GitHub.

**Narracao:**
Agora criamos o servico web. No mesmo projeto Railway, clicamos em `+ New`, selecionamos `GitHub Repo` e escolhemos o repositorio do Sistema-X.

Selecionamos a branch `feature/docker`. Como existe um arquivo `Dockerfile` na raiz, o Railway detecta automaticamente que deve construir o container usando Docker.

Depois configuramos as variaveis do servico web:

```env
MYSQL_USER=${{MySQL.MYSQLUSER}}
MYSQL_PASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQL_HOST=${{MySQL.MYSQLHOST}}
MYSQL_PORT=${{MySQL.MYSQLPORT}}
MYSQL_DATABASE=${{MySQL.MYSQLDATABASE}}
SECRET_KEY=uma-chave-secreta-forte
```

Se o servico MySQL tiver outro nome, ajustamos o prefixo das referencias.

## 8:30 a 9:20 - Dominio e seed em producao

**Cena:** tela de `Settings > Networking`.

**Narracao:**
Com o deploy concluido, abrimos o servico web, entramos em `Settings`, depois `Networking`, e em `Public Networking` clicamos em `Generate Domain`.

O Railway gera um dominio `.railway.app` com HTTPS automatico.

Depois, executamos o seed uma vez no ambiente do servico web:

```bash
python seed.py
```

Isso popula o banco de producao com os dados demonstrativos.

## 9:20 a 10:00 - Encerramento

**Cena:** sistema rodando no Railway.

**Narracao:**
Com isso, o Sistema-X esta instalado localmente com Docker e tambem publicado em nuvem pelo Railway. Vimos a instalacao do Git e Docker, o clone do repositorio, a execucao local, a populacao do banco, o acesso ao sistema, a criacao do banco MySQL no Railway, o deploy do site e a geracao do dominio publico.

Para encerrar a execucao local, usamos:

```powershell
docker compose down
```

E, se quisermos apagar o banco local e comecar do zero:

```powershell
docker compose down -v
```
