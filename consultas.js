// 1. Calcular a porcentagem de vitórias e derrotas utilizando a carta X ("Mortar")

let carta = "Mortar";
let totalVitorias = db.batalha.countDocuments({
    "deck_jogador1.nome": carta,
    "vencedor": "jogador1"
}) + db.batalha.countDocuments({
    "deck_jogador2.nome": carta,
    "vencedor": "jogador2"
});
let totalDerrotas = db.batalha.countDocuments({
    "deck_jogador1.nome": carta,
    "vencedor": "jogador2"
}) + db.batalha.countDocuments({
    "deck_jogador2.nome": carta,
    "vencedor": "jogador1"
});
let totalBattles = totalVitorias + totalDerrotas;
let porcentagemVitorias = (totalBattles > 0) ? (totalVitorias / totalBattles * 100) : 0;
let porcentagemDerrotas = (totalBattles > 0) ? (totalDerrotas / totalBattles * 100) : 0;
print(`Porcentagem de Vitórias: ${porcentagemVitorias}%`);
print(`Porcentagem de Derrotas: ${porcentagemDerrotas}%`);




// 2. Liste os decks completos que produziram mais de X% (mínimo e máximo) de vitórias 

let porcentagemMinima = 60;
let porcentagemMaxima = 85;

db.batalha.aggregate([
    {
        $project: {
            deck_jogador1: "$deck_jogador1.nome", // Seleciona o deck do jogador 1
            vitorias_jogador1: {
                $cond: [{ $eq: ["$vencedor", "jogador1"] }, 1, 0]
            }
        }
    },
    {
        $group: {
            _id: "$deck_jogador1", // Agrupa pelo deck do jogador 1
            totalVitorias: { $sum: "$vitorias_jogador1" }, 
            totalBatalhas: { $sum: 1 } 
        }
    },
    {
        $project: {
            _id: 0,
            deck: "$_id", // O deck agrupado
            porcentagemVitorias: {
                $multiply: [{ $divide: ["$totalVitorias", "$totalBatalhas"] }, 100] 
            }
        }
    },
    {
        $match: {
            porcentagemVitorias: { $gte: porcentagemMinima, $lte: porcentagemMaxima } 
        }
    }
])




// 3. Calcular a quantidade de derrotas utilizando o combo de cartas (X1, X2, ...): 

let combo = ["Mortar", "Bats", "Miner", "Skeleton King", "Cannon Cart", "Goblin Gang", "Ice Wizard", "Arrows"];
let totalDerrotasCombo = db.batalha.countDocuments({
    $or: [
        { "deck_jogador1.nome": { $all: combo }, "vencedor": "jogador2" },
        { "deck_jogador2.nome": { $all: combo }, "vencedor": "jogador1" }
    ]
});
print(`Total de derrotas usando o combo ${combo.join(", ")}: ${totalDerrotasCombo}`);




// 4. Calcular a quantidade de vitórias envolvendo a carta X ("mortar") nos casos em que o vencedor possui Z% menos troféus do que o perdedor:

let cartaX = "arrows";
let minTrof = 10;
let minTorres = 2;

db.batalha.aggregate([
    {
        $match: {
            "deck_jogador1.nome": cartaX
        }
    },
    {
        $group: {
            _id: null,
            vitorias: {
                $sum: {
                    $cond: [{ $eq: ["$vencedor", "jogador1"] }, 1, 0]
                }
            },
            totalBatalhas: { $sum: 1
            }
        }
    },
    {
        $project: {
            _id: 0,
            porcentagemVitorias: {
                $cond: [
                    { $eq: ["$totalBatalhas", 0] },
                    0, // Se for zero, a porcentagem é 0
                    { $multiply: [{ $divide: ["$vitorias", "$totalBatalhas"] }, 100] }
                ]
            },
            derrotas: { $subtract: ["$totalBatalhas", "$vitorias"] }
        }
    }
]).forEach(result => print(`Porcentagem de Vitórias: ${result.porcentagemVitorias.toFixed(2)}%, Derrotas: ${result.derrotas}`));




// 5. Listar o combo de cartas de tamanho N que produziram mais de Y% de vitórias:

let tamanhoCombo = 4;
let minPorcentagem = 60;
let combos = db.batalha.aggregate([
    {
        $project: {
            deck_jogador1: "$deck_jogador1.nome",
            vitorias: {
                $cond: [{ $eq: ["$vencedor", "jogador1"] }, 1, 0]
            }
        }
    },
    {
        $group: {
            _id: { $slice: ["$deck_jogador1", tamanhoCombo] },
            totalVitorias: { $sum: "$vitorias" },
            totalBatalhas: { $sum: 1 }
        }
    },
    {
        $project: {
            combo: "$_id",
            porcentagemVitorias: { $multiply: [{ $divide: ["$totalVitorias", "$totalBatalhas"] }, 100] }
        }
    },
    {
        $match: {
            porcentagemVitorias: { $gt: minPorcentagem }
        }
    }
]);
combos.forEach(combo => print(`Combo: ${combo.combo}, Porcentagem de Vitórias: ${combo.porcentagemVitorias}%`));




// 6. Identificar as Cartas (10) com Menor Taxa de Vitórias

db.batalha.aggregate([
    {
        $unwind: "$deck_jogador1"
    },
    {
        $group: {
            _id: "$deck_jogador1.nome",
            totalVitorias: {
                $sum: { $cond: [{ $eq: ["$vencedor", "jogador1"] }, 1, 0] }
            },
            totalBatalhas: { $sum: 1 }
        }
    },
    {
        $project: {
            porcentagemVitorias: { $multiply: [{ $divide: ["$totalVitorias", "$totalBatalhas"] }, 100] }
        }
    },
    {
        $sort: { porcentagemVitorias: 1 }
    },
    {
        $limit: 10
    }
])




// 7. Cartas com Maior Frequência de Uso nos Decks Vencedores:

db.batalha.aggregate([
    {
        $project: {
            deck_vencedor: {
                $cond: [{ $eq: ["$vencedor", "jogador1"] }, "$deck_jogador1", "$deck_jogador2"]
            }
        }
    },
    {
        $unwind: "$deck_vencedor"
    },
    {
        $group: {
            _id: "$deck_vencedor.nome",
            frequencia: { $sum: 1 }
        }
    },
    {
        $sort: { frequencia: -1 }
    },
    {
        $limit: 10
    }
])




// 8. Os 10 Jogadores com maior taxa de vitórias

db.jogador.aggregate([
    {
        $project: {
            player_id: 1,
            nickname: 1,
            taxa_vitorias: {
                $multiply: [
                    { $divide: ["$total_vitorias", { $add: ["$total_vitorias", "$total_derrotas"] }] },
                    100
                ]
            }
        }
    },
    { $match: { taxa_vitorias: { $gt: 50 } } },
    { $sort: { taxa_vitorias: -1 } },
    { $limit: 10 }
]);
