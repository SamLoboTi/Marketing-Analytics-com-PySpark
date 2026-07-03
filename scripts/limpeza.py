"""Regras de qualidade e padronização das entidades."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def limpar_clientes(df: DataFrame) -> DataFrame:
    """Remove registros inválidos, deduplica e completa dimensões ausentes."""
    return (df.filter(F.col("id_cliente").isNotNull())
            .dropDuplicates(["id_cliente"])
            .fillna({"nome": "Não informado", "cidade": "Não informada", "segmento": "Não informado"})
            .withColumn("idade", F.when(F.col("idade").between(18, 100), F.col("idade"))))


def limpar_campanhas(df: DataFrame) -> DataFrame:
    """Mantém campanhas válidas e padroniza texto."""
    return (df.filter(F.col("id_campanha").isNotNull() & (F.col("data_fim") >= F.col("data_inicio")))
            .dropDuplicates(["id_campanha"])
            .fillna({"nome_campanha": "Campanha sem nome", "canal": "Não informado"})
            .withColumn("canal", F.initcap(F.trim("canal"))))


def limpar_interacoes(df: DataFrame) -> DataFrame:
    """Normaliza flags binárias e remove interações repetidas."""
    return (df.filter(F.col("id_cliente").isNotNull() & F.col("id_campanha").isNotNull())
            .fillna({"abriu": 0, "clicou": 0})
            .withColumn("abriu", F.when(F.col("abriu") == 1, 1).otherwise(0))
            .withColumn("clicou", F.when((F.col("clicou") == 1) & (F.col("abriu") == 1), 1).otherwise(0))
            .dropDuplicates(["id_cliente", "id_campanha", "data_interacao"]))


def limpar_vendas(df: DataFrame) -> DataFrame:
    """Remove vendas sem chave, sem data ou com valor inválido."""
    return (df.filter(F.col("id_venda").isNotNull() & F.col("data_venda").isNotNull() & (F.col("valor") > 0))
            .dropDuplicates(["id_venda"])
            .withColumn("valor", F.round("valor", 2)))


def limpar_dados(dados: dict[str, DataFrame]) -> dict[str, DataFrame]:
    """Aplica as regras de limpeza a todas as entidades."""
    return {
        "clientes": limpar_clientes(dados["clientes"]),
        "campanhas": limpar_campanhas(dados["campanhas"]),
        "interacoes": limpar_interacoes(dados["interacoes"]),
        "vendas": limpar_vendas(dados["vendas"]),
    }

