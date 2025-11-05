import streamlit as st
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# =========================
# CONFIGURAÇÃO INICIAL
# =========================
st.set_page_config(page_title="SIGMA-Q - Dashboard de Defeitos", layout="wide")

st.title("📊 SIGMA-Q - Dashboard de Defeitos na Linha de Montagem")
st.markdown("Monitoramento inteligente e classificação automática de defeitos")

# =========================
# LEITURA LOCAL DO EXCEL
# =========================
st.header("📂 Leitura da Base de Dados Local")

base_padrao = os.path.join("data", "base_de_dados.xlsx")
st.write(f"📁 Procurando arquivo em: `{base_padrao}`")

if os.path.exists(base_padrao):
    try:
        st.write("🚀 Iniciando leitura da base...")
        df = pd.read_excel(base_padrao, engine="openpyxl")
        st.success(f"✅ Dados carregados de: {base_padrao}")
        st.info(f"📊 Total de linhas: {len(df)}")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo Excel: {e}")
        st.stop()
else:
    st.error("❌ Arquivo `base_de_dados.xlsx` não encontrado em `/data`.")
    st.stop()

# =========================
# CLASSIFICAÇÃO AUTOMÁTICA
# =========================
st.header("🤖 Classificação Automática")

modelo_path = "model/modelo_classificacao.pkl"
vetorizador_path = "model/vectorizer.pkl"

if os.path.exists(modelo_path) and os.path.exists(vetorizador_path):
    modelo = joblib.load(modelo_path)
    vetorizador = joblib.load(vetorizador_path)
    st.sidebar.success("✅ Modelo carregado com sucesso!")
else:
    st.sidebar.error("❌ Modelo não encontrado! Execute o treino primeiro.")
    st.stop()

if "DESCRIÇÃO DA FALHA" in df.columns:
    descricoes = df["DESCRIÇÃO DA FALHA"].astype(str)
    X_tfidf = vetorizador.transform(descricoes)
    predicoes = modelo.predict(X_tfidf)
    df["CATEGORIA_PREDITA"] = predicoes
    st.success("✅ Classificação concluída!")
    st.dataframe(df[["DESCRIÇÃO DA FALHA", "CATEGORIA_PREDITA"]], use_container_width=True)
else:
    st.warning("⚠️ A coluna 'DESCRIÇÃO DA FALHA' não foi encontrada no arquivo.")


# =========================
# CLASSIFICAÇÃO AUTOMÁTICA
# =========================
st.header("🤖 Classificação Automática")

if "DESCRIÇÃO DA FALHA" in df.columns:
    descricoes = df["DESCRIÇÃO DA FALHA"].astype(str)
    X_tfidf = vetorizador.transform(descricoes)
    predicoes = modelo.predict(X_tfidf)
    df["CATEGORIA_PREDITA"] = predicoes

    st.success("✅ Classificação concluída!")
    st.dataframe(df[["DESCRIÇÃO DA FALHA", "CATEGORIA_PREDITA"]], use_container_width=True)
else:
    st.error("A coluna 'DESCRIÇÃO DA FALHA' não foi encontrada no arquivo.")

# =========================
# ANÁLISE E VISUALIZAÇÃO
# =========================
st.header("📈 Estatísticas e Gráficos")

if "CATEGORIA_PREDITA" in df.columns:
    contagem = df["CATEGORIA_PREDITA"].value_counts()
    st.bar_chart(contagem)

    modelo_counts = df["MODELO"].value_counts()
    st.subheader("📦 Quantidade de defeitos por modelo")
    st.bar_chart(modelo_counts)

# =========================
# EXPORTAR RESULTADOS
# =========================
st.header("💾 Exportar Resultados")

if st.button("Salvar base classificada"):
    saida = "data/base_classificada.xlsx"
    df.to_excel(saida, index=False)
    st.success(f"Base salva em: `{saida}`")
