# utils/atualizador.py
import pandas as pd
import os
import time

# ------------------------------------------------------------
# Caminho absoluto — compatível com Streamlit Cloud e ambiente local
# ------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_PATH = os.path.join(BASE_DIR, "data", "quality_control_outubro.xlsx")

def carregar_base(path: str = None, usecols: list | None = None) -> pd.DataFrame:
    """
    Carrega a base oficial (oculta no front-end) e retorna um DataFrame limpo.
    - path: caminho alternativo (opcional). Se None, usa a base oficial.
    - usecols: se quiser carregar apenas algumas colunas para memória economizada.
    """

    caminho = path or DEFAULT_PATH
    print(f"[SIGMA-Q] Tentando carregar a base em: {caminho}")  # debug visível no terminal

    # Verifica se o arquivo existe
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"❌ Base de dados não encontrada no caminho: {caminho}")

    # Leitura básica
    try:
        df = pd.read_excel(caminho, usecols=usecols)
    except Exception as e:
        raise RuntimeError(f"⚠️ Erro ao ler a planilha '{caminho}': {e}")

    # Normalização dos cabeçalhos
    df.columns = (
        df.columns.str.strip()
                  .str.upper()
                  .str.normalize('NFKD')  # remove acentos
                  .str.encode('ascii', errors='ignore').str.decode('ascii')
                  .str.replace(" ", "_")
    )

    # Remover linhas totalmente vazias
    df = df.dropna(how="all").reset_index(drop=True)

    # Aviso se colunas importantes estiverem ausentes
    expected = ["DESCRICAO", "DESCRICAO_DA_FALHA", "REFERENCIA", "MOTIVO", "CATEGORIA"]
    faltando = [c for c in expected if c not in df.columns]
    if faltando:
        print(f"[AVISO] Colunas não encontradas na base: {faltando}")

    print(f"[SIGMA-Q] Base carregada com sucesso: {len(df)} registros, {len(df.columns)} colunas.")
    return df


def monitorar_base(intervalo: int = 30, path: str = None, last_mtime: float | None = None) -> tuple[bool, float]:
    """
    Verifica se o arquivo da base foi modificado.
    Retorna (True/False, mtime).
    """
    caminho = path or DEFAULT_PATH
    try:
        mtime = os.path.getmtime(caminho)
    except Exception:
        return False, None

    if last_mtime is None:
        return False, mtime

    return (mtime != last_mtime), mtime
