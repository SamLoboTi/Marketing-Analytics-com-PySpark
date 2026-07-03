"""Gráficos, dashboard HTML e diagrama de arquitetura."""

from html import escape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from scripts.config import GRAFICOS_DIR, OUTPUT_DIR


def _coletar(df: DataFrame, categoria: str, valor: str, limite: int | None = None) -> tuple[list, list]:
    linhas = df.select(categoria, valor).limit(limite).collect() if limite else df.select(categoria, valor).collect()
    return [linha[categoria] for linha in linhas], [float(linha[valor] or 0) for linha in linhas]


def _grafico_barras(df: DataFrame, categoria: str, valor: str, titulo: str, arquivo: str, limite: int = 10) -> None:
    categorias, valores = _coletar(df, categoria, valor, limite)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh([str(item) for item in categorias][::-1], valores[::-1], color="#2563EB")
    ax.set(title=titulo, xlabel=valor.replace("_", " ").title(), ylabel=categoria.replace("_", " ").title())
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(GRAFICOS_DIR / arquivo, dpi=160, bbox_inches="tight")
    plt.close(fig)


def gerar_graficos(indicadores: dict[str, DataFrame]) -> None:
    """Gera cinco visualizações estáticas em PNG."""
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)
    _grafico_barras(indicadores["desempenho_campanhas"], "nome_campanha", "receita", "Receita por campanha — Top 10", "receita_campanha.png")
    _grafico_barras(indicadores["receita_por_segmento"], "segmento", "receita", "Receita por segmento", "receita_segmento.png")
    _grafico_barras(indicadores["receita_por_cidade"], "cidade", "receita", "Receita por cidade", "receita_cidade.png")
    conversao = indicadores["desempenho_campanhas"].orderBy("taxa_conversao", ascending=False)
    _grafico_barras(conversao, "nome_campanha", "taxa_conversao", "Conversão por campanha — Top 10", "conversao_campanha.png")
    meses, receitas = _coletar(indicadores["evolucao_mensal_vendas"], "mes_venda", "receita")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(meses, receitas, marker="o", color="#0F766E", linewidth=2)
    ax.set(title="Evolução mensal das vendas", xlabel="Mês", ylabel="Receita (R$)")
    ax.grid(alpha=0.25)
    fig.autofmt_xdate(); fig.tight_layout()
    fig.savefig(GRAFICOS_DIR / "evolucao_mensal.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def gerar_dashboard(indicadores: dict[str, DataFrame]) -> None:
    """Monta um dashboard Plotly autocontido, sem servidor web."""
    desempenho = indicadores["desempenho_campanhas"]
    total = desempenho.agg(F.sum("receita").alias("receita_total"), F.sum("vendas").alias("total_vendas")).first()
    top_nomes, top_receitas = _coletar(desempenho, "nome_campanha", "receita", 10)
    segmentos, receita_segmentos = _coletar(indicadores["receita_por_segmento"], "segmento", "receita")
    meses, receitas_mensais = _coletar(indicadores["evolucao_mensal_vendas"], "mes_venda", "receita")
    fig = make_subplots(rows=2, cols=2, specs=[[{"type": "indicator"}, {"type": "indicator"}], [{"type": "bar"}, {"type": "scatter"}]],
                        subplot_titles=("Receita total", "Total de vendas", "Receita por segmento", "Evolução mensal"))
    fig.add_trace(go.Indicator(mode="number", value=float(total["receita_total"] or 0), number={"prefix": "R$ ", "valueformat": ",.2f"}), 1, 1)
    fig.add_trace(go.Indicator(mode="number", value=int(total["total_vendas"] or 0)), 1, 2)
    fig.add_trace(go.Bar(x=segmentos, y=receita_segmentos, marker_color="#2563EB", name="Segmentos"), 2, 1)
    fig.add_trace(go.Scatter(x=meses, y=receitas_mensais, mode="lines+markers", line={"color": "#0F766E"}, name="Receita"), 2, 2)
    fig.update_layout(title="Dashboard de Performance de Marketing", template="plotly_white", height=800, showlegend=False,
                      margin={"l": 60, "r": 40, "t": 100, "b": 60})
    tabela = "".join(f"<tr><td>{escape(str(n))}</td><td>R$ {v:,.2f}</td></tr>" for n, v in zip(top_nomes, top_receitas))
    html = fig.to_html(full_html=False, include_plotlyjs=True)
    pagina = f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><title>Dashboard Marketing</title><style>body{{font-family:Arial;margin:24px;background:#f8fafc}}main{{max-width:1400px;margin:auto;background:white;padding:24px;border-radius:12px}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid #ddd;text-align:left}}</style></head><body><main>{html}<h2>Top 10 campanhas por receita</h2><table><thead><tr><th>Campanha</th><th>Receita</th></tr></thead><tbody>{tabela}</tbody></table></main></body></html>"
    (OUTPUT_DIR / "dashboard.html").write_text(pagina, encoding="utf-8")


def gerar_diagrama_arquitetura() -> None:
    """Cria um diagrama SVG simples do fluxo do pipeline."""
    etapas = ["Arquivos CSV", "PySpark", "Transformações", "Indicadores", "Dashboard", "Resultados"]
    blocos = []
    for i, etapa in enumerate(etapas):
        x = 30 + i * 190
        blocos.append(f'<rect x="{x}" y="55" width="150" height="60" rx="10" fill="#2563EB"/><text x="{x + 75}" y="91" text-anchor="middle" fill="white" font-family="Arial" font-size="14">{etapa}</text>')
        if i < len(etapas) - 1:
            blocos.append(f'<path d="M{x + 155} 85 H{x + 185}" stroke="#0F172A" stroke-width="3" marker-end="url(#seta)"/>')
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1170" height="170" viewBox="0 0 1170 170"><defs><marker id="seta" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#0F172A"/></marker></defs><rect width="100%" height="100%" fill="#F8FAFC"/>' + "".join(blocos) + "</svg>"
    (OUTPUT_DIR / "arquitetura.svg").write_text(svg, encoding="utf-8")
