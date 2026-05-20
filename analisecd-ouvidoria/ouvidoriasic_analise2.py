# ==========================================================
# 📊 CONFIGURAÇÃO INICIAL E LEITURA DOS DADOS
# ==========================================================
import pandas as pd
import matplotlib.pyplot as plt
# Carregando o arquivo com o separador correto e codificação para português
dados = pd.read_csv("ouvidoriasic.csv", sep=";", encoding="latin1")

# Limpando os nomes das colunas (remove quebras de linha e espaços extras)
dados.columns = dados.columns.str.strip().str.replace('\n', '').str.replace('\r', '')

colunas_texto = dados.select_dtypes(include=["object", "string"]).columns

# ==========================================================
# CORREÇÃO DE ACENTOS E TEXTOS QUEBRADOS
# ==========================================================

# Convertendo as colunas de data para o formato correto do Pandas
dados['Data de Abertura'] = pd.to_datetime(dados['Data de Abertura'], errors='coerce', dayfirst=True)
dados['Data Resp. Concl.'] = pd.to_datetime(dados['Data Resp. Concl.'], errors='coerce', dayfirst=True)

# Criando as colunas necessárias para a análise baseada no cabeçalho real
dados['tempo_resposta'] = (dados['Data Resp. Concl.'] - dados['Data de Abertura']).dt.days
dados['mes'] = dados['Data de Abertura'].dt.month

# ==========================================================
# CORREÇÃO DE ACENTOS E TEXTOS QUEBRADOS
# ==========================================================

traducao_acentos = {

    # =========================
    # TIPOS DE MANIFESTAÇÃO
    # =========================
    "Reclamao": "Reclamação",
    "Comunicao": "Comunicação",
    "Solicitao": "Solicitação",
    "Denncia": "Denúncia",
    "Sugesto": "Sugestão",
    "Elogio": "Elogio",
    "Acesso  Informao": "Acesso à Informação",

    # =========================
    # ASSUNTOS
    # =========================
    "Servios Pblicos": "Serviços Públicos",
    "Servios Urbanos": "Serviços Urbanos",
    "Outros em Administrao": "Outros em Administração",
    "Outros em Sade": "Outros em Saúde",
    "Outros em Educao": "Outros em Educação",
    "Fiscalizao do Estado": "Fiscalização do Estado",
    "Coronavrus (COVID-19)": "Coronavírus (COVID-19)",

    # =========================
    # PALAVRAS GERAIS
    # =========================
    "Informao": "Informação",
    "Municpio": "Município",
    "rgo": "Órgão",
    "Pblico": "Público",
    "Sade": "Saúde",
    "Educao": "Educação",
    "Administrao": "Administração",
    "Fiscalizao": "Fiscalização",
    "Solicitaes": "Solicitações",
    "Manifestao": "Manifestação",
    "Concluso": "Conclusão",
    "Situao": "Situação",
    "Resposta": "Resposta",
    "Abertura": "Abertura",
    "Destinatrio": "Destinatário",

    # =========================
    # CARACTERES QUEBRADOS
    # =========================
    "ï¿½": "",
    "Ã§": "ç",
    "Ã£": "ã",
    "Ã¡": "á",
    "Ã©": "é",
    "Ãª": "ê",
    "Ã³": "ó",
    "Ãº": "ú",
    "Ã": "à"
}
colunas_texto = dados.select_dtypes(include=["object", "string"]).columns

for col in colunas_texto:
    dados[col] = dados[col].astype(str).str.strip()

    for errado, correto in traducao_acentos.items():
        dados[col] = dados[col].str.replace(errado, correto, regex=False)
# ==========================================================
# LIMPEZA DA COLUNA PRAZO
# ==========================================================

dados['Prazo de Resposta'] = (
    dados['Prazo de Resposta']
    .astype(str)
    .str.extract(r'(\d+)')[0]
)

dados['Prazo de Resposta'] = pd.to_numeric(
    dados['Prazo de Resposta'],
    errors='coerce'
)

prazo = dados['Prazo de Resposta'].dropna()


# ==========================================================
# HISTOGRAMAS + MÉDIA + MEDIANA + DESVIO PADRÃO
# ==========================================================

# ==========================================================
# VARIÁVEL 1 -> TEMPO DE RESPOSTA
# ==========================================================

# Filtrando apenas valores válidos e positivos de tempo de resposta
tempo = dados['tempo_resposta'].dropna()
tempo = tempo[tempo >= 0]

media_tempo = tempo.mean()
mediana_tempo = tempo.median()
desvio_tempo = tempo.std()

