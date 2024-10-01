import requests
import mongoengine as me

API_TOKEN = 'Insira seu Token da API do Clash Royale Aqui'

HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}'
}

uri = "Insira a URI do MongoDb aqui"

me.connect(host=uri)

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

class Batalha(me.Document):
    battle_id = me.StringField(required=True)
    torres_destruidas_jogador1 = me.IntField()
    torres_destruidas_jogador2 = me.IntField()
    vencedor = me.StringField()  
    deck_jogador1 = me.ListField(me.DictField())  
    deck_jogador2 = me.ListField(me.DictField())  
    trofeus_jogador1 = me.IntField()
    trofeus_jogador2 = me.IntField()

def get_player_info(player_tag):
    url = f"https://api.clashroyale.com/v1/players/%23{player_tag.upper()}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return None

def salvar_jogador_no_mongodb(player_data):
    jogador = Jogador(
        player_id=player_data['tag'],
        nickname=player_data['name'],
        trofeus=player_data['trophies'],
        nivel=player_data['expLevel'],
        total_vitorias=player_data['wins'],  
        total_derrotas=player_data['losses']  
    )
    jogador.save()
    print(f"Jogador {player_data['name']} salvo no MongoDB!")

def get_player_battles(player_tag):
    url = f"https://api.clashroyale.com/v1/players/%23{player_tag.upper()}/battlelog"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return None

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

def salvar_batalhas_no_mongodb(battles_data):
    for battle in battles_data:
        torres_destruidas_jogador1 = battle['team'][0].get('crowns', 0)
        torres_destruidas_jogador2 = battle['opponent'][0].get('crowns', 0)
        
        vencedor = 'empate'
        if torres_destruidas_jogador1 > torres_destruidas_jogador2:
            vencedor = 'jogador1'
        elif torres_destruidas_jogador1 < torres_destruidas_jogador2:
            vencedor = 'jogador2'

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
    print(f"{len(battles_data)} batalhas salvas no MongoDB") 

def listar_jogadores():
    jogadores = Jogador.objects()
    for jogador in jogadores:
        print(jogador)

def coletar_dados_de_varios_jogadores(player_tags):
    for player_tag in player_tags:
        print(f"\nColetando dados do jogador: {player_tag}")
        player_info = get_player_info(player_tag)
        if player_info:
            salvar_jogador_no_mongodb(player_info)

        battles_info = get_player_battles(player_tag)
        if battles_info:
            salvar_batalhas_no_mongodb(battles_info)

if __name__ == "__main__":
    player_tags = ['Q0298LL98', 'GG829JGY', '8UVPR9CY', 'JYCU28LPR', 'CGJYQ9QLC', '2QP2Y0V2', '8QV2U0QL2', 'VLQ0CG2PY', 'JCRURRR0Q', 'Y299R2Y2', 'CU892YRQ8', 'Q09VPPY8', 'L989VJUY0', '90C9PUUY', '8P8ULCCLV', 'PJJ8QJ2Q8', 'G0VR9ULUY', '8LV9GP8L', 'G29YCCJPP', '9992JC2UQ', 'V9YUQLYYV', 'R9PU0LR', 'P0R9YGL', '2VC290J2C', 'RVJCJGRV', 'YC2Q0VRC', '22CV9CRJL', '9LRUUCC98', '2PP888L8J', '82Y88GL90', '29UCLRP8G', '820LCC', '98U8JJQ2V', 'LJ0YC9LQ2', 'PJCG8V0R', 'QYC2RJU', 'GVJRQYU0', '9V99RYLP', '9R2L00CVP', '90GPCGPQ', 'JCJG888', 'RRPGYGJP', '2GL9PL98J', '8PGCVU02V', '8RUY9PJJU', 'GPUL2GLL', 'PJ2JVQ0YU', '2RQPCY92', 'QQJYLQ9', 'PG8J2JPJ', '2L02YJV2', '92VYCCPJ', 'YR9YP9CVJ', '2JL2GJ2PJ', '2V9YJ2LR', '9R0L8PVYJ', 'V9LR90R92', '2LL2PCUQV', 'YGPQLQ2C', 'LJ2GYUQCG', '2QYP92PV', '222L8CV99', '8R9L8JV2', '9QJPGG92P', 'PR9U9CP2V', 'PQRVPRG8C', '9PQRU2V80', 'JJ8GP99R', '8QU8LP80V', 'QU92LPJ', 'QC2YYV90C', '28PRC2QQC', 'RG2292U0', '2JGCQJCRP', 'PUYUC8G', '8QP0VJ0RY', '99QJ8YUP9', 'RRU00GUCC', '2LYPQ0G8', 'GUPLY9U88', '8C9UY9V00', '2PLLV9PLC', '8PRRPL8G', 'YVQ28PCR', '9YJCQG8U0', '80VL8QJJ', '2U0U2L8VJ', '22CCG0J90', '2QUULV8', '8LC228CJ', '9RQ8298R', '2R9PLR9R', '8V8CPRGRJ', '98G9P8R0', '2JJ0V8G8Q', '82LLPJCQ', '9800CYY9', 'LQ90LRQU', '9C2UQQVL', '9YRQJCL'] 

    coletar_dados_de_varios_jogadores(player_tags)

    print("\nJogadores Salvos:")
    listar_jogadores()














