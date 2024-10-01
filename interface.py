import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient

client = MongoClient('Insira a URI do MongoDb aqui')
db = client['Insira o nome da DataBase Aqui']

def calcular_porcentagem_vitorias_derrotas():
    carta = carta_input.get()
    total_vitorias = db.batalha.count_documents({
        "$or": [
            {"deck_jogador1.nome": carta, "vencedor": "jogador1"},
            {"deck_jogador2.nome": carta, "vencedor": "jogador2"}
        ]
    })
    total_derrotas = db.batalha.count_documents({
        "$or": [
            {"deck_jogador1.nome": carta, "vencedor": "jogador2"},
            {"deck_jogador2.nome": carta, "vencedor": "jogador1"}
        ]
    })
    total_batalhas = total_vitorias + total_derrotas
    porcentagem_vitorias = (total_vitorias / total_batalhas * 100) if total_batalhas > 0 else 0
    porcentagem_derrotas = (total_derrotas / total_batalhas * 100) if total_batalhas > 0 else 0

    resultado = f"Porcentagem de Vitórias: {porcentagem_vitorias:.2f}%\nPorcentagem de Derrotas: {porcentagem_derrotas:.2f}%"
    messagebox.showinfo("Resultado", resultado)

def listar_decks_vitorias():
    porcentagem_minima = int(porc_min_input.get())
    porcentagem_maxima = int(porc_max_input.get())
    
    resultado = ""
    decks = db.batalha.aggregate([ 
        {
            "$project": {
                "deck_jogador1": "$deck_jogador1.nome",
                "vitorias_jogador1": {
                    "$cond": [{"$eq": ["$vencedor", "jogador1"]}, 1, 0]
                }
            }
        },
        {
            "$group": {
                "_id": "$deck_jogador1",
                "totalVitorias": {"$sum": "$vitorias_jogador1"},
                "totalBatalhas": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "deck": "$_id",
                "porcentagemVitorias": {
                    "$multiply": [{"$divide": ["$totalVitorias", "$totalBatalhas"]}, 100]
                }
            }
        },
        {
            "$match": {
                "porcentagemVitorias": {"$gte": porcentagem_minima, "$lte": porcentagem_maxima}
            }
        }
    ])

    for deck in decks:
        resultado += f"Deck: {deck['deck']}, Porcentagem de Vitórias: {deck['porcentagemVitorias']:.2f}%\n"
    
    messagebox.showinfo("Decks com mais de X% de Vitórias", resultado)

def calcular_derrotas_combo():
    combo = ["Mortar", "Bats", "Miner", "Skeleton King", "Cannon Cart", "Goblin Gang", "Ice Wizard", "Arrows"]
    total_derrotas_combo = db.batalha.count_documents({
        "$or": [
            {"deck_jogador1.nome": {"$all": combo}, "vencedor": "jogador2"},
            {"deck_jogador2.nome": {"$all": combo}, "vencedor": "jogador1"}
        ]
    })
    
    resultado = f"Derrotas usando: {', '.join(combo)}: {total_derrotas_combo}"
    messagebox.showinfo("Resultado", resultado)

def calcular_vitorias_carta_com_menos_trofeus():
    carta = carta_input_trofeus.get()
    
    vitorias = db.batalha.aggregate([
        {
            "$match": {"deck_jogador1.nome": carta}
        },
        {
            "$group": {
                "_id": None,
                "vitorias": {
                    "$sum": {"$cond": [{"$eq": ["$vencedor", "jogador1"]}, 1, 0]}
                },
                "total_batalhas": {"$sum": 1}
            }
        },
        {
            "$project": {
                "porcentagemVitorias": {"$multiply": [{"$divide": ["$vitorias", "$total_batalhas"]}, 100]},
                "derrotas": {"$subtract": ["$total_batalhas", "$vitorias"]}
            }
        }
    ])

    resultado = ""
    for res in vitorias:
        resultado = f"Porcentagem de Vitórias: {res['porcentagemVitorias']:.2f}%\nDerrotas: {res['derrotas']}"
    
    messagebox.showinfo("Vitórias com menos troféus", resultado)

