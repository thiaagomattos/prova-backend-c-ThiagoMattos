# Prova Backend C - Thiago Mattos Silveira

Repositório desenvolvido como parte do desafio técnico para a vaga de **Backend Python** na IPM Sistemas.

O projeto consiste no desenvolvimento de uma **API RESTful para gerenciamento de missões de drones**, com autenticação JWT, processamento de imagens utilizando um modelo de IA previamente treinado, registro do histórico de predições e execução containerizada com Docker.

A aplicação foi desenvolvida em **Python com FastAPI**, utilizando **PostgreSQL** como banco de dados, **Redis** como serviço de infraestrutura preparado para operações de cache e processamento assíncrono, e **Docker Compose** para orquestração do ambiente local.

---

## 📋 Índice

* [Sobre o projeto](#sobre-o-projeto)
* [Tecnologias utilizadas](#tecnologias-utilizadas)
* [Arquitetura](#arquitetura)
* [Funcionalidades](#funcionalidades)
* [Modelo de dados](#modelo-de-dados)
* [Como executar o projeto](#como-executar-o-projeto)
* [API](#api)
* [Autenticação](#autenticação)
* [Integração com IA](#integração-com-ia)
* [Docker e infraestrutura](#docker-e-infraestrutura)
* [Questões teóricas](#questões-teóricas)
* [Questões extras](#questões-extras)
* [Uso de IA](#uso-de-ia)
* [Portfólio](#portfólio)

---

# Sobre o projeto

O projeto simula uma API utilizada em um ambiente de processamento de imagens capturadas por drones.

A aplicação possui duas responsabilidades principais:

1. Gerenciamento das missões realizadas pelos drones;
2. Recebimento e processamento de imagens utilizando um modelo de Inteligência Artificial.

A API disponibiliza operações CRUD para as missões, autenticação utilizando JWT e um endpoint responsável por executar inferências em imagens.

Cada processamento registra informações como versão do modelo utilizado, tempo de inferência, status da execução e resultado das predições.

A aplicação também foi preparada para execução utilizando Docker Compose, contendo os seguintes serviços:

* API FastAPI;
* PostgreSQL;
* Redis.

---

# Tecnologias utilizadas

## Backend

* Python 3.12
* FastAPI
* Pydantic
* SQLAlchemy
* JWT
* Uvicorn

## Banco de dados

* PostgreSQL
* SQLite — utilizado durante a implementação inicial da Parte 2

## Inteligência Artificial

* Ultralytics
* YOLO
* Modelo pré-treinado `yolo26n`

## Infraestrutura

* Docker
* Docker Compose
* Redis

## Ferramentas

* Git
* GitHub
* Postman
* Swagger / OpenAPI

---

# Arquitetura

A arquitetura atual da aplicação pode ser representada da seguinte forma:

```text
                         ┌─────────────────────┐
                         │       Cliente       │
                         │ Swagger / Postman   │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │        API          │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌────────────┐  ┌──────────────┐  ┌───────────┐
             │ PostgreSQL │  │  AI Service   │  │   Redis   │
             │            │  │              │  │           │
             │ Missions   │  │ YOLO model   │  │ Cache /   │
             │ Users      │  │ Inference    │  │ Future    │
             │ History    │  │              │  │ Queue     │
             └────────────┘  └──────────────┘  └───────────┘
```

## PostgreSQL

O PostgreSQL é utilizado como banco de dados principal da aplicação.

Ele armazena as entidades persistentes do sistema, incluindo:

* Usuários;
* Missões;
* Histórico dos processamentos;
* Resultados das predições.

Durante a implementação inicial da Parte 2 foi utilizado SQLite para simplificar o desenvolvimento do CRUD. Na etapa de containerização, a aplicação foi migrada para PostgreSQL, que é o banco solicitado no desafio e é mais adequado para um ambiente com múltiplos usuários e múltiplas instâncias da API.

Dessa forma, **não existe necessidade de manter SQLite e PostgreSQL simultaneamente na versão final da aplicação**.

## Redis

O Redis faz parte da infraestrutura da aplicação e está disponível no Docker Compose.

Redis é uma estrutura de dados em memória com baixa latência, sendo uma opção adequada para funcionalidades que não precisam ser armazenadas diretamente no banco relacional.

Neste projeto, ele está preparado para uma futura evolução da arquitetura, principalmente para:

* Cache;
* Controle de estado de processamento;
* Filas de tarefas;
* Comunicação entre API e workers;
* Controle de jobs em processamento.

O processamento síncrono implementado atualmente utiliza diretamente o serviço de IA. Para cargas maiores, o Redis pode ser utilizado como parte de uma arquitetura assíncrona com workers.

---

# Funcionalidades

## Gerenciamento de missões

A API permite:

* Criar uma missão;
* Listar missões;
* Consultar uma missão por ID;
* Atualizar uma missão;
* Excluir uma missão.

Cada missão possui:

| Campo           | Descrição                 |
| --------------- | ------------------------- |
| `id`            | Identificador único       |
| `name`          | Nome da missão            |
| `status`        | Status da missão          |
| `created_at`    | Data e hora de criação    |
| `drone_model`   | Modelo do drone utilizado |
| `image_count`   | Quantidade de imagens     |
| `area_hectares` | Área coberta em hectares  |

---

# Modelo de dados

A aplicação utiliza PostgreSQL como banco principal.

Uma representação simplificada das entidades é:

```text
┌──────────────────────┐
│        users         │
├──────────────────────┤
│ id                   │
│ username             │
│ password_hash        │
└──────────┬───────────┘
           │
           │
           ▼
┌──────────────────────┐
│       missions       │
├──────────────────────┤
│ id                   │
│ name                 │
│ status               │
│ created_at           │
│ drone_model          │
│ image_count          │
│ area_hectares        │
└──────────┬───────────┘
           │
           │ 1:N
           ▼
┌──────────────────────────┐
│   processing_history     │
├──────────────────────────┤
│ id                       │
│ mission_id               │
│ model_version            │
│ status                   │
│ inference_time           │
│ predictions              │
│ error_message            │
│ created_at               │
└──────────────────────────┘
```

O relacionamento entre missão e histórico permite registrar várias execuções de processamento para uma mesma missão.

---

# Como executar o projeto

## Pré-requisitos

Para executar a versão containerizada, é necessário possuir:

* Docker Desktop;
* Docker Compose;
* Git.

## 1. Clone o repositório

```bash
git clone <REPOSITORY_URL>
```

## 2. Acesse o diretório

```bash
cd challenge-ipm
```

## 3. Configure as variáveis de ambiente

Crie o arquivo `.env` utilizando `.env.example` como referência.

Exemplo:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/challenge_ipm

SECRET_KEY=sua_chave_secreta
ALGORITHM=HS256

AI_MODEL_PATH=yolo26n.pt
AI_MODEL_VERSION=1.0.0

REDIS_URL=redis://redis:6379/0
```

O arquivo `.env` não deve ser versionado no Git.

## 4. Execute os serviços

```bash
docker compose up --build
```

Para executar em segundo plano:

```bash
docker compose up -d --build
```

## 5. Verifique os containers

```bash
docker compose ps
```

Os serviços esperados são:

```text
api
db
redis
```

O PostgreSQL e o Redis possuem healthchecks configurados.

## 6. Acesse a documentação

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Healthcheck:

```text
http://localhost:8000/health
```

## 7. Encerrar a aplicação

```bash
docker compose down
```

Para remover também os volumes persistentes:

```bash
docker compose down -v
```

---

# API

A API segue os princípios REST e possui documentação automática através do FastAPI/OpenAPI.

## Autenticação

| Método | Endpoint         | Descrição                   | Autenticação |
| ------ | ---------------- | --------------------------- | ------------ |
| `POST` | `/auth/register` | Cria usuário                | Não          |
| `POST` | `/auth/login`    | Realiza login e retorna JWT | Não          |

## Missões

| Método   | Endpoint         | Descrição       | Autenticação |
| -------- | ---------------- | --------------- | ------------ |
| `POST`   | `/missions/`     | Cria missão     | Sim          |
| `GET`    | `/missions/`     | Lista missões   | Sim          |
| `GET`    | `/missions/{id}` | Busca missão    | Sim          |
| `PUT`    | `/missions/{id}` | Atualiza missão | Sim          |
| `DELETE` | `/missions/{id}` | Remove missão   | Sim          |

## Processamento

| Método | Endpoint                            | Descrição          | Autenticação |
| ------ | ----------------------------------- | ------------------ | ------------ |
| `POST` | `/missions/{id}/process`            | Processa imagem    | Sim          |
| `GET`  | `/missions/{id}/processing-history` | Consulta histórico | Sim          |

---

# Autenticação

A API utiliza **JSON Web Tokens (JWT)** para proteger os endpoints.

O fluxo é:

```text
POST /auth/register
        │
        ▼
POST /auth/login
        │
        ▼
     JWT Token
        │
        ▼
Authorization: Bearer <token>
        │
        ▼
Endpoints protegidos
```

Após o login, a API retorna um token:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

O token deve ser enviado nas requisições protegidas através do header:

```text
Authorization: Bearer <token>
```

No Swagger, o botão **Authorize** pode ser utilizado para informar o token e testar os endpoints protegidos.

---

# Integração com IA

A terceira etapa do desafio solicitava a utilização de um modelo previamente treinado.

Como nenhum modelo foi disponibilizado junto ao desafio, foi utilizado um modelo público pré-treinado da família **YOLO**, através da biblioteca Ultralytics.

O modelo utilizado foi:

```text
yolo26n.pt
```

A escolha foi feita por ser um modelo pré-treinado disponível publicamente e adequado para demonstrar o fluxo de inferência de detecção de objetos.

## Fluxo

```text
POST /missions/{id}/process
          │
          ▼
     Validação JWT
          │
          ▼
    Busca da missão
          │
          ▼
     Upload da imagem
          │
          ▼
      AIService
          │
          ▼
     YOLO Model
          │
          ▼
      Inferência
          │
          ├── Predições
          ├── Confiança
          ├── Bounding boxes
          └── Tempo
          │
          ▼
 Processing History
          │
          ▼
       Response
```

## Requisitos implementados

### Modelo carregado apenas uma vez

O modelo é inicializado uma única vez pelo serviço responsável pela IA, evitando carregar os pesos novamente a cada requisição.

Isso reduz o custo de inicialização e melhora o tempo de resposta após o carregamento inicial.

### Tratamento de erros

Erros relacionados ao processamento são tratados para evitar que uma falha na inferência resulte em uma resposta inesperada da API.

O histórico também pode registrar o status da execução e uma mensagem de erro quando aplicável.

### Tempo de inferência

O tempo necessário para executar a inferência é medido e armazenado no histórico.

Exemplo:

```json
{
  "inference_time": 0.108
}
```

### Versionamento do modelo

Cada processamento registra a versão do modelo utilizada.

Exemplo:

```json
{
  "model_version": "1.0.0"
}
```

Isso permite identificar posteriormente qual versão do modelo foi responsável por determinada predição.

### Histórico

Cada processamento gera um registro contendo informações como:

* Missão;
* Versão do modelo;
* Status;
* Tempo de inferência;
* Predições;
* Bounding boxes;
* Confiança;
* Mensagem de erro, quando aplicável;
* Data e hora.

---

# Docker e infraestrutura

A aplicação utiliza Docker Compose para executar os serviços necessários:

```text
                    Docker Compose
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
      ┌───────┐      ┌──────────┐   ┌─────────┐
      │  API  │      │PostgreSQL│   │  Redis  │
      │FastAPI│      │          │   │         │
      └───────┘      └──────────┘   └─────────┘
```

## API

A aplicação FastAPI é executada dentro de um container baseado em Python.

O servidor Uvicorn é exposto na porta:

```text
8000
```

## PostgreSQL

O PostgreSQL é utilizado como banco relacional principal.

A aplicação aguarda o PostgreSQL estar saudável antes de iniciar, utilizando `depends_on` com healthcheck no Docker Compose.

## Redis

O Redis é executado como serviço independente.

A aplicação possui a variável:

```env
REDIS_URL=redis://redis:6379/0
```

Isso permite que o Redis seja utilizado posteriormente para cache ou processamento assíncrono sem precisar alterar a infraestrutura.

## Variáveis de ambiente

Informações sensíveis e configurações específicas do ambiente não são armazenadas diretamente no código.

Exemplos:

```env
DATABASE_URL
SECRET_KEY
ALGORITHM
AI_MODEL_PATH
AI_MODEL_VERSION
REDIS_URL
```

O `.env` está incluído no `.gitignore`, enquanto `.env.example` é versionado para documentar as configurações necessárias.

## Healthcheck

A aplicação possui:

```text
GET /health
```

Exemplo:

```json
{
  "status": "ok"
}
```

O Docker também utiliza esse endpoint para verificar a saúde da API.

---

# Questões teóricas

## Por que utilizar Redis neste cenário?

O Redis é interessante nesse cenário principalmente por sua baixa latência e por permitir implementar mecanismos que não precisam utilizar o banco relacional para todas as operações.

Um dos principais usos seria o gerenciamento de tarefas assíncronas.

Por exemplo, uma requisição de processamento de imagem poderia gerar um job e colocá-lo em uma fila. Um worker retiraria esse job da fila e executaria a inferência.

```text
API
 │
 ▼
Redis / Queue
 │
 ├── Job 1
 ├── Job 2
 ├── Job 3
 └── ...
      │
      ▼
   Workers
```

Além disso, o Redis poderia ser utilizado para:

* Cache de informações acessadas frequentemente;
* Controle de status de processamento;
* Filas de tarefas;
* Rate limiting;
* Armazenamento temporário.

No projeto atual, o Redis está disponível como serviço de infraestrutura, mas o processamento de IA ainda é realizado de forma síncrona. Para uma arquitetura de maior escala, eu evoluiria essa parte para processamento assíncrono utilizando Redis como parte da fila de tarefas.

---

# Como escalaria a aplicação para processar milhares de imagens simultaneamente?

Eu separaria o recebimento das requisições do processamento das imagens.

A API não deveria executar diretamente uma tarefa que pode durar vários minutos.

Uma arquitetura possível seria:

```text
                    Load Balancer
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          API #1       API #2      API #3
             │           │           │
             └───────────┼───────────┘
                         ▼
                    Redis / Queue
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          Worker #1   Worker #2   Worker #N
             │           │           │
             └───────────┼───────────┘
                         ▼
                    PostgreSQL
```

A API receberia a solicitação, validaria os dados e criaria um job.

Em vez de esperar o processamento terminar, retornaria imediatamente algo como:

```json
{
  "job_id": "123",
  "status": "queued"
}
```

Os workers seriam responsáveis por executar as inferências.

Para aumentar a capacidade de processamento, seria possível aumentar horizontalmente a quantidade de workers.

Também seria importante controlar a quantidade de workers de acordo com os recursos disponíveis, principalmente CPU e memória, pois modelos de IA podem consumir bastante memória.

---

# Como faria o deploy em AWS?

Para uma primeira versão, eu utilizaria serviços gerenciados da AWS sempre que possível.

Uma arquitetura possível seria:

```text
                    Internet
                       │
                       ▼
                Application Load
                    Balancer
                       │
                       ▼
                  ECS / Fargate
                       │
              ┌────────┴────────┐
              │                 │
            API #1            API #2
              │                 │
              └────────┬────────┘
                       │
              ┌────────┼─────────┐
              ▼        ▼         ▼
             RDS     ElastiCache   S3
         PostgreSQL    Redis      Images
```

### ECS / Fargate

Utilizaria ECS para executar os containers da aplicação.

O Fargate permitiria executar os containers sem precisar gerenciar diretamente as máquinas virtuais.

### RDS

O PostgreSQL poderia ser executado utilizando Amazon RDS, evitando a necessidade de administrar manualmente o banco.

### ElastiCache

O Redis poderia ser disponibilizado através do Amazon ElastiCache.

### S3

As imagens dos drones seriam armazenadas no Amazon S3 em vez de ficarem dentro dos containers da API.

### Load Balancer

Um Application Load Balancer poderia distribuir as requisições entre múltiplas instâncias da API.

Para o nível atual do projeto, eu começaria com uma infraestrutura menor e evoluiria conforme a necessidade de processamento e volume de usuários.

---

# Como desacoplaria o processamento pesado da API?

Utilizaria uma arquitetura baseada em jobs assíncronos.

A API seria responsável apenas por:

1. Validar a requisição;
2. Registrar o processamento;
3. Criar um job;
4. Colocar o job em uma fila;
5. Retornar o identificador do processamento.

Um worker separado seria responsável pela inferência.

```text
Cliente
   │
   ▼
FastAPI
   │
   ├── Valida
   ├── Cria job
   └── Retorna job_id
          │
          ▼
       Redis
          │
          ▼
       Worker
          │
          ▼
       YOLO
          │
          ▼
    PostgreSQL
```

Isso evita que uma tarefa pesada bloqueie a API.

Também permite escalar API e processamento de forma independente.

Por exemplo, se houver muitas requisições mas poucos processamentos, posso aumentar a quantidade de instâncias da API sem necessariamente aumentar os workers.

Se o problema for o processamento de IA, posso aumentar apenas a quantidade de workers.

---

# Questões extras

## Questão 4 — 500 imagens de drone

### Enunciado

Um usuário envia 500 imagens de drone. O processamento pode levar vários minutos. Descreva uma arquitetura para esse fluxo.

### Resposta

Eu não faria o processamento das 500 imagens dentro da própria requisição HTTP.

Primeiramente, criaria uma missão ou um lote de processamento e armazenaria as imagens em um serviço de armazenamento de objetos, como Amazon S3.

A API criaria um job para cada imagem ou para pequenos lotes de imagens e colocaria esses jobs em uma fila.

```text
Cliente
   │
   ▼
FastAPI
   │
   ├──────────────► S3
   │                │
   │                └── 500 imagens
   │
   ▼
Redis / Queue
   │
   ├── Job 1
   ├── Job 2
   ├── Job 3
   ├── ...
   └── Job 500
          │
          ▼
      Workers
          │
          ▼
     Modelo YOLO
          │
          ▼
     PostgreSQL
```

A API poderia responder imediatamente:

```json
{
  "job_id": "batch-123",
  "status": "queued",
  "total_images": 500
}
```

Os workers processariam as imagens de forma independente.

Também seria possível registrar estados como:

```text
queued
processing
completed
failed
```

O cliente poderia consultar o status posteriormente através de um endpoint como:

```text
GET /processing/{job_id}
```

Essa abordagem evita manter uma requisição HTTP aberta durante vários minutos e permite aumentar a quantidade de workers conforme a necessidade.

---

# Questão 5 — Upload de uma imagem de 2 GB

### Enunciado

O upload de uma imagem de 2 GB não deve passar pela API. Como você resolveria isso?

### Resposta

Eu utilizaria armazenamento de objetos, como Amazon S3, com **upload direto do cliente para o S3 através de uma URL pré-assinada**.

O fluxo seria:

```text
Cliente
   │
   │ 1. Solicita URL
   ▼
FastAPI
   │
   │ 2. Gera URL pré-assinada
   ▼
Cliente
   │
   │ 3. Upload direto
   ▼
Amazon S3
   │
   │ 4. Evento / confirmação
   ▼
Fila de processamento
   │
   ▼
Worker
```

Dessa forma, a API nunca precisa receber os 2 GB.

A API poderia gerar uma URL temporária permitindo que o cliente faça o upload diretamente para um local específico do bucket.

Além de reduzir a carga da API, essa abordagem permite utilizar recursos do próprio S3 para uploads grandes, como multipart upload.

---

# Questão 6 — Isolamento das imagens entre clientes

### Enunciado

Como impedir que um usuário baixe imagens pertencentes a outro cliente?

### Resposta

Eu implementaria autorização baseada no usuário autenticado.

Não seria suficiente verificar apenas se o arquivo existe. A API deveria verificar se o recurso solicitado pertence ao usuário ou cliente autenticado.

Por exemplo:

```text
users
  │
  ▼
missions
  │
  ▼
images
```

Cada missão teria uma relação com o cliente responsável.

Ao solicitar uma imagem:

```text
GET /missions/123/images/456
```

a API faria:

```text
Token JWT
   │
   ▼
Identifica usuário
   │
   ▼
Busca missão
   │
   ▼
Verifica proprietário
   │
   ├── Pertence ao usuário → permite acesso
   │
   └── Não pertence → 403 Forbidden
```

No caso de imagens armazenadas no S3, eu evitaria tornar o bucket público.

A API poderia validar a autorização e, somente depois, gerar uma **URL pré-assinada com tempo limitado** para o download.

Assim, mesmo que o usuário conheça o ID ou o caminho de uma imagem de outro cliente, ele não conseguiria acessá-la sem possuir autorização.

---

# Uso de IA

A Inteligência Artificial foi utilizada como ferramenta de apoio durante o desenvolvimento, principalmente para pesquisa, revisão de implementação, esclarecimento de conceitos e identificação de possíveis problemas.

A implementação final foi revisada e testada localmente.

## Utilizações durante o desenvolvimento

### Estrutura inicial do projeto

A IA foi utilizada como apoio para estruturar inicialmente a aplicação FastAPI, incluindo:

* Organização de diretórios;
* Criação das primeiras rotas;
* Configuração do SQLAlchemy;
* Estruturação dos schemas;
* Configuração inicial do banco de dados.

### Implementação do CRUD

A IA auxiliou na identificação de padrões para implementação das operações:

* Create;
* Read;
* Update;
* Delete.

Também foi utilizada para revisar problemas encontrados durante os testes da API.

### Autenticação JWT

A IA foi utilizada como apoio para compreender e implementar o fluxo de autenticação utilizando JWT, incluindo:

* Geração de tokens;
* Validação do token;
* Proteção das rotas;
* Utilização do header `Authorization: Bearer`.

### Integração com Inteligência Artificial

Como o desafio não disponibilizou um modelo pré-treinado, foi pesquisada uma alternativa pública para demonstrar o requisito.

Foi utilizado o modelo YOLO através da biblioteca Ultralytics.

A IA auxiliou principalmente na compreensão da biblioteca e na estruturação do serviço responsável pela inferência.

A implementação foi executada e validada localmente através de imagens de teste.

### Docker, PostgreSQL e Redis

A IA também foi utilizada como apoio na configuração do ambiente Docker, principalmente por serem ferramentas que não faziam parte da experiência prática anterior com a mesma profundidade.

Durante essa etapa foram estudados conceitos como:

* Dockerfile;
* Docker Compose;
* Containers;
* Networks;
* Volumes;
* Healthchecks;
* `depends_on`;
* PostgreSQL em containers;
* Redis em containers;
* Variáveis de ambiente.

### Resolução de problemas

A IA também foi utilizada como ferramenta de troubleshooting durante o desenvolvimento, principalmente para interpretar mensagens de erro e sugerir caminhos de investigação.

Os comandos e alterações sugeridos foram executados e validados no ambiente local antes de serem incorporados ao projeto.

---

# Portfólio

## GitHub

**Thiago Mattos Silveira**

Perfil: `github.com/thiaagomattos`

## LinkedIn

**Thiago Mattos Silveira**

Perfil: `linkedin.com/in/thiago-mattos-silveira`

## Projeto relacionado

### Projeto Localizador

https://github.com/thiaagomattos/projeto-localizador

Projeto desenvolvido utilizando crawler para consulta e localização de endereços através de CEP.

O projeto demonstra experiência com:

* Python;
* Crawler;
* Consumo de páginas web;
* Processamento de dados;
* Organização de uma aplicação backend.

Esse projeto foi desenvolvido para um trabalho da faculdade, onde foi pedido uma aplicação com Frontend e Backend, com utlização de APIs de consulta.
Nesse projeto eu faria algumas coisas diferentes, como a implementação de deploy com Docker facilitando o build da aplicação e algumas mudanças de segurança,
como padrões de autenticação e melhores técnicas de segurança.

---

# Considerações finais

Este projeto foi desenvolvido com foco em demonstrar conhecimentos práticos de desenvolvimento backend utilizando Python e FastAPI.

Além da implementação dos requisitos principais, o desafio permitiu explorar conceitos relacionados a:

* APIs REST;
* Autenticação;
* Bancos relacionais;
* ORM;
* Processamento de imagens;
* Inteligência Artificial;
* Docker;
* PostgreSQL;
* Redis;
* Arquiteturas assíncronas;
* Escalabilidade;
* Armazenamento de objetos;
* Serviços AWS.

A implementação atual mantém o processamento de IA de forma síncrona para manter o escopo do desafio controlado. A arquitetura proposta nas questões extras apresenta como a solução poderia evoluir para um ambiente de produção com maior volume de imagens e usuários.
