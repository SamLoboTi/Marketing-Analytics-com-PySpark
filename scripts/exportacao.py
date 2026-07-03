"""Persistência dos indicadores em formatos analíticos."""

import shutil
from pathlib import Path

from pyspark.sql import DataFrame

from scripts.config import OUTPUT_DIR


def _salvar(df: DataFrame, caminho: Path, formato: str) -> None:
    writer = df.coalesce(1).write.mode("overwrite")
    if formato == "csv":
        writer.option("header", True).option("encoding", "UTF-8").csv(str(caminho))
    else:
        writer.parquet(str(caminho))


def exportar_indicadores(indicadores: dict[str, DataFrame]) -> None:
    """Salva cada indicador em CSV e Parquet."""
    for formato in ("csv", "parquet"):
        destino = OUTPUT_DIR / formato
        destino.mkdir(parents=True, exist_ok=True)
        for nome, df in indicadores.items():
            _salvar(df, destino / nome, formato)


def preparar_output() -> None:
    """Remove somente artefatos gerados em execuções anteriores."""
    for nome in ("csv", "parquet", "graficos"):
        shutil.rmtree(OUTPUT_DIR / nome, ignore_errors=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

