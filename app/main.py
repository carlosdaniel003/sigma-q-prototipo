# =========================
# SIGMA-Q DASHBOARD PRINCIPAL
# =========================
import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import sys, os

# Identificação da build atual
st.caption("🚀 Build SIGMA-Q 2025-11-07-Rev3")

# Garante que o diretório raiz do projeto (pai de /app) esteja no sys.path
# Isso permite importar os módulos de /utils/ corretamente no Streamlit Cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importações internas do SIGMA-Q
from utils.atualizador import carregar_base, monitorar_base
from utils.logger import registrar_classificacoes
from utils.model_manager import carregar_modelos, verificar_modelos


# Adiciona a pasta raiz ao caminho do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.atualizador import carregar_base, monitorar_base
from utils.logger import registrar_classificacoes
from utils.auto_updater import verificar_atualizacao



# Verifica alterações na base oficial do Quality Control
if os.path.exists("data/quality_control_outubro.xlsx"):
    ultima_modificacao = os.path.getmtime("data/quality_control_outubro.xlsx")
    atualizado, ultima_modificacao = verificar_atualizacao("data/quality_control_outubro.xlsx", ultima_modificacao)

else:
    ultima_modificacao = None
    atualizado = False


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

# Verifica a base oficial
base_ok = os.path.exists("data/quality_control_outubro.xlsx")

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
    data_mod = pd.Timestamp(os.path.getmtime("data/quality_control_outubro.xlsx"), unit="s")
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
if os.path.exists("data/quality_control_outubro.xlsx"):
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
# LEITURA LOCAL DO EXCEL (USANDO A BASE OFICIAL, OCULTA)
# =========================
st.header("📂 Status da Base de Dados (oculta)")

with st.spinner("📥 Carregando base oficial (oculta)..."):
    # Carrega apenas colunas necessárias para análises e IA — evita expor dados brutos
    # ajuste usecols conforme seu espaço / necessidade
    usecols = None  # Ex: ["DATA","MÊS","DESCRIÇÃO_DA_FALHA","MODELO","CATEGORIA","REFERENCIA","MOTIVO"]
  # =========================
# CARREGAMENTO DA BASE DE DADOS (com debug)
# =========================
try:
    df = carregar_base(path=None, usecols=usecols)
except Exception as e:
    import traceback
    st.error("❌ Erro ao carregar base:")
    st.code(traceback.format_exc())
    st.stop()

    # =========================
# TREINAMENTO AUTOMÁTICO DO MODELO (se não existir)
# =========================
from utils.model_manager import verificar_modelos
from utils.model_trainer import treinar_modelo

if not verificar_modelos():
    st.info("🧠 Nenhum modelo encontrado — iniciando treinamento automático...")
    modelo, vetorizador = treinar_modelo()
    if modelo:
        st.success("✅ Treinamento automático concluído com sucesso!")


# NÃO exibir df completo no front-end!
st.info("🔒 Base oficial carregada internamente. Dados linha-a-linha não são exibidos por política de privacidade.")

# Apenas mostrar uma amostra reduzida (por exemplo, 5 linhas) para debug — opcional e pode ficar desativada.
if st.checkbox("Mostrar amostra segura (5 linhas) - uso interno", value=False):
    st.dataframe(df.head(5), use_container_width=True)

# Mostrar somentes agregados/contagens úteis para o usuário
st.subheader("🔎 Visão resumida (agregados)")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Registros (Base oficial)", len(df))
col2.metric("Categorias distintas", df["CATEGORIA"].nunique() if "CATEGORIA" in df.columns else "N/A")
col3.metric("Motivos distintos", df["MOTIVO"].nunique() if "MOTIVO" in df.columns else "N/A")

# Verificação automática (em segundo plano)
atualizado, _ = monitorar_base(intervalo=15)
if atualizado:
    st.rerun()

from utils.text_processor import preprocessar_dataframe

# Garantir nome de coluna correto (tolerância a variações)
col_ops = [
    "DESCRICAO_DA_FALHA", 
    "DESCRIÇÃO_DA_FALHA",
    "DESCRICAO",
    "DESCRICAO_DA_FALHA",
    "DESC_FALHA",      # ← versão sem ponto
    "DESC._FALHA",     # ← versão com ponto (como na sua planilha)
]

for c in col_ops:
    if c in df.columns:
        col_text = c
        break

