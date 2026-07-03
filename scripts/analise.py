"""Indicadores de negócio do pipeline de marketing."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def desempenho_campanhas(dados: dict[str, DataFrame]) -> DataFrame:
    """Calcula receita, engajamento, conversão e ticket por campanha."""
    def taxa_segura(numerador: str) -> F.Column:
        return F.when(
            F.col("clientes_impactados") > 0,
            F.round(F.col(numerador) / F.col("clientes_impactados") * 100, 2),
        ).otherwise(F.lit(0.0))

    interacoes = (dados["interacoes_consolidadas"].groupBy("id_campanha")
                  .agg(F.countDistinct("id_cliente").alias("clientes_impactados"),
                       F.sum("abriu").alias("aberturas"), F.sum("clicou").alias("cliques")))
    vendas = (dados["vendas_enriquecidas"].groupBy("id_campanha")
              .agg(F.round(F.sum("valor"), 2).alias("receita"), F.count("id_venda").alias("vendas"),
                   F.countDistinct("id_cliente").alias("clientes_convertidos"),
                   F.round(F.avg("valor"), 2).alias("ticket_medio")))
    return (dados["campanhas"].select("id_campanha", "nome_campanha", "canal")
            .join(interacoes, "id_campanha", "left").join(vendas, "id_campanha", "left")
            .fillna(0)
            .withColumn("taxa_abertura", taxa_segura("aberturas"))
            .withColumn("taxa_clique", taxa_segura("cliques"))
            .withColumn("taxa_conversao", taxa_segura("clientes_convertidos")))


def receita_por_dimensao(vendas: DataFrame, dimensao: str) -> DataFrame:
    """Agrega receita e vendas por uma dimensão categórica."""
    return (vendas.groupBy(dimensao)
            .agg(F.round(F.sum("valor"), 2).alias("receita"), F.count("id_venda").alias("quantidade_vendas"))
            .orderBy(F.desc("receita")))


def gerar_indicadores(dados: dict[str, DataFrame]) -> dict[str, DataFrame]:
    """Produz todos os indicadores solicitados para análise e exportação."""
    vendas = dados["vendas_enriquecidas"]
    desempenho = desempenho_campanhas(dados).cache()
    ranking = desempenho.withColumn("posicao", F.dense_rank().over(Window.orderBy(F.desc("receita"), F.desc("taxa_conversao"))))
    top_clientes = (vendas.groupBy("id_cliente", "nome", "cidade", "segmento")
                    .agg(F.round(F.sum("valor"), 2).alias("faturamento"), F.count("id_venda").alias("compras"))
                    .orderBy(F.desc("faturamento")).limit(10))
    compradores = vendas.select("id_cliente").distinct()
    abriu_sem_comprar = (dados["interacoes_consolidadas"].filter(F.col("abriu") == 1)
                         .select("id_cliente").distinct().join(compradores, "id_cliente", "left_anti")
                         .join(dados["clientes"], "id_cliente", "inner").orderBy("id_cliente"))
    evolucao = (vendas.groupBy("mes_venda")
                .agg(F.round(F.sum("valor"), 2).alias("receita"), F.count("id_venda").alias("vendas"),
                     F.round(F.avg("valor"), 2).alias("ticket_medio")).orderBy("mes_venda"))
    return {
        "desempenho_campanhas": desempenho.orderBy(F.desc("receita")),
        "receita_por_cidade": receita_por_dimensao(vendas, "cidade"),
        "receita_por_segmento": receita_por_dimensao(vendas, "segmento"),
        "ranking_campanhas": ranking.orderBy("posicao"),
        "top_10_clientes": top_clientes,
        "clientes_abriu_nunca_comprou": abriu_sem_comprar,
        "evolucao_mensal_vendas": evolucao,
    }
