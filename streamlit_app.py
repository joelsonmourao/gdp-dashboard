import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel de Taxa de Entrega", layout="wide")

st.title("📊 Painel de Taxa de Entrega")

# Upload manual
arquivo = st.file_uploader("Carregar planilha de dados", type=["xlsx", "csv"])

if arquivo is not None:
    if arquivo.name.endswith(".csv"):
        df = pd.read_csv(arquivo, dtype={"Pedido": str})
    else:
        df = pd.read_excel(arquivo, dtype={"Pedido": str})

    # ---------------- Filtros ----------------
    st.sidebar.header("Filtros")
    base = st.sidebar.multiselect("Selecione a Base de entrega:", df["Base de entrega"].unique())
    cidade = st.sidebar.multiselect("Selecione a Cidade Destino:", df["Cidade Destino"].unique())
    entregador = st.sidebar.multiselect("Selecione o Entregador:", df["Entregador"].dropna().unique())

    df_filtrado = df.copy()
    if base:
        df_filtrado = df_filtrado[df_filtrado["Base de entrega"].isin(base)]
    if cidade:
        df_filtrado = df_filtrado[df_filtrado["Cidade Destino"].isin(cidade)]
    if entregador:
        df_filtrado = df_filtrado[df_filtrado["Entregador"].isin(entregador)]

    # ---------------- KPIs ----------------
    col1, col2, col3, col4 = st.columns(4)
    total_pedidos = len(df_filtrado)
    entregues = df_filtrado["Recebimento"].eq("Sim").sum()  # se "Sim" = entregue
    problematicos = df_filtrado["Problemático"].notna().sum()
    taxa_entrega = (entregues / total_pedidos * 100) if total_pedidos > 0 else 0

    col1.metric("📦 Total de Pedidos", total_pedidos)
    col2.metric("✅ Entregues", entregues)
    col3.metric("⚠️ Problemáticos", problematicos)
    col4.metric("📈 Taxa de Entrega", f"{taxa_entrega:.2f}%")

    # ---------------- Tabela completa ----------------
    st.subheader("📍 Detalhes dos Pedidos")
    st.dataframe(df_filtrado, use_container_width=True)

    # ---------------- Resumo por Base ----------------
    st.subheader("📊 Taxa por Base de entrega")
    df_base = (
        df_filtrado.groupby("Base de entrega")
        .agg(
            Pedidos=("Pedido", "count"),
            Entregues=("Recebimento", lambda x: (x == "Sim").sum()),
            Problemáticos=("Problemático", "count"),
        )
    )
    df_base["Taxa de Entrega (%)"] = (df_base["Entregues"] / df_base["Pedidos"]) * 100
    st.dataframe(df_base, use_container_width=True)
    st.bar_chart(df_base["Taxa de Entrega (%)"])

    # ---------------- Resumo por Entregador ----------------
    st.subheader("👷 Taxa por Entregador")
    df_entregador = (
        df_filtrado.groupby("Entregador")
        .agg(
            Pedidos=("Pedido", "count"),
            Entregues=("Recebimento", lambda x: (x == "Sim").sum()),
            Problemáticos=("Problemático", "count"),
        )
    )
    df_entregador["Taxa de Entrega (%)"] = (df_entregador["Entregues"] / df_entregador["Pedidos"]) * 100
    st.dataframe(df_entregador, use_container_width=True)
    st.bar_chart(df_entregador["Taxa de Entrega (%)"])

else:
    st.info("📂 Carregue uma planilha para visualizar os dados")
