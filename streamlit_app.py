import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Painel de Taxa de Entrega", layout="wide")

st.title("📊 Painel de Taxa de Entrega")

# 🔹 Link direto do Google Sheets para baixar como .xlsx
google_sheets_url = "https://docs.google.com/spreadsheets/d/1pik6-AIg3g6fzR0vLrHDPUzV7IOruDtP/export?format=xlsx"

@st.cache_data
def carregar_dados(uploaded_file=None):
    try:
        if uploaded_file is not None:
            # Se o usuário fizer upload manual
            return pd.read_excel(uploaded_file, dtype={"Pedido": str})
        else:
            # Caso contrário, baixa direto do Google Sheets
            res = requests.get(google_sheets_url)
            res.raise_for_status()
            return pd.read_excel(io.BytesIO(res.content), dtype={"Pedido": str})
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return None

# Carrega automaticamente do Google Sheets
df = carregar_dados()

if df is not None:
    st.success("✅ Dados carregados com sucesso do Google Sheets!")
    st.dataframe(df.head(), use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado disponível. Carregue uma planilha manualmente.")
    uploaded_file = st.file_uploader("📂 Carregar planilha manualmente", type=["xlsx", "csv"])
    if uploaded_file:
        df = carregar_dados(uploaded_file)
        if df is not None:
            st.success("✅ Dados carregados com sucesso do arquivo enviado!")
            st.dataframe(df.head(), use_container_width=True)
