"""Testes das regras de qualidade aplicadas às fontes."""

from datetime import date

from scripts.limpeza import limpar_clientes, limpar_interacoes, limpar_vendas


def test_limpar_clientes_remove_chaves_invalidas_e_duplicadas(spark):
    entrada = spark.createDataFrame([
        (1, "Ana", 30, "Recife", "Varejo"),
        (1, "Ana duplicada", 31, "Recife", "Varejo"),
        (2, None, 15, None, None),
        (None, "Sem chave", 40, "Natal", "Serviços"),
    ], "id_cliente int, nome string, idade int, cidade string, segmento string")

    resultado = limpar_clientes(entrada).orderBy("id_cliente").collect()

    assert [linha.id_cliente for linha in resultado] == [1, 2]
    assert resultado[1].nome == "Não informado"
    assert resultado[1].cidade == "Não informada"
    assert resultado[1].idade is None


def test_limpar_interacoes_exige_abertura_para_clique_e_deduplica(spark):
    entrada = spark.createDataFrame([
        (1, 10, 0, 1, date(2026, 1, 10)),
        (1, 10, 0, 1, date(2026, 1, 10)),
        (2, 10, 1, 1, date(2026, 1, 11)),
    ], "id_cliente int, id_campanha int, abriu int, clicou int, data_interacao date")

    resultado = limpar_interacoes(entrada).orderBy("id_cliente").collect()

    assert len(resultado) == 2
    assert (resultado[0].abriu, resultado[0].clicou) == (0, 0)
    assert (resultado[1].abriu, resultado[1].clicou) == (1, 1)


def test_limpar_vendas_descarta_valores_nao_positivos(spark):
    entrada = spark.createDataFrame([
        (1, 1, 10, 100.126, date(2026, 1, 10)),
        (2, 1, 10, 0.0, date(2026, 1, 11)),
        (3, 1, 10, -5.0, date(2026, 1, 12)),
    ], "id_venda int, id_cliente int, id_campanha int, valor double, data_venda date")

    resultado = limpar_vendas(entrada).collect()

    assert len(resultado) == 1
    assert resultado[0].valor == 100.13