def listar_combos_vitoriosos():
    tamanho_combo = int(combo_size_input.get())
    min_porcentagem = int(min_percent_input.get())

    combos = db.batalha.aggregate([
        {
            "$project": {
                "deck_jogador1": "$deck_jogador1.nome",
                "vitorias": {"$cond": [{"$eq": ["$vencedor", "jogador1"]}, 1, 0]}
            }
        },
        {
            "$group": {
                "_id": {"$slice": ["$deck_jogador1", tamanho_combo]},
                "totalVitorias": {"$sum": "$vitorias"},
                "totalBatalhas": {"$sum": 1}
            }
        },
        {
            "$project": {
                "combo": "$_id",
                "porcentagemVitorias": {"$multiply": [{"$divide": ["$totalVitorias", "$totalBatalhas"]}, 100]}
            }
        },
        {
            "$match": {
                "porcentagemVitorias": {"$gt": min_porcentagem}
            }
        }
    ])

    resultado = ""
    for combo in combos:
        resultado += f"Combo: {combo['combo']}, Porcentagem de Vitórias: {combo['porcentagemVitorias']:.2f}%\n"
    
    messagebox.showinfo("Combos Vitoriosos", resultado)

def listar_menor_taxa_vitorias():
    cartas = db.batalha.aggregate([
        {
            "$unwind": "$deck_jogador1"
        },
        {
            "$group": {
                "_id": "$deck_jogador1.nome",
                "totalVitorias": {
                    "$sum": {"$cond": [{"$eq": ["$vencedor", "jogador1"]}, 1, 0]}
                },
                "totalBatalhas": {"$sum": 1}
            }
        },
        {
            "$project": {
                "porcentagemVitorias": {"$multiply": [{"$divide": ["$totalVitorias", "$totalBatalhas"]}, 100]}
            }
        },
        {
            "$sort": {"porcentagemVitorias": 1}
        },
        {
            "$limit": 10
        }
    ])

    resultado = ""
    for carta in cartas:
        resultado += f"Carta: {carta['_id']}, Porcentagem de Vitórias: {carta['porcentagemVitorias']:.2f}%\n"
    
    messagebox.showinfo("Menor Taxa de Vitórias", resultado)

def listar_cartas_frequentes():
    cartas = db.batalha.aggregate([
        {
            "$project": {
                "deck_vencedor": {
                    "$cond": [{"$eq": ["$vencedor", "jogador1"]}, "$deck_jogador1", "$deck_jogador2"]
                }
            }
        },
        {
            "$unwind": "$deck_vencedor"
        },
        {
            "$group": {
                "_id": "$deck_vencedor.nome",
                "frequencia": {"$sum": 1}
            }
        },
        {
            "$sort": {"frequencia": -1}
        },
        {
            "$limit": 10
        }
    ])

    resultado = ""
    for carta in cartas:
        resultado += f"Carta: {carta['_id']}, Frequência: {carta['frequencia']}\n"
    
    messagebox.showinfo("Cartas Frequentes", resultado)

def listar_top_jogadores():
    jogadores = db.jogador.aggregate([
        {
            "$project": {
                "player_id": 1,
                "nickname": 1,
                "taxa_vitorias": {
                    "$multiply": [
                        {"$divide": ["$total_vitorias", {"$add": ["$total_vitorias", "$total_derrotas"]}]}, 100
                    ]
                }
            }
        },
        {
            "$sort": {"taxa_vitorias": -1}
        },
        {
            "$limit": 10
        }
    ])

    resultado = ""
    for jogador in jogadores:
        resultado += f"Jogador: {jogador['nickname']}, Taxa de Vitórias: {jogador['taxa_vitorias']:.2f}%\n"
    
    messagebox.showinfo("Top Jogadores", resultado)

root = tk.Tk()
root.title("Interface de Consultas")

tab_control = ttk.Notebook(root)

aba_porcentagem_vit_der = ttk.Frame(tab_control)
aba_vitorias_decks = ttk.Frame(tab_control)
aba_derrotas_combo = ttk.Frame(tab_control)
aba_vitorias_trofeus = ttk.Frame(tab_control)
aba_combos_vitoriosos = ttk.Frame(tab_control)
aba_menor_taxa = ttk.Frame(tab_control)
aba_frequencia_cartas = ttk.Frame(tab_control)
aba_top_jogadores = ttk.Frame(tab_control)

