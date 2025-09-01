import streamlit as st
import pandas as pd

# --- Resumo por Entregador com Taxa ---
st.subheader("📊 Taxa de Entrega por Entregador")

df_taxa = (
    df_filtrado.groupby("Entregador")
    .agg(
        **{
            "NÃO ENTREGUE": ("Recebimento", lambda x: (x != "Sim").sum()),
            "ENTREGUE": ("Recebimento", lambda x: (x == "Sim").sum()),
            "TOTAL": ("Pedido", "count"),
        }
    )
    .reset_index()
)

# Calcular taxa
df_taxa["TAXA %"] = (df_taxa["ENTREGUE"] / df_taxa["TOTAL"] * 100).round(2)

# Função para colorir
def cor_taxa(val):
    if val >= 98:
        color = "background-color: #00B050; color: white"  # Verde
    elif val >= 95:
        color = "background-color: #FFC000; color: black"  # Amarelo
    else:
        color = "background-color: #FF0000; color: white"  # Vermelho
    return color

# Aplicar estilo
st.dataframe(
    df_taxa.style
    .format({"TAXA %": "{:.2f}%"})
    .applymap(cor_taxa, subset=["TAXA %"]),
    use_container_width=True
)

# Totais
total_nao_entregue = df_taxa["NÃO ENTREGUE"].sum()
total_entregue = df_taxa["ENTREGUE"].sum()
total_geral = df_taxa["TOTAL"].sum()
taxa_geral = (total_entregue / total_geral * 100).round(2) if total_geral > 0 else 0

st.markdown(f"""
### 📌 Total Geral
- **Não entregue:** {total_nao_entregue}  
- **Entregue:** {total_entregue}  
- **Total:** {total_geral}  
- **Taxa Geral:** {taxa_geral:.2f}%  
""")
