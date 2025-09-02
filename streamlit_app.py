import streamlit as st
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt

st.set_page_config(page_title="Painel de Taxa de Entrega", layout="wide")

st.title("📊 Painel de Taxa de Entrega")

# -------------------------------
# 🔗 Link direto para o Google Sheets em formato Excel
google_drive_url = "https://docs.google.com/spreadsheets/d/1pik6-AIg3g6fzR0vLrHDPUzV7IOruDtP/export?format=xlsx"

# -------------------------------
# Função para carregar os dados
@st.cache_data
def carregar_dados(uploaded_file=None):
    try:
        if uploaded_file is not None:
            return pd.read_excel(uploaded_file, dtype={"Pedido": str})
        else:
            res = requests.get(google_drive_url)
            if res.status_code == 200:
                return pd.read_excel(io.BytesIO(res.content), dtype={"Pedido": str})
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
    return None

# -------------------------------
# Carregar dados
df = carregar_dados()

if df is not None and not df.empty:
    st.success("✅ Dados carregados com sucesso do Google Drive!")

    # ---------------- Normalização de Recebimento ----------------
    def classificar_recebimento(valor):
        if pd.isna(valor) or str(valor).strip().lower() == "não entregue":
            return "NÃO ENTREGUE"
        elif "assinatura normal" in str(valor).lower():
            return "ENTREGUE"
        elif "na base" in str(valor).lower():
            return "NA BASE"
        else:
            return "NÃO ENTREGUE"

    df["StatusEntrega"] = df["Recebimento"].apply(classificar_recebimento)

    # ---------------- Filtro por Base ----------------
    st.sidebar.header("Filtros")
    bases = st.sidebar.multiselect("Selecione a Base de Entrega:", df["Base de entrega"].unique())
    
    if bases:
        df = df[df["Base de entrega"].isin(bases)]

    # ---------------- Botão para baixar Excel ----------------
    st.sidebar.subheader("📥 Exportar")
    excel_bytes = io.BytesIO()
    df.to_excel(excel_bytes, index=False, engine="openpyxl")
    excel_bytes.seek(0)

    st.sidebar.download_button(
        label="⬇️ Baixar planilha filtrada (Excel)",
        data=excel_bytes,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ---------------- KPIs ----------------
    col1, col2, col3, col4 = st.columns(4)
    total_pedidos = len(df)
    entregues = (df["StatusEntrega"] == "ENTREGUE").sum()
    nao_entregues = (df["StatusEntrega"] == "NÃO ENTREGUE").sum()
    na_base = (df["StatusEntrega"] == "NA BASE").sum()
    taxa_entrega = (entregues / total_pedidos * 100) if total_pedidos > 0 else 0

    col1.metric("📦 Total de Pedidos", total_pedidos)
    col2.metric("✅ Entregues", entregues)
    col3.metric("❌ Não Entregues", nao_entregues)
    col4.metric("📊 Na Base", na_base)

    # ---------------- Taxa por Base ----------------
    st.subheader("🏢 Taxa de Entrega por Base de Entrega")

    df_base = (
        df.groupby("Base de entrega")
        .agg(
            **{
                "NÃO ENTREGUE": ("StatusEntrega", lambda x: (x == "NÃO ENTREGUE").sum()),
                "ENTREGUE": ("StatusEntrega", lambda x: (x == "ENTREGUE").sum()),
                "NA BASE": ("StatusEntrega", lambda x: (x == "NA BASE").sum()),
                "TOTAL": ("Pedido", "count"),
            }
        )
        .reset_index()
    )

    df_base["TAXA %"] = (df_base["ENTREGUE"] / df_base["TOTAL"] * 100).round(2)

    def cor_taxa(val):
        if val >= 98:
            return "background-color: #00B050; color: white"
        elif val >= 95:
            return "background-color: #FFC000; color: black"
        else:
            return "background-color: #FF0000; color: white"

    # 👉 Deixar cabeçalhos em negrito
    st.dataframe(
        df_base.style
        .set_table_styles([{"selector": "th", "props": [("font-weight", "bold")]}])
        .format({"TAXA %": "{:.2f}%"}).applymap(cor_taxa, subset=["TAXA %"]),
        use_container_width=True
    )

    # ---------------- Pedidos na Base ----------------
    st.subheader("📍 Pedidos que estão NA BASE")

    df_na_base = df[df["StatusEntrega"] == "NA BASE"]

    if not df_na_base.empty:
        st.write(df_na_base[["Pedido", "Base de entrega", "Cidade Destino", "Entregador"]])

        # Gráfico
        fig, ax = plt.subplots(figsize=(8, 4))
        df_na_base["Base de entrega"].value_counts().plot(kind="bar", ax=ax, color="red")
        ax.set_title("Pedidos NA BASE por Base de Entrega", fontsize=14, fontweight="bold")
        ax.set_ylabel("Quantidade")
        st.pyplot(fig)

        # Botão para baixar gráfico em PNG
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button(
            label="⬇️ Baixar gráfico NA BASE (PNG)",
            data=buf.getvalue(),
            file_name="pedidos_na_base.png",
            mime="image/png"
        )

    else:
        st.info("✅ Nenhum pedido está na BASE.")

    # ---------------- Taxa por Entregador ----------------
    st.subheader("👷 Taxa de Entrega por Entregador")

    df_ent = (
        df.groupby("Entregador")
        .agg(
            **{
                "NÃO ENTREGUE": ("StatusEntrega", lambda x: (x == "NÃO ENTREGUE").sum()),
                "ENTREGUE": ("StatusEntrega", lambda x: (x == "ENTREGUE").sum()),
                "TOTAL": ("Pedido", "count"),
            }
        )
        .reset_index()
    )

    df_ent["TAXA %"] = (df_ent["ENTREGUE"] / df_ent["TOTAL"] * 100).round(2)

    st.dataframe(
        df_ent.style
        .set_table_styles([{"selector": "th", "props": [("font-weight", "bold")]}])
        .format({"TAXA %": "{:.2f}%"}).applymap(cor_taxa, subset=["TAXA %"]),
        use_container_width=True
    )

    # ---------------- Totais ----------------
    total_nao_entregue = df_ent["NÃO ENTREGUE"].sum()
    total_entregue = df_ent["ENTREGUE"].sum()
    total_geral = df_ent["TOTAL"].sum()
    taxa_geral = (total_entregue / total_geral * 100).round(2) if total_geral > 0 else 0

    st.markdown(f"""
    ### 📌 Total Geral
    - **Não entregue:** {total_nao_entregue}  
    - **Entregue:** {total_entregue}  
    - **Total:** {total_geral}  
    - **Taxa Geral:** {taxa_geral:.2f}%  
    """)
else:
    st.warning("⚠️ Nenhum dado disponível. Verifique o link do Google Drive ou carregue manualmente.")
