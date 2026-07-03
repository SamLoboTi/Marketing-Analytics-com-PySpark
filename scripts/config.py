"""Configurações e caminhos compartilhados pelo projeto."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
GRAFICOS_DIR = OUTPUT_DIR / "graficos"

CSV_OPTIONS = {
    "header": True,
    "sep": ",",
    "encoding": "UTF-8",
    "mode": "PERMISSIVE",
}