plt.figure(figsize=(10,6))
plt.hist(tempo, bins=20, color="steelblue", edgecolor="black", alpha=0.8)

# Linhas da média e mediana
plt.axvline(media_tempo, color="red", linestyle="--", linewidth=2, label=f"Média = {media_tempo:.2f}")
plt.axvline(mediana_tempo, color="green", linestyle="-", linewidth=2, label=f"Mediana = {mediana_tempo:.2f}")

plt.title("Histograma - Tempo de Resposta")
plt.xlabel("Dias")
plt.ylabel("Frequência")
plt.legend()
plt.show()

print("\n==============================")
print("ESTATÍSTICAS - TEMPO DE RESPOSTA")
print("==============================")
print(f"Média: {media_tempo:.2f} dias")
print(f"Mediana: {mediana_tempo:.2f} dias")
print(f"Desvio Padrão: {desvio_tempo:.2f} dias")


# ==========================================================
# VARIÁVEL 2 -> MÊS DAS SOLICITAÇÕES
# ==========================================================

# Filtrando os meses válidos (de 1 a 12)
meses = dados['mes'].dropna().astype(int)
meses = meses[(meses >= 1) & (meses <= 12)]

media_mes = meses.mean()
mediana_mes = meses.median()
desvio_mes = meses.std()

plt.figure(figsize=(10,6))
plt.hist(meses, bins=12, range=(0.5, 12.5), color="orange", edgecolor="black", alpha=0.8)

# Linhas da média e mediana
plt.axvline(media_mes, color="red", linestyle="--", linewidth=2, label=f"Média = {media_mes:.2f}")
plt.axvline(mediana_mes, color="green", linestyle="-", linewidth=2, label=f"Mediana = {mediana_mes:.2f}")

plt.title("Histograma - Distribuição por Mês")
plt.xlabel("Mês do Ano")
plt.ylabel("Frequência")
plt.xticks(range(1, 13))
plt.legend()
plt.show()

print("\n==============================")
print("ESTATÍSTICAS - DISTRIBUIÇÃO POR MÊS")
print("==============================")
print(f"Média: {media_mes:.2f}")
print(f"Mediana: {mediana_mes:.2f}")
print(f"Desvio Padrão: {desvio_mes:.2f}")

# ==========================================================
# VARIÁVEL 3 -> CANAL DE ENTRADA
# ==========================================================

canal_freq = dados['Canal de Entrada'].value_counts()

media_canal = canal_freq.mean()
mediana_canal = canal_freq.median()
desvio_canal = canal_freq.std()

plt.figure(figsize=(10,6))

plt.hist(
    canal_freq,
    bins=10,
    color="teal",
    edgecolor="black",
    alpha=0.8
)

plt.axvline(media_canal, color="red", linestyle="--", linewidth=2, label=f"Média = {media_canal:.2f}")
plt.axvline(mediana_canal, color="green", linestyle="-", linewidth=2, label=f"Mediana = {mediana_canal:.2f}")

plt.title("Histograma - Canal de Entrada")
plt.xlabel("Quantidade")
plt.ylabel("Frequência")

plt.legend()
plt.show()

print("\n==============================")
print("ESTATÍSTICAS - CANAL DE ENTRADA")
print("==============================")
print(f"Média: {media_canal:.2f}")
print(f"Mediana: {mediana_canal:.2f}")
print(f"Desvio Padrão: {desvio_canal:.2f}")

# ==========================================================
# VARIÁVEL 4 -> TIPO DE MANIFESTAÇÃO
# ==========================================================

tipo_freq = dados['Tipo'].value_counts()

media_tipo = tipo_freq.mean()
mediana_tipo = tipo_freq.median()
desvio_tipo = tipo_freq.std()

plt.figure(figsize=(10,6))

plt.hist(
    tipo_freq,
    bins=10,
    color="orange",
    edgecolor="black",
    alpha=0.8
)

plt.axvline(media_tipo, color="red", linestyle="--", linewidth=2, label=f"Média = {media_tipo:.2f}")
plt.axvline(mediana_tipo, color="green", linestyle="-", linewidth=2, label=f"Mediana = {mediana_tipo:.2f}")

plt.title("Histograma - Tipo de Manifestação")
plt.xlabel("Quantidade")
plt.ylabel("Frequência")

plt.legend()
plt.show()

print("\n==============================")
print("ESTATÍSTICAS - TIPO DE MANIFESTAÇÃO")
print("==============================")
print(f"Média: {media_tipo:.2f}")
print(f"Mediana: {mediana_tipo:.2f}")
print(f"Desvio Padrão: {desvio_tipo:.2f}")

