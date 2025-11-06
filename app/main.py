import streamlit as st
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import os

import sys
import os

import matplotlib.pyplot as plt  # (adicione no topo do arquivo, se ainda não tiver)


# Adiciona a pasta raiz ao caminho do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.atualizador import carregar_base, monitorar_base
from utils.logger import registrar_classificacoes
from utils.auto_updater import verificar_atualizacao



ultima_modificacao = os.path.getmtime("data/base_de_dados.xlsx")
atualizado, ultima_modificacao = verificar_atualizacao("data/base_de_dados.xlsx", ultima_modificacao)

if atualizado:
    df = carregar_base()
    st.experimental_rerun()


# =========================
# CONFIGURAÇÃO INICIAL
# =========================
st.set_page_config(page_title="SIGMA-Q - Dashboard de Defeitos", layout="wide")

# Barra lateral fixa
# =========================
# PAINEL LATERAL INTELIGENTE SIGMA-Q
# =========================
st.sidebar.title("⚙️ Painel SIGMA-Q")
st.sidebar.markdown("Gerenciamento e status do sistema SIGMA-Q")

# --- STATUS DO SISTEMA ---
st.sidebar.header("📊 Status do Sistema")

# Verifica a base
base_ok = os.path.exists("data/base_de_dados.xlsx")
modelo_ok = os.path.exists("model/modelo_classificacao.pkl")
vet_ok = os.path.exists("model/vectorizer.pkl")
log_ok = os.path.exists("data/logs/log_classificacoes.xlsx")

# Indicadores de status
if base_ok:
    st.sidebar.success("✅ Base de dados carregada")
else:
    st.sidebar.error("❌ Base de dados não encontrada")

if modelo_ok and vet_ok:
    st.sidebar.success("💾 Modelos prontos para uso")
else:
    st.sidebar.warning("⚠️ Modelos ausentes – treine novamente")

if modelo_ok and vet_ok:
    st.sidebar.info("🧠 Modelos carregados")
else:
    st.sidebar.warning("📦 Aguardando treinamento...")

# --- MÉTRICAS RÁPIDAS ---
st.sidebar.header("📈 Indicadores")

# Última atualização
if base_ok:
    data_mod = pd.Timestamp(os.path.getmtime("data/base_de_dados.xlsx"), unit="s")
    st.sidebar.metric("Última atualização da base", data_mod.strftime("%d/%m/%Y %H:%M"))

# Histórico de acurácia
if log_ok:
    try:
        df_log = pd.read_excel("data/logs/log_classificacoes.xlsx")
        total_registros = len(df_log)
        st.sidebar.metric("Classificações registradas", total_registros)
    except:
        st.sidebar.metric("Classificações registradas", "N/A")

# --- AÇÕES RÁPIDAS ---
st.sidebar.header("⚡ Ações Rápidas")

if st.sidebar.button("🔁 Atualizar Base de Dados"):
    st.toast("📂 Base recarregada manualmente.")
    st.rerun()

if st.sidebar.button("💾 Exportar Log de Classificações"):
    if log_ok:
        from datetime import datetime
        destino = f"data/logs/export_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        import shutil
        shutil.copy("data/logs/log_classificacoes.xlsx", destino)
        st.sidebar.success(f"📤 Log exportado como {destino}")
    else:
        st.sidebar.warning("⚠️ Nenhum log disponível para exportar.")

if st.sidebar.button("🧹 Limpar Histórico de Logs"):
    if log_ok:
        import os
        os.remove("data/logs/log_classificacoes.xlsx")
        st.sidebar.success("🧾 Histórico de logs limpo.")
        st.rerun()
    else:
        st.sidebar.info("ℹ️ Nenhum log para limpar.")

# --- TREINAMENTO DIRETO ---
st.sidebar.header("🧠 Treinamento do Modelo")

if st.sidebar.button("Treinar Modelo de IA"):
    from utils.model_trainer import treinar_modelo
    modelo, vetorizador = treinar_modelo()
    if modelo:
        st.sidebar.success("✅ Modelo treinado com sucesso!")
        st.rerun()

st.sidebar.divider()
st.sidebar.subheader("📡 Status do Sistema")

# Status da base
if os.path.exists("data/base_de_dados.xlsx"):
    st.sidebar.success("📘 Base de dados carregada")
else:
    st.sidebar.warning("⚠️ Base ausente")