tab_control.add(aba_porcentagem_vit_der, text="Vitórias/Derrotas por Carta")
tab_control.add(aba_vitorias_decks, text="Vitórias por Deck")
tab_control.add(aba_derrotas_combo, text="Derrotas por Combo")
tab_control.add(aba_vitorias_trofeus, text="Carta Vitoriosa (com Menos Troféus)")
tab_control.add(aba_combos_vitoriosos, text="Combos Vitoriosos")
tab_control.add(aba_menor_taxa, text="Menor Taxa de Vitórias")
tab_control.add(aba_frequencia_cartas, text="Cartas Frequentes")
tab_control.add(aba_top_jogadores, text="Top Jogadores")

ttk.Label(aba_porcentagem_vit_der, text="Nome da Carta:").grid(column=0, row=0, padx=10, pady=10)
carta_input = ttk.Entry(aba_porcentagem_vit_der)
carta_input.grid(column=1, row=0, padx=10, pady=10)
ttk.Button(aba_porcentagem_vit_der, text="Calcular", command=calcular_porcentagem_vitorias_derrotas).grid(column=1, row=1, padx=10, pady=10)

ttk.Label(aba_vitorias_decks, text="Porcentagem Mínima(%):").grid(column=0, row=0, padx=10, pady=10)
porc_min_input = ttk.Entry(aba_vitorias_decks)
porc_min_input.grid(column=1, row=0, padx=10, pady=10)

ttk.Label(aba_vitorias_decks, text="Porcentagem Máxima(%):").grid(column=0, row=1, padx=10, pady=10)
porc_max_input = ttk.Entry(aba_vitorias_decks)
porc_max_input.grid(column=1, row=1, padx=10, pady=10)

ttk.Button(aba_vitorias_decks, text="Listar Decks", command=listar_decks_vitorias).grid(column=1, row=2, padx=10, pady=10)

ttk.Button(aba_derrotas_combo, text="Calcular Derrotas De Combo", command=calcular_derrotas_combo).grid(column=1, row=0, padx=10, pady=10)

ttk.Label(aba_vitorias_trofeus, text="Nome da Carta:").grid(column=0, row=0, padx=10, pady=10)
carta_input_trofeus = ttk.Entry(aba_vitorias_trofeus)
carta_input_trofeus.grid(column=1, row=0, padx=10, pady=10)
ttk.Button(aba_vitorias_trofeus, text="Calcular Vitórias", command=calcular_vitorias_carta_com_menos_trofeus).grid(column=1, row=1, padx=10, pady=10)

ttk.Label(aba_combos_vitoriosos, text="Tamanho do Combo:").grid(column=0, row=0, padx=10, pady=10)
combo_size_input = ttk.Entry(aba_combos_vitoriosos)
combo_size_input.grid(column=1, row=0, padx=10, pady=10)

ttk.Label(aba_combos_vitoriosos, text="Porcentagem Mínima de Vitórias(%):").grid(column=0, row=1, padx=10, pady=10)
min_percent_input = ttk.Entry(aba_combos_vitoriosos)
min_percent_input.grid(column=1, row=1, padx=10, pady=10)

ttk.Button(aba_combos_vitoriosos, text="Listar Combos", command=listar_combos_vitoriosos).grid(column=1, row=2, padx=10, pady=10)

ttk.Button(aba_menor_taxa, text="Ver Top 10 Piores Cartas (Win Rate)", command=listar_menor_taxa_vitorias).grid(column=1, row=0, padx=10, pady=10)

ttk.Button(aba_frequencia_cartas, text="Cartas Frequentes", command=listar_cartas_frequentes).grid(column=1, row=0, padx=10, pady=10)

ttk.Button(aba_top_jogadores, text="Ver Top 10 Jogadores", command=listar_top_jogadores).grid(column=1, row=0, padx=10, pady=10)

tab_control.pack(expand=1, fill='both')

root.mainloop()