# ==========================================================
# GRÁFICO 1 -> TEMPO DE RESPOSTA (ASSIMETRIA POSITIVA)
# ==========================================================

import seaborn as sns

tempo = dados['tempo_resposta'].dropna()
tempo = tempo[tempo >= 0]

media = tempo.mean()
mediana = tempo.median()

plt.figure(figsize=(10,6))

sns.histplot(
    tempo,
    bins=25,
    kde=True,
    color="skyblue",
    edgecolor="black"
)

plt.axvline(media, color="red", linestyle="--", linewidth=2, label=f"Média = {media:.2f}")
plt.axvline(mediana, color="green", linestyle="-", linewidth=2, label=f"Mediana = {mediana:.2f}")

plt.title("Distribuição do Tempo de Resposta")
plt.xlabel("Dias")
plt.ylabel("Frequência")

plt.legend()
plt.show()

print("\nANÁLISE:")
print("1. O gráfico apresenta concentração em menores tempos.")
print("2. A cauda à direita indica assimetria positiva.")
print("3. A diferença entre média e mediana sugere presença de valores extremos.")

# ==========================================================
# GRÁFICO 2 -> PRAZO DE RESPOSTA
# ==========================================================

dados['Prazo de Resposta'] = pd.to_numeric(
    dados['Prazo de Resposta'],
    errors='coerce'
)

prazo = dados['Prazo de Resposta'].dropna()

media = prazo.mean()
mediana = prazo.median()

plt.figure(figsize=(10,6))

sns.histplot(
    prazo,
    bins=20,
    kde=True,
    color="orange",
    edgecolor="black"
)

plt.axvline(media, color="red", linestyle="--", linewidth=2, label=f"Média = {media:.2f}")
plt.axvline(mediana, color="green", linestyle="-", linewidth=2, label=f"Mediana = {mediana:.2f}")

plt.title("Distribuição do Prazo de Resposta")
plt.xlabel("Prazo")
plt.ylabel("Frequência")

plt.legend()
plt.show()

print("\nANÁLISE:")
print("1. O gráfico mostra concentração próxima ao prazo médio.")
print("2. A dispersão indica variabilidade entre os registros.")
print("3. Os valores extremos aumentam a média da distribuição.")

# ==========================================================
# GRÁFICO 3 -> DISTRIBUIÇÃO DOS MESES
# ==========================================================

meses = dados['mes'].dropna()

media = meses.mean()
mediana = meses.median()

plt.figure(figsize=(10,6))

sns.histplot(
    meses,
    bins=12,
    kde=True,
    color="purple",
    edgecolor="black"
)

plt.axvline(media, color="red", linestyle="--", linewidth=2, label=f"Média = {media:.2f}")
plt.axvline(mediana, color="green", linestyle="-", linewidth=2, label=f"Mediana = {mediana:.2f}")

plt.title("Distribuição das Solicitações por Mês")
plt.xlabel("Mês")
plt.ylabel("Frequência")

plt.legend()
plt.show()

print("\nANÁLISE:")
print("1. O gráfico mostra variação na quantidade de solicitações.")
print("2. Existem meses com maior concentração de registros.")
print("3. A distribuição apresenta dispersão moderada.")

# ==========================================================
# GRÁFICO 4 -> DISTRIBUIÇÃO DOS TIPOS (CURVA)
# ==========================================================

import seaborn as sns

tipo_freq = dados['Tipo'].value_counts()

valores = tipo_freq.values

media = valores.mean()
mediana = pd.Series(valores).median()
desvio = pd.Series(valores).std()

plt.figure(figsize=(10,6))

# Curva de distribuição
sns.kdeplot(
    valores,
    fill=True,
    color="green",
    linewidth=2
)

# Média
plt.axvline(
    media,
    color="red",
    linestyle="--",
    linewidth=2,
    label=f"Média = {media:.2f}"
)

# Mediana
plt.axvline(
    mediana,
    color="blue",
    linestyle="-",
    linewidth=2,
    label=f"Mediana = {mediana:.2f}"
)

plt.title("Distribuição dos Tipos de Manifestação")
plt.xlabel("Quantidade")
plt.ylabel("Densidade")

plt.legend()
plt.show()

print("\n==============================")
print("ESTATÍSTICAS - TIPOS")
print("==============================")
print(f"Média: {media:.2f}")
print(f"Mediana: {mediana:.2f}")
print(f"Desvio Padrão: {desvio:.2f}")

print("\nANÁLISE:")
print("1. O gráfico apresenta assimetria na distribuição.")
print("2. A média diferente da mediana indica concentração desigual.")
print("3. O desvio padrão mostra alta dispersão entre os tipos.")