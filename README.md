# Projeto Banco de Dados MongoDB Clash Royale 2024.2

## Integrantes do Grupo
- Adonis Vinicius
- Alan Vitor
- João Victor Santos
- Luis Vinicius

## Objetivo do Projeto
Armazenar dados de batalhas do jogo **Clash Royale** em um banco de dados NoSQL (MongoDB Atlas) para viabilizar consultas analíticas. O objetivo é analisar estatísticas de vitórias/derrotas associadas ao uso das cartas, visando balancear o jogo.

## O Banco de Dados Armazena:
- **Informações dos Jogadores:** ID, nickname, troféus, nível, total de vitórias e derrotas.
- **Informações das Batalhas:** Número de torres derrubadas de cada lado, vencedor, deck de batalha de cada jogador, e quantidade de troféus de cada jogador no momento da partida.

## Conteúdo Deste Repositório
- **Modelagem do Banco de Dados**
- **Consultas** na linguagem do MongoDB
- **Interface Gráfica** para acesso aos dados
- **Uso de dados reais** por meio da [API do Clash Royale](https://developer.clashroyale.com/#/)
- **Integração com o MongoDB Atlas**

## Consultas Disponíveis:
1. Calcular a porcentagem de vitórias e derrotas utilizando a carta X.
2. Listar os decks completos que produziram mais de X% (mínimo e máximo) de vitórias.
3. Calcular a quantidade de derrotas utilizando o combo de cartas ("Mortar", "Bats", "Miner", "Skeleton King", "Cannon Cart", "Goblin Gang", "Ice Wizard", "Arrows").
4. Calcular a quantidade de vitórias envolvendo a carta X nos casos em que o vencedor possui Z% menos troféus do que o perdedor.
5. Listar o combo de cartas de tamanho N que produziram mais de Y% de vitórias.
6. Identificar as 10 cartas com menor taxa de vitórias.
7. Cartas com maior frequência de uso nos decks vencedores.
8. Listar os 10 jogadores com maior taxa de vitórias.

## Como Rodar o Código

### Requisitos:
- Conta no site da [API do Clash Royale](https://developer.clashroyale.com/#/) para obtenção do token.
- Conta no [MongoDB Atlas](https://www.mongodb.com/) e criação de Cluster para integração com o código.
- Visual Studio Code com as bibliotecas: `Tkinter`, `Pymongo`, `Requests` e `Mongoengine`.
- Projeto desenvolvido em Python.

### Passo a Passo:

1. No arquivo **`clashroyale.py`**, adicione:
   - O Token retirado do site da API do Clash Royale.
   - A URI do seu MongoDB.

2. Execute o arquivo **`clashroyale.py`** e aguarde a extração dos dados (pode adicionar ou remover tags de jogadores reais no final do código, conforme necessário).

3. No arquivo **`interface.py`**, adicione:
   - A URI do seu MongoDB.
   - O nome do seu banco de dados.

4. Execute o arquivo **`interface.py`**.

5. Teste as consultas utilizando nomes de cartas reais do jogo Clash Royale (em inglês).

## Referências:
- [API do Clash Royale](https://developer.clashroyale.com/#/)
- [MongoDB Atlas](https://www.mongodb.com/)

---

**Obrigado por utilizar nosso projeto!**