# Status dos modelos
from utils.model_manager import verificar_modelos
if verificar_modelos():
    st.sidebar.success("🧠 Modelos carregados")
else:
    st.sidebar.warning("❌ Modelos não encontrados")

st.sidebar.divider()


st.title("📊 SIGMA-Q - Dashboard de Defeitos na Linha de Montagem")
st.markdown("Monitoramento inteligente e classificação automática de defeitos")

# =========================
# LEITURA LOCAL DO EXCEL (com atualização automática)
# =========================
st.header("📂 Leitura da Base de Dados Local")

with st.spinner("📥 Carregando base de dados..."):
    df = carregar_base()


st.dataframe(df, use_container_width=True)

# Botão de atualização manual
if st.button("🔁 Atualizar Base de Dados"):
    with st.spinner("🔄 Atualando dados..."):
        df = carregar_base()

    st.dataframe(df, use_container_width=True)
    st.toast("✅ Base recarregada manualmente!")

# Verificação automática (em segundo plano)
if monitorar_base(intervalo=15):
    st.rerun()

from utils.text_processor import preprocessar_dataframe

# Pré-processa as descrições antes de classificar
df = preprocessar_dataframe(df, coluna_texto="DESCRIÇÃO DA FALHA")
st.write("🧹 Textos pré-processados (coluna 'TEXTO_PROCESSADO'):")
st.dataframe(df[["DESCRIÇÃO DA FALHA", "TEXTO_PROCESSADO"]])


# =========================
# CLASSIFICAÇÃO AUTOMÁTICA
# =========================
st.header("🤖 Classificação Automática")

from utils.model_manager import carregar_modelos, verificar_modelos

# Normaliza as colunas para evitar erros de acentuação
df.columns = (
    df.columns.str.strip()
              .str.upper()
              .str.replace("Ç", "C")
              .str.replace("Ã", "A")
              .str.replace("Õ", "O")
              .str.replace(" ", "_")
)

# =========================
# TREINAMENTO DIRETO PELO PAINEL
# =========================
st.sidebar.header("🧠 Treinamento do Modelo")

if st.sidebar.button("Treinar Modelo de IA", key="btn_treinar_sidebar"):

    from utils.model_trainer import treinar_modelo
    modelo, vetorizador = treinar_modelo()
    if modelo:
        st.sidebar.success("✅ Modelo treinado com sucesso!")
        st.rerun()

# Verifica se o modelo existe e carrega
if verificar_modelos():
    modelo, vetorizador = carregar_modelos()
else:
    st.stop()

# Executa a classificação se a coluna existir
if "DESCRICAO_DA_FALHA" in df.columns:
    descricoes = df["DESCRICAO_DA_FALHA"].astype(str)

    with st.spinner("🧠 Classificando falhas..."):
        X_tfidf = vetorizador.transform(descricoes)
        predicoes = modelo.predict(X_tfidf)
        df["CATEGORIA_PREDITA"] = predicoes

    st.success("✅ Classificação concluída com sucesso!")
    st.dataframe(df[["DESCRICAO_DA_FALHA", "CATEGORIA_PREDITA"]], use_container_width=True)

    # Registrar automaticamente no log
    try:
        registrar_classificacoes(df[["DESCRICAO_DA_FALHA", "CATEGORIA_PREDITA"]])
        st.toast("📘 Log de classificações atualizado com sucesso.")
    except Exception as e:
        st.warning(f"⚠️ Falha ao atualizar log: {e}")

else:
    st.warning("⚠️ Coluna 'DESCRIÇÃO DA FALHA' (ou equivalente) não encontrada na base de dados.")

# =========================
# ANÁLISE E VISUALIZAÇÃO
# =========================
st.header("📈 Análise e Visualização de Desempenho")

