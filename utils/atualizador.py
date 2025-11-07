import os
import sys
import pandas as pd
import streamlit as st

# =========================
# Corrige o caminho de importação
# =========================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.text_normalizer import normalizar_dataframe

# =========================
# Caminhos base
# =========================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_PATH = os.path.join(BASE_DIR, "data", "base_de_dados_unificada.xlsx")

print(">>> SIGMA-Q carregando base padrão em:", DEFAULT_PATH)

# =========================
# Função principal: carregar_base
# =========================
def carregar_base(path: str = None, usecols: list | None = None) -> pd.DataFrame:
    """
    Carrega a base oficial de dados SIGMA-Q com checagem e normalização.
    """
    caminho = path or DEFAULT_PATH
    st.write(f"📂 Caminho da base: {caminho}")

    if not os.path.exists(caminho):
        st.error(f"❌ Arquivo não encontrado: {caminho}")
        st.stop()

    try:
        # Carrega planilha
        df = pd.read_excel(caminho, usecols=usecols)

        # Normaliza nomes das colunas
        df.columns = (
            df.columns.str.strip()
            .str.upper()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("ascii")
            .str.replace(" ", "_")
        )

        # Remove linhas totalmente vazias
        df = df.dropna(how="all").reset_index(drop=True)

        # Aplica limpeza e padronização textual
        df = normalizar_dataframe(df)

        st.success(f"✅ Base carregada com sucesso ({len(df)} registros, {len(df.columns)} colunas).")
        return df

    except Exception as e:
        st.error(f"⚠️ Erro ao carregar base: {e}")
        st.stop()


# =========================
# Função auxiliar: monitorar_base
# =========================
def monitorar_base(intervalo: int = 30, path: str = None, last_mtime: float | None = None) -> tuple[bool, float]:
    """
    Verifica se o arquivo da base foi modificado.
    Retorna uma tupla (modificado: bool, timestamp_atual: float).
    """
    caminho = path or DEFAULT_PATH
    try:
        mtime = os.path.getmtime(caminho)
    except Exception:
        return False, None

    if last_mtime is None:
        return False, mtime

    return (mtime != last_mtime), mtime
