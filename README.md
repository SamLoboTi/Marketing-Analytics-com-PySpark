# Marketing Analytics com PySpark

Projeto de portfólio que simula o pipeline analítico de uma empresa de marketing digital. A solução transforma dados de clientes, campanhas, interações e vendas em indicadores acionáveis, arquivos analíticos, gráficos e um dashboard HTML.

## Problema de negócio

A equipe de marketing precisa avaliar quais campanhas geram receita e engajamento, entender o perfil geográfico e setorial do faturamento e identificar oportunidades de conversão. O pipeline consolida essas perguntas em uma execução reproduzível.

## Arquitetura da solução

![Arquitetura](output/arquitetura.svg)

`CSV → ingestão com schema → qualidade → transformação → indicadores → CSV/Parquet → gráficos/dashboard`

- **Ingestão:** leitura dos arquivos com schemas explícitos.
- **Qualidade:** chaves válidas, padronização, nulos e duplicidades.
- **Transformação:** consolidação da jornada e enriquecimento das vendas.
- **Análise:** métricas de receita, engajamento, conversão e clientes.
- **Consumo:** CSV, Parquet, PNG e dashboard Plotly autocontido.

## Tecnologias

- Python 3.12
- Apache Spark / PySpark 4.1
- Matplotlib
- Plotly
- Parquet e CSV

## Estrutura

```text
marketing-pyspark/
├── data/                   # fontes CSV fictícias
├── notebooks/              # espaço para análises exploratórias
├── output/                 # resultados gerados
│   ├── csv/
│   ├── parquet/
│   ├── graficos/
│   ├── arquitetura.svg
│   └── dashboard.html
├── scripts/
│   ├── ingestao.py
│   ├── limpeza.py
│   ├── transformacao.py
│   ├── analise.py
│   ├── exportacao.py
│   ├── visualizacao.py
│   └── gerar_dados.py
├── main.py
├── requirements.txt
└── README.md
```

## Instalação

Pré-requisitos: Python 3.12 e Java 17 ou superior disponíveis no `PATH`.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

Na primeira execução, os quatro CSVs são criados de forma determinística em `data/`, com 3.000 a 9.000 registros por arquivo. Para recriá-los:

```bash
python -m scripts.gerar_dados
```

Após a execução, abra `output/dashboard.html` diretamente no navegador. Os resultados tabulares ficam em `output/csv/` e `output/parquet/`.

## Testes

Instale as dependências de desenvolvimento e execute a suíte:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes validam as principais regras de qualidade, a consolidação da jornada do cliente e os cálculos de receita, engajamento e conversão.

## Indicadores

- receita, abertura, clique, conversão e ticket médio por campanha;
- receita por cidade e segmento;
- ranking de campanhas e top 10 clientes;
- clientes que abriram campanhas, mas nunca compraram;
- evolução mensal de vendas.

As taxas usam clientes únicos impactados como denominador. A conversão considera clientes compradores únicos associados à campanha.

## Melhorias futuras

- processamento incremental e particionamento por período;
- catálogo de dados, observabilidade e alertas;
- orquestração com Airflow e armazenamento em nuvem;
- dashboard conectado a uma camada semântica atualizada.
