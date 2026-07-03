"""Ponto de entrada do pipeline de marketing."""

import logging
import os
import shutil
import sys
from pathlib import Path

from pyspark.sql import SparkSession

from scripts.analise import gerar_indicadores
from scripts.exportacao import exportar_indicadores, preparar_output
from scripts.gerar_dados import gerar_dados
from scripts.ingestao import carregar_dados
from scripts.limpeza import limpar_dados
from scripts.transformacao import transformar_dados
from scripts.visualizacao import gerar_dashboard, gerar_diagrama_arquitetura, gerar_graficos
from scripts.config import ROOT_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
LOGGER = logging.getLogger("marketing-pyspark")


def criar_spark() -> SparkSession:
    """Cria uma sessão Spark local adequada ao volume do projeto."""
    hadoop_local = ROOT_DIR / ".runtime" / "hadoop"
    if not os.environ.get("HADOOP_HOME") and (hadoop_local / "bin" / "winutils.exe").exists():
        os.environ["HADOOP_HOME"] = os.fspath(hadoop_local)
        os.environ["PATH"] = f"{hadoop_local / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}"
    if not os.environ.get("JAVA_HOME") and not shutil.which("java"):
        java_local = next((ROOT_DIR / ".runtime" / "java").glob("*/bin/java.exe"), None)
        if java_local:
            os.environ["JAVA_HOME"] = os.fspath(java_local.parents[1])
    os.environ.setdefault("PYSPARK_PYTHON", os.fspath(Path(sys.executable)))
    return (SparkSession.builder.appName("MarketingAnalytics")
            .master("local[*]").config("spark.sql.shuffle.partitions", "8")
            .config("spark.ui.enabled", "false").getOrCreate())


def executar_pipeline() -> None:
    """Orquestra todas as etapas e encerra recursos com segurança."""
    LOGGER.info("Preparando dados e diretórios")
    gerar_dados()
    preparar_output()
    spark = criar_spark()
    spark.sparkContext.setLogLevel("WARN")
    bases_cache = []
    try:
        LOGGER.info("Executando ingestão e limpeza")
        dados = limpar_dados(carregar_dados(spark))
        LOGGER.info("Executando transformações e análises")
        transformados = transformar_dados(dados)
        bases_cache.extend([transformados["interacoes_consolidadas"], transformados["vendas_enriquecidas"]])
        indicadores = gerar_indicadores(transformados)
        bases_cache.append(indicadores["desempenho_campanhas"])
        LOGGER.info("Exportando indicadores e visualizações")
        exportar_indicadores(indicadores)
        gerar_graficos(indicadores)
        gerar_dashboard(indicadores)
        gerar_diagrama_arquitetura()
        LOGGER.info("Pipeline concluído. Resultados disponíveis em output/")
    finally:
        for base in bases_cache:
            base.unpersist()
        spark.stop()


if __name__ == "__main__":
    executar_pipeline()
