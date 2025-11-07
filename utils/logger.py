# utils/logger.py
import os
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# Caminho padrão do log
LOG_PATH = os.path.join("data", "logs", "log_classificacoes.xlsx")

# Tempo máximo de retenção (em dias)
RETENCAO_DIAS = 30


def registrar_classificacoes(df: pd.DataFrame):
    """
    Registra automaticamente as classificações realizadas pela IA SIGMA-Q.
    - Cria o log se não existir
    - Adiciona data/hora de cada classificação
    - Remove registros antigos automaticamente (> RETENCAO_DIAS)
    """

    # Verificação básica
    if df.shape[1] < 2:
        st.warning("⚠️ DataFrame inválido para registro de log (faltam colunas).")
        return

    # Detecta a coluna de descrição de falha
    col_falha = None
    for c in df.columns:
        nome = (
            str(c)
            .strip()
            .upper()
            .replace("Ç", "C")
            .replace("Ã", "A")
            .replace("Õ", "O")
        )
        if "DESC" in nome or "DESCRICAO" in nome:
            col_falha = c
            break

    if not col_falha:
        st.warning("⚠️ Nenhuma coluna de descrição de falha encontrada para registrar log.")
        return

    # Garante que o diretório exista
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    # Prepara DataFrame de log com timestamp
    df_log = df.copy()
    df_log["DATA_LOG"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Carrega log existente, se houver
    if os.path.exists(LOG_PATH):
        try:
            df_existente = pd.read_excel(LOG_PATH)
            df_concat = pd.concat([df_existente, df_log], ignore_index=True)
        except Exception:
            df_concat = df_log
    else:
        df_concat = df_log

    # Remove duplicados (descrição + categoria + data)
    df_concat.drop_duplicates(
        subset=[col_falha, "CATEGORIA_PREDITA", "DATA_LOG"],
        keep="last",
        inplace=True,
    )

    # --------------------------
    # 🧹 AUTO-LIMPEZA DO HISTÓRICO
    # --------------------------
    try:
        df_concat["DATA_LOG"] = pd.to_datetime(df_concat["DATA_LOG"], errors="coerce")
        limite = datetime.now() - timedelta(days=RETENCAO_DIAS)
        antes = len(df_concat)
        df_concat = df_concat[df_concat["DATA_LOG"] >= limite]
        removidos = antes - len(df_concat)

        if removidos > 0:
            st.info(f"🧹 {removidos} registros antigos removidos (>{RETENCAO_DIAS} dias).")

    except Exception as e:
        st.warning(f"⚠️ Falha ao limpar registros antigos: {e}")

    # Salva o log atualizado
    df_concat.to_excel(LOG_PATH, index=False)

    # Feedback visual
    st.toast("📘 Log de classificações atualizado com sucesso.")
    st.info(f"💾 {len(df_concat)} registros mantidos após limpeza automática.")
