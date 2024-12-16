import os
import http.client
import json
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta
import holidays
import plotly.graph_objects as go

# Caminhos:
caminho_local = os.getcwd()
caminho_local = os.path.join(caminho_local, "Data_files")

# Função para criar pastas:
def criar_pasta(caminho):
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        print(f"Pasta '{caminho}' criada com sucesso.")
    else:
        print(f"A pasta '{caminho}' já existe.")

criar_pasta(caminho_local)
criar_pasta(os.path.join(caminho_local, "Bronze"))
criar_pasta(os.path.join(caminho_local, "Silver"))
criar_pasta(os.path.join(caminho_local, "Gold"))

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)

# Parâmetros:
symbols = ['MSFT','TSLA','GOOGL','AMZN','META','AAPL','INTC','ORCL','ADBE','NVDA']
api_token = 'sLnVmn2Rv8MAjQ2DgJfx8lMlWGlCJ8pyRZv74ZZn'
url = http.client.HTTPSConnection('api.stockdata.org')
data_inicial = '2024-11-25'

# Função para formatar datas:
def formatar_data(data, formato='%Y-%m-%d'):
    """Converte data entre string e datetime."""
    if isinstance(data, str):
        return datetime.strptime(data, formato)
    return data.strftime(formato)

# Função para calcular dias entre datas definidas:
def calcular_dias(data_inicial, data_final):

    data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')

    data_final = datetime.strptime(data_final, '%Y-%m-%d')


    delta = data_final - data_inicial

    dias = [(data_inicial + timedelta(days=i - 1)).strftime('%Y-%m-%d') for i in range(delta.days)]

    return dias

# Função  para calcular dias retroativos:
def calcular_dias_hoje(data_inicial):
    """Calcula os dias entre a data inicial e hoje."""
    data_inicial = formatar_data(data_inicial)
    data_hoje = datetime.today()
    delta = (data_hoje - data_inicial).days
    return [(data_hoje - timedelta(days=i + 1)).strftime('%Y-%m-%d') for i in range(delta - 1)]

# Função para calcular dias úteis:
def calcular_dias_uteis(data_inicial):
    """Calcula os próximos 10 dias úteis a partir da data inicial."""
    data_inicial = formatar_data(data_inicial)
    dias_uteis = []
    data_atual = data_inicial
    while len(dias_uteis) < 10:
        if data_atual.weekday() < 5:  # Semana: 0-4 são úteis.
            dias_uteis.append(data_atual.strftime('%Y-%m-%d'))
        data_atual += timedelta(days=1)
    return dias_uteis


# Função para acessar a API:
def get_data(symbol, data_inicial, data_final):
    """Busca dados de ações na API."""
    parametros = urllib.parse.urlencode({
        'api_token': api_token,
        'symbols': symbol,
        'sort': 'asc',
        'date_from': data_inicial,
        'date_to': data_final,
    })

    url.request('GET', f'/v1/data/eod?{parametros}')
    res = url.getresponse()
    if res.status != 200:
        print(f"Erro na API para {symbol}: {res.status} - {res.reason}")
        return {}
    data = res.read()
    return json.loads(data.decode('utf-8'))

# Processamento dos dados:
data_final = calcular_dias_uteis(data_inicial)[-1]
print(f"Data Inicial Full Load: {data_inicial}\nData_final Full Load: {data_final}")

# Caminho do arquivo JSON:
arquivo_json = f"{caminho_local}/Bronze/stock_data_bronze.json"

# Carregando ou criando full load inicial:
if not os.path.exists(arquivo_json):
    print(f"O arquivo '{arquivo_json}' não existe, full load iniciado...")
    full_load = []
    for symbol in symbols:
        try:
            json_data = get_data(symbol, data_inicial, data_final)
            if 'data' in json_data:
                for record in json_data['data']:
                    record['symbol'] = symbol
                full_load.extend(json_data['data'])
            else:
                print(f"Nenhum dado encontrado para {symbol}.")
        except Exception as e:
            print(f"Erro ao buscar dados para {symbol}: {e}")

    with open(arquivo_json, 'w') as json_file:
        json.dump(full_load, json_file, indent=4)
    print(f"Arquivo '{arquivo_json}' salvo com sucesso.")
else:
    print(f"O arquivo '{arquivo_json}' já existe.")

# Extração do DF do Full Load de JSON:
with open(arquivo_json, 'r') as file:
    dados_json = json.load(file)

df_full_load = pd.DataFrame(dados_json)

#Calcula o incremento de dias
df_full_load['date'] = pd.to_datetime(df_full_load['date']).dt.strftime('%Y-%m-%d')
dias_existente = df_full_load['date'].unique()
dias_hoje = calcular_dias_hoje(data_inicial)

# Filtrando dias sem feriados e fins de semana:
usa_feriados = holidays.US(years=2024)
feriados = set(usa_feriados.keys())

