"""Leitura dos dados de origem com schemas explícitos."""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import DateType, DoubleType, IntegerType, StringType, StructField, StructType

from scripts.config import CSV_OPTIONS, DATA_DIR

SCHEMAS = {
    "clientes": StructType([
        StructField("id_cliente", IntegerType()), StructField("nome", StringType()),
        StructField("idade", IntegerType()), StructField("cidade", StringType()),
        StructField("segmento", StringType()),
    ]),
    "campanhas": StructType([
        StructField("id_campanha", IntegerType()), StructField("nome_campanha", StringType()),
        StructField("canal", StringType()), StructField("data_inicio", DateType()),
        StructField("data_fim", DateType()),
    ]),
    "interacoes": StructType([
        StructField("id_cliente", IntegerType()), StructField("id_campanha", IntegerType()),
        StructField("abriu", IntegerType()), StructField("clicou", IntegerType()),
        StructField("data_interacao", DateType()),
    ]),
    "vendas": StructType([
        StructField("id_venda", IntegerType()), StructField("id_cliente", IntegerType()),
        StructField("id_campanha", IntegerType()), StructField("valor", DoubleType()),
        StructField("data_venda", DateType()),
    ]),
}


def ler_csv(spark: SparkSession, nome: str) -> DataFrame:
    """Lê um CSV conhecido usando o schema definido para a entidade."""
    return spark.read.options(**CSV_OPTIONS).schema(SCHEMAS[nome]).csv(str(DATA_DIR / f"{nome}.csv"))


def carregar_dados(spark: SparkSession) -> dict[str, DataFrame]:
    """Carrega todas as fontes do pipeline."""
    return {nome: ler_csv(spark, nome) for nome in SCHEMAS}