if col_text:
    df = preprocessar_dataframe(df, coluna_texto=col_text)
    if st.checkbox("Mostrar preview de textos processados", value=False):
        st.dataframe(df[[col_text, "TEXTO_PROCESSADO"]].head(5))
else:
    st.warning("⚠️ Coluna de texto para pré-processamento não encontrada.")


# =========================
# 🤖 CLASSIFICAÇÃO AUTOMÁTICA
# =========================
st.header("🤖 Classificação Automática")

from utils.model_manager import carregar_modelos, verificar_modelos

# Verifica se os modelos estão disponíveis
if not verificar_modelos():
    st.warning("⚠️ Nenhum modelo de IA encontrado. Treine o modelo antes de continuar.")
    st.stop()

# Carrega modelo e vetorizador
modelo, vetorizador = carregar_modelos()

# Normaliza os nomes das colunas
df.columns = (
    df.columns.str.strip()
              .str.upper()
              .str.replace("Ç", "C")
              .str.replace("Ã", "A")
              .str.replace("Õ", "O")
              .str.replace(" ", "_")
)

# Verifica se existe uma coluna de descrição de falha
col_text = None
for c in ["DESCRICAO_DA_FALHA", "DESC_FALHA", "DESC._FALHA", "DESCRICAO"]:
    if c in df.columns:
        col_text = c
        break

if not col_text:
    st.warning("⚠️ Nenhuma coluna de texto encontrada para classificação automática.")
    st.stop()

# =========================
# EXECUTA A CLASSIFICAÇÃO
# =========================
descricoes = df[col_text].astype(str)

with st.spinner("🧠 Classificando falhas..."):
    try:
        # Se o modelo for um Pipeline (TF-IDF + Classificador), ele já faz o transform internamente
        predicoes = modelo.predict(descricoes)
    except Exception:
        # Caso o modelo seja apenas o classificador e precise do vetor separadamente
        X_tfidf = vetorizador.transform(descricoes)
        predicoes = modelo.predict(X_tfidf)

    # Atribui as previsões ao DataFrame
    df["CATEGORIA_PREDITA"] = predicoes

# Exibe resultados
st.success("✅ Classificação concluída com sucesso!")
st.subheader("Top categorias previstas")
st.table(df["CATEGORIA_PREDITA"].value_counts().head(10))


# Exemplo seguro (até 3 registros por categoria)
st.subheader("Exemplos (segurança) — até 3 por categoria")
sample_preview = df.groupby("CATEGORIA_PREDITA").head(3)[[col_text, "CATEGORIA_PREDITA"]]
st.table(sample_preview)

# =========================
# REGISTRO AUTOMÁTICO DE CLASSIFICAÇÕES
# =========================
from utils.logger import registrar_classificacoes

try:
    # Detecta automaticamente a coluna correta de falha
    col_falha = None
    for c in ["DESCRICAO_DA_FALHA", "DESC_FALHA", "DESC._FALHA", "DESC. FALHA", "DESCRICAO"]:
        if c in df.columns:
            col_falha = c
            break

    if col_falha:
        # Salva apenas as colunas necessárias
        registrar_classificacoes(df[[col_falha, "CATEGORIA_PREDITA"]])
        st.toast("📘 Log de classificações atualizado com sucesso.")
    else:
        st.warning("⚠️ Nenhuma coluna de descrição de falha encontrada para registrar log.")

except Exception as e:
    st.warning(f"⚠️ Falha ao atualizar log: {e}")

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

except Exception as e:
    st.error(f"❌ Erro ao gerar visualizações: {e}")

# =========================
# 🕒 HISTÓRICO DE CLASSIFICAÇÕES (versão aprimorada)
# =========================
import altair as alt
from datetime import datetime, timedelta


log_path = os.path.join("data", "logs", "log_classificacoes.xlsx")

