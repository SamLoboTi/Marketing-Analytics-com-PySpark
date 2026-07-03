"""Junções e transformações que formam as bases analíticas."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def consolidar_interacoes(interacoes: DataFrame) -> DataFrame:
    """Consolida a jornada de cada cliente em cada campanha."""
    return (interacoes.groupBy("id_cliente", "id_campanha")
            .agg(F.max("abriu").alias("abriu"), F.max("clicou").alias("clicou"),
                 F.min("data_interacao").alias("primeira_interacao")))


def enriquecer_vendas(vendas: DataFrame, clientes: DataFrame, campanhas: DataFrame) -> DataFrame:
    """Adiciona atributos de cliente e campanha às vendas."""
    return (vendas.join(clientes.select("id_cliente", "nome", "cidade", "segmento"), "id_cliente", "inner")
            .join(campanhas.select("id_campanha", "nome_campanha", "canal"), "id_campanha", "inner")
            .withColumn("mes_venda", F.date_trunc("month", "data_venda").cast("date")))


def transformar_dados(dados: dict[str, DataFrame]) -> dict[str, DataFrame]:
    """Constrói e mantém em cache as bases reutilizadas pelos indicadores."""
    interacoes = consolidar_interacoes(dados["interacoes"]).cache()
    vendas = enriquecer_vendas(dados["vendas"], dados["clientes"], dados["campanhas"]).cache()
    return {**dados, "interacoes_consolidadas": interacoes, "vendas_enriquecidas": vendas}

