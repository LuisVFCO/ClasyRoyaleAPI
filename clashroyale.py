import requests
import mongoengine as me

API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImU3ZWEyODZkLTI1OGQtNGQwNS04ZGRiLWUzYjA1MThmMDc3ZiIsImlhdCI6MTcyNzU0NzY4NSwic3ViIjoiZGV2ZWxvcGVyL2NjYjExYWI1LTMxYjMtY2E1Yy0wMzZkLWExYzQ4MTkzMzNmNiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIyMDEuNTkuMTY5LjkiXSwidHlwZSI6ImNsaWVudCJ9XX0.vM15ZpYLpcO407axS1j-BlbQcEhddKUahf_EGyNfkqwuBkaT2Y1HphaaPmU9nRx2BH5ikaJFZkB9Xiw97NqIvQ'
HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Conectar ao MongoDB
me.connect('clash_royale_db', host='localhost', port=27017)

# Definir modelo de dados para jogador
class Jogador(me.Document):
    player_id = me.StringField(required=True)
    nickname = me.StringField(required=True)
    trofeus = me.IntField()
    nivel = me.IntField()
    total_vitorias = me.IntField()
    total_derrotas = me.IntField()

    def __str__(self):
        return (f"ID: {self.player_id}, Nome: {self.nickname}, "
                f"Troféus: {self.trofeus}, Nível: {self.nivel}, "
                f"Vitórias: {self.total_vitorias}, Derrotas: {self.total_derrotas}")

# Definir modelo de dados para batalhas
class Batalha(me.Document):
    battle_id = me.StringField(required=True)
    torres_destruidas_jogador1 = me.IntField()
    torres_destruidas_jogador2 = me.IntField()
    vencedor = me.StringField()  # 'jogador1', 'jogador2', ou 'empate'
    deck_jogador1 = me.ListField(me.DictField())  # Informações detalhadas das cartas
    deck_jogador2 = me.ListField(me.DictField())  # Informações detalhadas das cartas
    trofeus_jogador1 = me.IntField()
    trofeus_jogador2 = me.IntField()

# Função para obter dados de um jogador
def get_player_info(player_tag):
    url = f"https://api.clashroyale.com/v1/players/%23{player_tag.upper()}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return None

# Função para salvar jogador no MongoDB
def salvar_jogador_no_mongodb(player_data):
    jogador = Jogador(
        player_id=player_data['tag'],
        nickname=player_data['name'],
        trofeus=player_data['trophies'],
        nivel=player_data['expLevel'],
        total_vitorias=player_data['wins'],  # Total de vitórias
        total_derrotas=player_data['losses']  # Total de derrotas
    )
    jogador.save()
    print(f"Jogador {player_data['name']} salvo no MongoDB!")

# Função para obter batalhas de um jogador
def get_player_battles(player_tag):
    url = f"https://api.clashroyale.com/v1/players/%23{player_tag.upper()}/battlelog"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return None

# Função para extrair informações detalhadas das cartas
def extrair_info_cartas(cartas):
    cartas_detalhadas = []
    for carta in cartas:
        carta_info = {
            'nome': carta.get('name'),
            'nivel': carta.get('level'),
            'raridade': carta.get('rarity'),
            'tipo': carta.get('type'),
            'elixir': carta.get('elixir')
        }
        cartas_detalhadas.append(carta_info)
    return cartas_detalhadas

# Função para salvar batalhas no MongoDB
def salvar_batalhas_no_mongodb(battles_data):
    for battle in battles_data:
        # Definir as torres destruídas
        torres_destruidas_jogador1 = battle['team'][0].get('crowns', 0)
        torres_destruidas_jogador2 = battle['opponent'][0].get('crowns', 0)
        
        # Definir vencedor
        vencedor = 'empate'
        if torres_destruidas_jogador1 > torres_destruidas_jogador2:
            vencedor = 'jogador1'
        elif torres_destruidas_jogador1 < torres_destruidas_jogador2:
            vencedor = 'jogador2'

        # Extrair informações detalhadas das cartas
        deck_jogador1 = extrair_info_cartas(battle['team'][0].get('cards', []))
        deck_jogador2 = extrair_info_cartas(battle['opponent'][0].get('cards', []))

        batalha = Batalha(
            battle_id=battle['battleTime'],
            torres_destruidas_jogador1=torres_destruidas_jogador1,
            torres_destruidas_jogador2=torres_destruidas_jogador2,
            vencedor=vencedor,
            deck_jogador1=deck_jogador1,
            deck_jogador2=deck_jogador2,
            trofeus_jogador1=battle['team'][0].get('startingTrophies', 0),
            trofeus_jogador2=battle['opponent'][0].get('startingTrophies', 0)
        )
        batalha.save()
        print(f"Batalha de {battle['battleTime']} salva no MongoDB!")

# Funções para listar dados
def listar_jogadores():
    jogadores = Jogador.objects()
    for jogador in jogadores:
        print(jogador)

def listar_batalhas():
    batalhas = Batalha.objects()
    for batalha in batalhas:
        print(f"Batalha ID: {batalha.battle_id}")
        print(f"Torres destruidas pelo Jogador 1: {batalha.torres_destruidas_jogador1}")
        print(f"Torres destruidas pelo Jogador 2: {batalha.torres_destruidas_jogador2}")
        print(f"Vencedor: {batalha.vencedor}")
        print("=========================================")

# Função para coletar dados de vários jogadores e salvar no MongoDB
def coletar_dados_de_varios_jogadores(player_tags):
    for player_tag in player_tags:
        print(f"\nColetando dados do jogador: {player_tag}")
        # Obter e salvar informações do jogador
        player_info = get_player_info(player_tag)
        if player_info:
            salvar_jogador_no_mongodb(player_info)

        # Obter e salvar batalhas do jogador
        battles_info = get_player_battles(player_tag)
        if battles_info:
            salvar_batalhas_no_mongodb(battles_info)

# Exemplo de uso
if __name__ == "__main__":
    # Lista de tags de jogadores (sem #, apenas o ID)
    player_tags = ['GG829JGY', '8UVPR9CY', 'CGJYQ9QLC', 'VLQ0CG2PY', '8QV2U0QL2', 'Q0298LL98', 'JCRURRR0Q', '2QP2Y0V2', '90C9PUUY', 'Y299R2Y2', 'CU892YRQ8', '8P8ULCCLV', 'G29YCCJPP', 'G0VR9ULUY', 'L989VJUY0', '8LV9GP8L', '9992JC2UQ', 'V9YUQLYYV', 'P0R9YGL', 'RVJCJGRV', 'JYCU28LPR', 'JCJG888', '9LRUUCC98', 'LJ0YC9LQ2', 'Q09VPPY8', 'QYC2RJU', '2VC290J2C', '82Y88GL90', '2PP888L8J', 'PJCG8V0R', '9V99RYLP', 'YC2Q0VRC', '9R2L00CVP', 'PJJ8QJ2Q8', '8RQ9GU09Y', '98U8JJQ2V']  # Exemplo de tags

    # Coletar dados de vários jogadores e salvar no MongoDB
    coletar_dados_de_varios_jogadores(player_tags)

    # Listar jogadores e batalhas salvos
    print("\nJogadores Salvos:")
    listar_jogadores()

    print("\nBatalhas Salvas:")
    listar_batalhas()