dias_sem_feriados_e_fins_de_semana = [
    dia for dia in dias_hoje
    if datetime.strptime(dia, '%Y-%m-%d').date() not in feriados
    and datetime.strptime(dia, '%Y-%m-%d').weekday() < 5]

# Remove finais de semana e feriados e calcula os dias faltantes
dias_faltantes = [dia for dia in dias_hoje if dia not in dias_existente]
dias_faltantes_real = [dia for dia in dias_sem_feriados_e_fins_de_semana if dia not in dias_existente]

# Resultados:
if dias_faltantes_real:
    print(f"Dias faltantes (sem feriados e finais de semana): {dias_faltantes_real}")

dt_inicial = dias_faltantes[-1]
dt_final = dias_faltantes[0]

if dias_faltantes_real:
    print(f"Os dias faltantes são: {dias_faltantes_real}")

    # Carrega dados existentes, se houver:
    if os.path.exists(arquivo_json):
        with open(arquivo_json, 'r') as json_file:
            dados_existentes = json.load(json_file)
    else:
        dados_existentes = []

    for symbol in symbols:
        try:
            json_data = get_data(symbol, dt_inicial, dt_final)
            if 'data' in json_data:
                for record in json_data['data']:
                    record['symbol'] = symbol
                dados_existentes.extend(json_data['data'])
            else:
                print(f"Nenhum dado encontrado para {symbol}.")
        except Exception as e:
            print(f"Erro ao buscar dados para {symbol}: {e}")

    with open(arquivo_json, 'w') as json_file:
        json.dump(dados_existentes, json_file, indent=4)
    print(f"Dados incrementados no arquivo '{arquivo_json}'.")
else:
    print("Não há dias faltantes.")

# Criando camada silver com tratamento de dados
with open(arquivo_json, 'r') as file:
    dados_json = json.load(file)

stock_data_silver = pd.DataFrame(dados_json)

stock_data_silver['date'] = pd.to_datetime(stock_data_silver['date'])
stock_data_silver['date'] = stock_data_silver['date'].dt.strftime('%d-%m-%Y')

symbol_names = {
    'MSFT': 'Microsoft', 'TSLA': 'Tesla', 'GOOGL': 'Google', 'AMZN': 'Amazon',
    'META': 'Facebook', 'AAPL': 'Apple', 'INTC': 'Intel', 'ORCL': 'Oracle',
    'ADBE': 'Adobe', 'NVDA': 'Nvidia'
}
stock_data_silver['company'] = stock_data_silver['symbol'].map(symbol_names)

# Salva dados da camada silver em parquet
arquivo_silver = f"{caminho_local}/Silver/stock_data_silver.parquet"
stock_data_silver.to_parquet(arquivo_silver)
print(f"Arquivo Parquet salvo em: {arquivo_silver}")

# Extrai o DF do parquet
arquivo_silver_df = pd.read_parquet(arquivo_silver)

# Tratamentos para camada Gold
stock_data_gold = arquivo_silver_df.rename(columns={'symbol': 'codigo_acao'})
stock_data_gold = stock_data_gold.drop(columns=['high', 'low', 'volume', 'company'])

stock_data_gold['dia'] = pd.to_datetime(stock_data_gold['date'], dayfirst=True)
stock_data_gold['preco'] = ((stock_data_gold['open'] + stock_data_gold['close']) / 2).round(2)
stock_data_gold = stock_data_gold.drop(columns=['date', 'close', 'open'])
stock_data_gold['preco'] = pd.to_numeric(stock_data_gold['preco'], errors='coerce')

# Salva dados da camada Gold em parquet
arquivo_gold = f"{caminho_local}/Gold/stock_data_gold.parquet"
stock_data_gold.to_parquet(arquivo_gold)
print(f"Arquivo Parquet salvo em: {arquivo_gold}")

# Extrai o DF do parquet
arquivo_gold_df = pd.read_parquet(arquivo_gold)

# Tratamento final para plot de gráfico
periodo = len(calcular_dias(data_inicial, dt_final))
arquivo_gold_df = arquivo_gold_df.groupby(['codigo_acao', 'dia']).agg({'preco': 'mean'}).reset_index()
arquivo_gold_df = arquivo_gold_df.sort_values(by='dia', ascending=True)

# Criando o gráfico
fig = go.Figure()
for symbol in symbols:
    dados_acao = arquivo_gold_df[arquivo_gold_df['codigo_acao'] == symbol]
    fig.add_trace(go.Scatter(x=dados_acao['dia'], y=dados_acao['preco'], mode='lines', name=symbol))

fig.update_layout(
    title=f'Evolução dos Preços de 10 Ações (Período de {periodo} dias)',
    xaxis_title='Dias',
    yaxis_title='Preço',
    legend_title='Ações',
    showlegend=True
)

fig.write_image("grafico_precos_acoes.jpg")


fig.show()