if os.path.exists(log_path):
    st.subheader("🕒 Histórico de Classificações")

    try:
        log_df = pd.read_excel(log_path)

        # Verifica e converte coluna de data
        if "DATA_LOG" not in log_df.columns:
            st.warning("⚠️ A coluna 'DATA_LOG' não foi encontrada no log.")
        else:
            log_df["DATA_LOG"] = pd.to_datetime(log_df["DATA_LOG"], errors="coerce")
            log_df = log_df.dropna(subset=["DATA_LOG"])
            log_df["DIA"] = log_df["DATA_LOG"].dt.date

            # Agrupa registros por dia
            historico = log_df.groupby("DIA").size().reset_index(name="TOTAL")

            # Calcula média móvel de 7 dias (se houver dados suficientes)
            if len(historico) >= 7:
                historico["MEDIA_MOVEL"] = (
                    historico["TOTAL"].rolling(window=7, min_periods=1).mean()
                )
            else:
                historico["MEDIA_MOVEL"] = historico["TOTAL"]

            # Define cores dinâmicas conforme volume
            color_scale = alt.Scale(
                domain=[historico["TOTAL"].min(), historico["TOTAL"].max()],
                scheme="blues"
            )

            # Cria gráfico com Altair
            chart = (
                alt.Chart(historico)
                .mark_bar(size=20)
                .encode(
                    x=alt.X("DIA:T", title="Data", axis=alt.Axis(format="%d/%m")),
                    y=alt.Y("TOTAL:Q", title="Classificações"),
                    color=alt.Color("TOTAL:Q", scale=color_scale, legend=None),
                    tooltip=[
                        alt.Tooltip("DIA:T", title="Data", format="%d/%m/%Y"),
                        alt.Tooltip("TOTAL:Q", title="Total de Registros"),
                        alt.Tooltip("MEDIA_MOVEL:Q", title="Média móvel (7 dias)", format=".1f")
                    ],
                )
            )

            # Linha da média móvel
            line = (
                alt.Chart(historico)
                .mark_line(color="orange", strokeWidth=2)
                .encode(x="DIA:T", y="MEDIA_MOVEL:Q")
            )

            # Combina gráfico de barras + linha
            final_chart = (chart + line).properties(
                width="container",
                height=300,
                title="Tendência de Classificações Diárias (com média móvel de 7 dias)",
            )

            st.altair_chart(final_chart, use_container_width=True)

            # KPIs do histórico
            st.markdown("### 📊 Indicadores Gerais")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Registros", len(log_df))
            col2.metric("Categorias Distintas", log_df["CATEGORIA_PREDITA"].nunique())
            col3.metric(
                "Última Atualização",
                log_df["DATA_LOG"].max().strftime("%d/%m/%Y %H:%M"),
            )

    except Exception as e:
        st.error(f"❌ Erro ao carregar histórico: {e}")

else:
    st.info("ℹ️ Nenhum histórico de classificações encontrado ainda.")



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

# Detecta coluna equivalente ao modelo
col_modelo = None
for c in ["MODELO", "DESCRICAO", "DESCRIÇÃO", "CODIGO", "CÓDIGO", "CÓD_PRODUTO"]:
    if c in df.columns:
        col_modelo = c
        break

if col_modelo:
    st.bar_chart(df.groupby(col_modelo)["CATEGORIA_PREDITA"].count())
    st.write("Top 5 modelos com mais ocorrências:")
    st.table(df[col_modelo].value_counts().head(5))
else:
    st.warning("⚠️ Nenhuma coluna de modelo ou descrição encontrada na base.")


# --- 🔍 Análises Detalhadas ---
with tab3:
    st.subheader("Top 5 defeitos mais recorrentes")
    top_defeitos = df["CATEGORIA_PREDITA"].value_counts().head(5)
    st.table(top_defeitos)

    # =========================
# ANÁLISES DETALHADAS — EVOLUÇÃO TEMPORAL
# =========================
st.subheader("📅 Evolução Temporal de Ocorrências")

# Detecta coluna de data (independente de nome ou formato)
col_data = None
for c in df.columns:
    nome = str(c).strip().upper()
    if nome in ["DATA", "DT", "DATA_REGISTRO", "DATA_LOG"]:
        col_data = c
        break

if col_data:
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df["DIA"] = df[col_data].dt.date

    # Gera gráfico temporal
    grafico = df.groupby("DIA")["CATEGORIA_PREDITA"].count().reset_index(name="TOTAL")

    if not grafico.empty:
        st.line_chart(grafico.set_index("DIA"), use_container_width=True)
    else:
        st.info("ℹ️ Nenhum registro temporal disponível para plotar.")
else:
    st.info("ℹ️ Nenhuma coluna de data encontrada na base para gerar gráfico temporal.")
