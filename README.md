# TDD-API
Este repositório contém o código do TDD 02, abordando a usabilidade de APIs para coleta de dados e o armazenamento em pipelines estruturados (Bronze, Silver e Gold).

# Descrição do Projeto
Este projeto realiza o monitoramento de dados de ações através do uso da API "Stockdata.org". Ele coleta informações financeiras do preço das ações em um periodo de tempo, armazena os dados em diferentes camadas (Bronze, Silver e Gold) e realiza visualizações gráficas para análise da evolução dos preços através da média diária.

# Recursos Utilizados
O código foi feito utilizando a linguagem python e as principais bibliotecas utilizadas foram:

  - os
  - http.client
  - json
  - pandas
  - urllib.parse
  - datetime
  - holidays
  - plotly

# Estrutura de Pastas
O projeto cria as seguintes pastas para organizar os dados:

Bronze: Armazena os dados brutos extraídos da API em formato JSON.
Silver: Contém dados tratados e organizados em formato Parquet.
Gold: Dados finais otimizados para análise e visualizações.

# Execução do Código
O código verifica o diretório atual, cria as pastas necessárias e define parâmetros, como o período de análise, símbolos das ações e a chave da API.

### Extração e Processamento de Dados:

  - Os dados de ações são extraídos da API StockData.org por meio do endpoint "/v1/data/eod", que monitora os valores historicos do preço de fechamento das ações.
O arquivo JSON inicial é salvo na camada Bronze.

  - A camada Silver organiza os dados em um DataFrame com mapeamento de nomes das empresas e formato tratado.
    
  - A camada Gold calcula o preço médio diário ((valor do fechamento - valor da abertura) / 2) e remove colunas desnecessárias para visualização, salvando os dados otimizados.
    
  - Visualização de Dados: Um gráfico é criado utilizando a biblioteca Plotly, apresentando a evolução dos preços das ações ao longo do tempo.

# Parâmetros Configuráveis
Símbolos das Ações: Lista das ações a serem analisadas
  - symbols = ['MSFT', 'TSLA', 'GOOGL', 'AMZN', 'META', 'AAPL', 'INTC', 'ORCL', 'ADBE', 'NVDA']
    
Token da API: Chave para acesso à API:
  - api_token = 'sLnVmn2Rv8MAjQ2DgJfx8lMlWGlCJ8pyRZv74ZZn'
    
Data Inicial: Data para início da análise:
  - data_inicial = '2024-11-25'

# Saída do Projeto
Arquivos Gerados:

  - Camada Bronze: stock_data_bronze.json
  - Camada Silver: stock_data_silver.parquet
  - Camada Gold: stock_data_gold.parquet
  - Gráfico Gerado: Exibe a evolução dos preços médios diários para cada uma das ações analisadas.
