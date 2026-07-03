"""Testes das transformações e métricas de negócio."""

from datetime import date

import pytest

from scripts.analise import desempenho_campanhas
from scripts.transformacao import consolidar_interacoes


def test_consolidar_interacoes_preserva_maior_engajamento(spark):
    entrada = spark.createDataFrame([
        (1, 10, 0, 0, date(2026, 1, 10)),
        (1, 10, 1, 1, date(2026, 1, 12)),
    ], "id_cliente int, id_campanha int, abriu int, clicou int, data_interacao date")

    resultado = consolidar_interacoes(entrada).first()

    assert (resultado.abriu, resultado.clicou) == (1, 1)
    assert resultado.primeira_interacao == date(2026, 1, 10)


def test_desempenho_calcula_taxas_sobre_clientes_unicos(spark):
    campanhas = spark.createDataFrame(
        [(10, "Campanha teste", "Email")],
        "id_campanha int, nome_campanha string, canal string",
    )
    interacoes = spark.createDataFrame([
        (1, 10, 1, 1),
        (2, 10, 1, 0),
        (3, 10, 0, 0),
        (4, 10, 0, 0),
    ], "id_cliente int, id_campanha int, abriu int, clicou int")
    vendas = spark.createDataFrame([
        (100, 1, 10, 120.0),
        (101, 1, 10, 80.0),
        (102, 2, 10, 100.0),
    ], "id_venda int, id_cliente int, id_campanha int, valor double")

    resultado = desempenho_campanhas({
        "campanhas": campanhas,
        "interacoes_consolidadas": interacoes,
        "vendas_enriquecidas": vendas,
    }).first()

    assert resultado.receita == pytest.approx(300.0)
    assert resultado.ticket_medio == pytest.approx(100.0)
    assert resultado.taxa_abertura == pytest.approx(50.0)
    assert resultado.taxa_clique == pytest.approx(25.0)
    assert resultado.taxa_conversao == pytest.approx(50.0)
