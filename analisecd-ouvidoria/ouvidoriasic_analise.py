# =========================
# IMPORTAÇÃO
# =========================
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================
# CARREGAMENTO
# =========================
dados = pd.read_csv(
    "ouvidoriasic.csv",
    sep=";",
    encoding="latin1",
    engine="python",
    on_bad_lines="skip"
)

# ==========================================================
# TRATAMENTO DE ACENTUAÇÃO (LOSANGOS E MOJIBAKE)
# ==========================================================

# 1. Corrigir os títulos das colunas tirando qualquer caractere quebrado de forma segura
dados.columns = dados.columns.str.encode("latin1", errors="ignore").str.decode("utf-8", errors="ignore").str.strip()

# 2. Dicionário mapeando exatamente os erros que aparecem nos gráficos
traducao_acentos = {
    # Tipos de Manifestação 
    "Reclamao": "Reclamação",
    "Comunicao": "Comunicação",
    "Solicitao": "Solicitação",
    "Denncia": "Denúncia",
    "Acesso  Informao": "Acesso à Informação",
    "Sugesto": "Sugestão",
    
    # Assuntos
    "Servios Pblicos": "Serviços Públicos",
    "Servios Urbanos": "Serviços Urbanos",
    "Outros em Administrao": "Outros em Administração",
    "Outros em Sade": "Outros em Saúde",
    "Coronavrus (COVID-19)": "Coronavírus (COVID-19)",
    "Outros em Educao": "Outros em Educação",
    "Fiscalizao do Estado": "Fiscalização do Estado"
}

# 3. Aplicar a substituição direta nas colunas de texto do dataset
colunas_texto = dados.select_dtypes(include=['object']).columns

for col in colunas_texto:
    dados[col] = dados[col].astype(str).str.strip()
    dados[col] = dados[col].str.replace("ï¿½", "", regex=False)
    dados[col] = dados[col].replace(traducao_acentos, regex=False)

# =========================
# LIMPEZA E TRATAMENTO DE DATAS
# =========================
dados = dados.dropna(subset=["Tipo", "Assunto", "Canal de Entrada"])

dados["data_abertura"] = pd.to_datetime(
    dados["Data de Abertura"],
    errors="coerce",
    dayfirst=True
)

# Mapeando a coluna com quebra de linha: "Data \nResp. Concl."
dados["data_resposta"] = pd.to_datetime(
    dados.get('"Data \nResp. Concl."', None),
    errors="coerce",
    dayfirst=True
)

if dados["data_resposta"].isnull().all():
    dados["data_resposta"] = pd.to_datetime(
        dados.get("Data \nResp. Concl.", None),
        errors="coerce",
        dayfirst=True
    )

# Garante a existência da data de abertura
dados = dados.dropna(subset=["data_abertura"])
dados["mes"] = dados["data_abertura"].dt.month

# Calculando o tempo de resposta em dias
dados["tempo_resposta"] = (dados["data_resposta"] - dados["data_abertura"]).dt.days

# Tratamento para evitar valores nulos ou negativos na dispersão
dados["tempo_resposta"] = dados["tempo_resposta"].fillna(0)
dados.loc[dados["tempo_resposta"] < 0, "tempo_resposta"] = 0

# Tamanho do marcador para os gráficos Scatter
dados["tamanho_marcador"] = dados["tempo_resposta"] + 4

# =========================
# GRÁFICOS DE BARRA
# =========================

# 1. Barra - Tipos
tipo_df = dados["Tipo"].value_counts().reset_index()
tipo_df.columns = ["Tipo", "Quantidade"]
fig_barra1 = px.bar(tipo_df, x="Tipo", y="Quantidade", title="1 Barra: Tipos de Manifestação")
fig_barra1.show()

# 2. Barra - Assuntos
assunto_df = dados["Assunto"].value_counts().head(10).reset_index()
assunto_df.columns = ["Assunto", "Quantidade"]
fig_barra2 = px.bar(assunto_df, x="Assunto", y="Quantidade", title="2 Barra: Top 10 Assuntos")
fig_barra2.show()

# 3. Barra - Canal
canal_df = dados["Canal de Entrada"].value_counts().reset_index()
canal_df.columns = ["Canal", "Quantidade"]
fig_barra3 = px.bar(canal_df, x="Canal", y="Quantidade", title="3 Barra: Canais de Entrada")
fig_barra3.show()