try:
    # Se o DataFrame atual tiver classificação
    if "CATEGORIA_PREDITA" in df.columns:
        st.subheader("📊 Distribuição de Defeitos por Categoria Predita")
        contagem = df["CATEGORIA_PREDITA"].value_counts()
        st.bar_chart(contagem)

        # Gráfico por modelo
        if "MODELO" in df.columns:
            st.subheader("🏭 Quantidade de Defeitos por Modelo")
            modelo_counts = df["MODELO"].value_counts()
            st.bar_chart(modelo_counts)

        # KPIs
        st.subheader("📌 Indicadores Gerais")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Registros", len(df))
        col2.metric("Categorias Distintas", df["CATEGORIA_PREDITA"].nunique())
        col3.metric("Última Atualização", pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"))

    # --------------------------
    # Histórico (logs de classificação)
    # --------------------------
    log_path = "data/logs/log_classificacoes.xlsx"
    if os.path.exists(log_path):
        st.subheader("🕒 Histórico de Classificações")
        log_df = pd.read_excel(log_path)

        # Gráfico temporal
        if "DATA_LOG" in log_df.columns:
            log_df["DATA_LOG"] = pd.to_datetime(log_df["DATA_LOG"], errors="coerce")
            log_df = log_df.dropna(subset=["DATA_LOG"])
            log_df["DIA"] = log_df["DATA_LOG"].dt.date

            # Contagem diária
            historico = log_df.groupby("DIA").size()
            st.line_chart(historico, use_container_width=True)
        else:
            st.warning("⚠️ O arquivo de log não possui a coluna DAT LOG.")
    else:
        st.info("ℹ️ Nenhum histórico de classificações encontrado ainda.")

except Exception as e:
    st.error(f"❌ Erro ao gerar visualizações: {e}")


# =========================
# EXPORTAR RESULTADOS
# =========================
st.header("💾 Exportar Resultados")

if st.button("Salvar base classificada"):
    saida = "data/base_classificada.xlsx"
    df.to_excel(saida, index=False)
    st.success(f"📁 Base salva em: `{saida}`")

   # =========================
# RELATÓRIOS TÉCNICOS (ETAPA 7.1)
# =========================
st.header("📊 Relatórios Técnicos de Produção")

if "CATEGORIA_PREDITA" in df.columns:
    tab1, tab2, tab3 = st.tabs(["📈 Visão Geral", "📦 Por Modelo", "🔍 Análises Detalhadas"])
# --- 📈 Visão Geral ---
with tab1:
    st.subheader("📊 Distribuição de Ocorrências por Categoria e Modelo")

    # Cria layout em colunas
    col1, col2 = st.columns([2, 1])

    # ----- COLUNA 1 → GRÁFICO DE BARRAS -----
    with col1:
        st.markdown("### 📦 Quantidade de Ocorrências por Categoria")
        st.bar_chart(df["CATEGORIA_PREDITA"].value_counts())

    # ----- COLUNA 2 → GRÁFICO DE PIZZA -----
    with col2:
        st.markdown("### 🥧 Proporção de Ocorrências")
        cat_counts = df["CATEGORIA_PREDITA"].value_counts()

        import matplotlib.pyplot as plt
        colors = plt.cm.tab20.colors
        explode = [0.05 if i == 0 else 0.02 for i in range(len(cat_counts))]

        fig, ax = plt.subplots(figsize=(4, 4), facecolor="#0e1117")
        wedges, texts, autotexts = ax.pie(
            cat_counts,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            pctdistance=0.8,
            explode=explode,
            wedgeprops={"edgecolor": "white", "linewidth": 1, "antialiased": True},
            textprops={"fontsize": 9, "color": "white", "weight": "bold"}
        )

        ax.set_title("Proporção de Ocorrências por Categoria", fontsize=11, color="white", pad=12)
        ax.legend(cat_counts.index, title="Categorias", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_aspect("equal")
        st.pyplot(fig)

# --- 📦 Por Modelo ---
with tab2:
    st.subheader("Distribuição de Defeitos por Modelo")
    if "MODELO" in df.columns:
        st.bar_chart(df.groupby("MODELO")["CATEGORIA_PREDITA"].count())
        st.write("Top 5 modelos com mais ocorrências:")
        st.table(df["MODELO"].value_counts().head(5))
    else:
        st.warning("⚠️ Coluna 'MODELO' não encontrada na base.")

# --- 🔍 Análises Detalhadas ---
with tab3:
    st.subheader("Top 5 defeitos mais recorrentes")
    top_defeitos = df["CATEGORIA_PREDITA"].value_counts().head(5)
    st.table(top_defeitos)

    if "data" in df.columns:
        st.subheader("📅 Evolução Temporal de Ocorrências")
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        st.line_chart(df.groupby("data")["CATEGORIA_PREDITA"].count())
    else:
        st.info("ℹ️ Nenhuma coluna de data encontrada para gerar gráfico temporal.")
