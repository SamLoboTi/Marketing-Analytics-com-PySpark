"""Gera conjuntos de dados fictícios, coerentes e reproduzíveis."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from scripts.config import DATA_DIR

SEED = 42


def _escrever_csv(caminho: Path, colunas: list[str], linhas: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas)


def _data_aleatoria(inicio: date, fim: date, rng: random.Random) -> date:
    return inicio + timedelta(days=rng.randint(0, (fim - inicio).days))


def gerar_dados(force: bool = False) -> None:
    """Cria os quatro CSVs de entrada quando ainda não existem."""
    arquivos = [DATA_DIR / nome for nome in ("clientes.csv", "campanhas.csv", "interacoes.csv", "vendas.csv")]
    if not force and all(arquivo.exists() for arquivo in arquivos):
        return

    rng = random.Random(SEED)
    cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre", "Recife", "Salvador", "Brasília", "Fortaleza", "Campinas"]
    segmentos = ["Varejo", "Tecnologia", "Serviços", "Educação", "Saúde", "Finanças"]
    nomes = ["Ana", "Bruno", "Camila", "Daniel", "Eduarda", "Felipe", "Gabriela", "Henrique", "Isabela", "João", "Larissa", "Marcos"]
    sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Pereira", "Almeida"]

    clientes = []
    for i in range(1, 5001):
        clientes.append({
            "id_cliente": i,
            "nome": f"{rng.choice(nomes)} {rng.choice(sobrenomes)}",
            "idade": "" if i % 337 == 0 else rng.randint(18, 75),
            "cidade": "" if i % 521 == 0 else rng.choice(cidades),
            "segmento": "" if i % 617 == 0 else rng.choice(segmentos),
        })

    canais = ["Email", "SMS", "Push"]
    temas = ["Black Friday", "Boas-vindas", "Reativação", "Lançamento", "Fidelidade", "Sazonal"]
    campanhas = []
    inicio_base = date(2024, 1, 1)
    for i in range(1, 3001):
        inicio = _data_aleatoria(inicio_base, date(2025, 11, 30), rng)
        campanhas.append({
            "id_campanha": i,
            "nome_campanha": f"{rng.choice(temas)} {inicio:%Y-%m} #{i:04d}",
            "canal": rng.choices(canais, weights=[75, 15, 10])[0],
            "data_inicio": inicio.isoformat(),
            "data_fim": (inicio + timedelta(days=rng.randint(3, 21))).isoformat(),
        })

    interacoes = []
    pares = set()
    while len(interacoes) < 9000:
        cliente = rng.randint(1, 5000)
        campanha = rng.randint(1, 3000)
        if (cliente, campanha) in pares:
            continue
        pares.add((cliente, campanha))
        abriu = int(rng.random() < 0.57)
        clicou = int(abriu and rng.random() < 0.31)
        inicio = date.fromisoformat(campanhas[campanha - 1]["data_inicio"])
        interacoes.append({
            "id_cliente": cliente,
            "id_campanha": campanha,
            "abriu": abriu,
            "clicou": clicou,
            "data_interacao": (inicio + timedelta(days=rng.randint(0, 10))).isoformat(),
        })

    vendas = []
    interacoes_com_clique = [item for item in interacoes if item["clicou"] == 1]
    for i in range(1, 5001):
        origem = rng.choice(interacoes_com_clique if rng.random() < 0.82 else interacoes)
        data_interacao = date.fromisoformat(origem["data_interacao"])
        vendas.append({
            "id_venda": i,
            "id_cliente": origem["id_cliente"],
            "id_campanha": origem["id_campanha"],
            "valor": "" if i % 997 == 0 else f"{rng.lognormvariate(4.4, 0.65):.2f}",
            "data_venda": (data_interacao + timedelta(days=rng.randint(0, 14))).isoformat(),
        })

    _escrever_csv(arquivos[0], list(clientes[0]), clientes)
    _escrever_csv(arquivos[1], list(campanhas[0]), campanhas)
    _escrever_csv(arquivos[2], list(interacoes[0]), interacoes)
    _escrever_csv(arquivos[3], list(vendas[0]), vendas)


if __name__ == "__main__":
    gerar_dados(force=True)