# 4. Barra - Pedidos por Mês
mes_df = dados["mes"].value_counts().reset_index()
mes_df.columns = ["Mes", "Quantidade"]
mes_df = mes_df.sort_values("Mes")
fig_barra4 = px.bar(mes_df, x="Mes", y="Quantidade", title="4 Barra: Pedidos por Mês", text="Quantidade")
fig_barra4.update_traces(textposition="outside")
fig_barra4.show()

# ==========================================================
# GRÁFICOS DE DISPERSÃO / ESPALHAMENTO
# ==========================================================

# 1. Dispersão: Mês vs Tempo de Resposta 
fig_disp1 = px.strip(
    dados, x="mes", y="tempo_resposta", color="Tipo",
    stripmode="overlay",
    title="Dispersão 1: Mês de Abertura vs Tempo de Resposta",
    labels={"mes": "Mês", "tempo_resposta": "Dias para Resposta"}
)
fig_disp1.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
fig_disp1.show()

# 2. Dispersão: Tipo de Manifestação vs Tempo de Resposta
fig_disp2 = px.strip(
    dados, x="Tipo", y="tempo_resposta", 
    color="Tipo", stripmode="overlay",
    title="Dispersão 2: Categorias vs Tempo de Resposta"
)
fig_disp2.show()

# 3. Dispersão: Canal de Entrada vs Tempo de Resposta
fig_disp3 = px.strip(
    dados, x="Canal de Entrada", y="tempo_resposta", color="Canal de Entrada",
    stripmode="overlay", title="Dispersão 3: Canal de Entrada vs Eficiência"
)
fig_disp3.show()

# 4. Dispersão: Top 10 Assuntos vs Tempo de Resposta
top_10_assuntos = dados["Assunto"].value_counts().head(10).index
df_top = dados[dados["Assunto"].isin(top_10_assuntos)]

fig_disp4 = px.strip(
    df_top, x="Assunto", y="tempo_resposta", color="Assunto",
    stripmode="overlay",
    title="Dispersão 4: Top 10 Assuntos vs Tempo de Resposta"
)
fig_disp4.show()

# ==========================================================
# GRÁFICO DE PIZZA ISOLADO 
# ==========================================================
fig_pizza_tipo = px.pie(
    dados,
    names="Tipo",
    title="Pizza 1 - Proporção dos Tipos"
)
fig_pizza_tipo.show()

# =========================
# TELA FINAL COMPLETA DE GRÁFICO DE PIZZA (DASHBOARD)
# =========================

total_bruto = len(pd.read_csv("ouvidoriasic.csv", sep=";", encoding="latin1", engine="python", on_bad_lines="skip"))
total_validos = len(dados)
total_descartados = total_bruto - total_validos

tipo_dash_df = dados["Tipo"].value_counts().reset_index()
tipo_dash_df.columns = ["Categoria", "Quantidade"]

canal_dash_df = dados["Canal de Entrada"].value_counts().reset_index()
canal_dash_df.columns = ["Categoria", "Quantidade"]

assunto_dash_df = dados["Assunto"].value_counts().head(5).reset_index()
assunto_dash_df.columns = ["Categoria", "Quantidade"]

fig_dash = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "domain"}, {"type": "domain"}],
           [{"type": "domain"}, {"type": "domain"}]],
    subplot_titles=(
        "Qualidade dos Registros", "Tipos de Manifestação",
        "Pizza: Canais de Entrada", "Top Assuntos"
    )
)

fig_dash.add_trace(go.Pie(labels=["Válidos", "Descartados"], values=[total_validos, total_descartados], textinfo="label+value", marker=dict(line=dict(width=0))), row=1, col=1)
fig_dash.add_trace(go.Pie(labels=tipo_dash_df["Categoria"], values=tipo_dash_df["Quantidade"], textinfo="percent+label", marker=dict(line=dict(width=0))), row=1, col=2)
fig_dash.add_trace(go.Pie(labels=canal_dash_df["Categoria"], values=canal_dash_df["Quantidade"], textinfo="percent+label", marker=dict(line=dict(width=0))), row=2, col=1)

fig_dash.add_trace(
    go.Pie(
        labels=assunto_dash_df["Categoria"], 
        values=assunto_dash_df["Quantidade"], 
        textinfo="percent+label",
        marker=dict(
            colors=["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"],
            line=dict(width=1, color="white")
        )
    ), 
    row=2, col=2
)

fig_dash.update_layout(
    title_text="Gráficos de Pizza (2-5) - ANÁLISE COMPLETA DA OUVIDORIA", 
    height=800, 
    showlegend=False,
    paper_bgcolor="white",
    plot_bgcolor="white"
)

fig_dash.show()