# Prova Backend C - Thiago Mattos Silveira

Repositório desenvolvido como parte do desafio técnico para a vaga de **Backend Python** na IPM Sistemas.

O projeto consiste no desenvolvimento de uma **API RESTful para gerenciamento de missões de drones**, com autenticação, integração com um modelo de Inteligência Artificial para processamento de imagens e execução containerizada utilizando **Docker**.

A solução é desenvolvida em **Python com FastAPI**, utilizando **SQLite** para o armazenamento das missões e **PostgreSQL** para o armazenamento do histórico relacionado ao processamento das predições. O **Redis** é utilizado como mecanismo de cache e/ou armazenamento temporário durante o processamento.


# Questões teóricas

Nesta seção estão as respostas referentes à **Parte 1 do desafio**.

## Questão 1

### Resposta

O diagrama apresenta uma arquitetura composta por diferentes serviços, cada um responsável por uma parte do fluxo de comunicação, processamento, persistência, mensageria e monitoramento da aplicação.

Usuário, controle remoto DJI e aplicativo Android

O usuário interage com o sistema por meio do controle remoto DJI e de um aplicativo Android. Esses componentes representam a camada de interação com o usuário e com o dispositivo responsável pela operação do drone e pela coleta das imagens e informações da missão.

O aplicativo realiza a comunicação com os serviços da infraestrutura, enviando as informações necessárias para processamento, armazenamento e acompanhamento das operações.

Kong — API Gateway / Reverse Proxy

O Kong atua como um Gateway e Reverse Proxy, funcionando como ponto de entrada para os serviços disponibilizados pela aplicação.

Sua principal função é receber as requisições provenientes dos clientes e encaminhá-las para o serviço correspondente. Dessa forma, o cliente não precisa conhecer diretamente a localização de cada serviço interno.

No diagrama, o Kong pode direcionar as requisições para diferentes componentes, como a API REST, a API Java e o serviço de mensageria.

Além do roteamento, uma solução como o Kong também pode centralizar funcionalidades como autenticação, autorização, controle de acesso, rate limiting e outras políticas de entrada.

API REST

A API REST representa um microsserviço responsável por abstrair a comunicação com o armazenamento de objetos utilizado pela aplicação.

Nesse caso, ela realiza a comunicação com o Amazon S3, permitindo que as imagens e outros arquivos sejam armazenados sem que os clientes ou demais serviços precisem acessar diretamente o bucket.

Essa abordagem aumenta a segurança e o controle sobre os dados armazenados, pois o acesso ao S3 pode ser centralizado nesse serviço.

O S3 é adequado para esse cenário por ser um serviço de armazenamento de objetos voltado para arquivos, como imagens e outros dados de maior tamanho.

Amazon S3

O Amazon S3 é o serviço de armazenamento de objetos utilizado para armazenar as imagens e outros arquivos gerados durante as operações dos drones.

Seu objetivo principal é fornecer um armazenamento altamente escalável e adequado para arquivos que podem ocupar uma quantidade significativa de espaço.

API Java

A API Java representa o principal serviço responsável pelo processamento das regras de negócio da aplicação.

Ela realiza a comunicação com outros componentes da arquitetura, incluindo o banco de dados MySQL, o Redis e o broker de mensageria EMQX.

Entre suas responsabilidades está o processamento e a persistência das informações relevantes da aplicação, como dados relacionados aos usuários, dispositivos e operações realizadas pelos drones.

MySQL

O MySQL é utilizado como banco de dados relacional para armazenar informações que precisam ser persistidas de forma estruturada.

Nesse contexto, pode armazenar dados como usuários, dispositivos, operações e outras informações relacionadas às regras de negócio da aplicação.

Redis

O Redis é utilizado como mecanismo de armazenamento em memória, sendo adequado para dados que precisam de acesso rápido e que não necessariamente precisam ter o mesmo comportamento de persistência de um banco de dados relacional.

Um possível uso nesse cenário seria o armazenamento de dados temporários, cache de informações frequentemente acessadas ou estados de processamento.

MQTT / EMQX

O MQTT é um protocolo de comunicação baseado em publicação e assinatura de mensagens, adequado para cenários envolvendo dispositivos e comunicação em tempo real.

No diagrama, o EMQX atua como broker MQTT, recebendo e distribuindo mensagens entre os componentes interessados.

A API Java pode publicar mensagens relacionadas às operações dos drones, enquanto outros componentes ou clientes podem consumir essas mensagens para acompanhar eventos e estados do sistema.

Prometheus

O Prometheus é responsável pela coleta e armazenamento de métricas dos serviços e da infraestrutura.

Essas métricas podem ser utilizadas para acompanhar informações como disponibilidade, quantidade de requisições, consumo de recursos, tempo de resposta e outros indicadores importantes para observar o comportamento da aplicação.

Grafana

O Grafana é utilizado para apresentar as métricas coletadas pelo Prometheus por meio de dashboards e gráficos.

Dessa forma, permite que um técnico ou administrador acompanhe de forma visual o estado da aplicação e da infraestrutura, facilitando a identificação de problemas e o acompanhamento do desempenho dos serviços.

