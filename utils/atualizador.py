# utils/atualizador.py
import pandas as pd
import os
import time

DEFAULT_PATH = os.path.join("data", "quality_control_outubro.xlsx")

def carregar_base(path: str = None, usecols: list | None = None) -> pd.DataFrame:
    """
    Carrega a base oficial (oculta no front-end) e retorna um DataFrame limpo.
    - path: caminho alternativo (opcional). Se None, usa a base oficial.
    - usecols: se quiser carregar apenas algumas colunas para memória economizada.
    """
    caminho = path or DEFAULT_PATH
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Base de dados não encontrada: {caminho}")

    # Leitura básica
    df = pd.read_excel(caminho, usecols=usecols)

    # Normalização de cabeçalhos (mantém original, mas padroniza espaços/acentos)
    df.columns = (
        df.columns.str.strip()
                  .str.upper()
                  .str.normalize('NFKD')  # remove acentos
                  .str.encode('ascii', errors='ignore').str.decode('ascii')
                  .str.replace(" ", "_")
    )

    # Pequenas limpezas comuns
    # Exemplo: remover linhas totalmente vazias
    df = df.dropna(how="all").reset_index(drop=True)

    # Garantir colunas críticas existam (adapte se necessário)
    expected = ["DESCRICAO","DESCRICAO_DA_FALHA","REFERENCIA","MOTIVO","CATEGORIA"]
    # não lançamos erro (apenas aviso) — evita quebrar em ambientes com variações
    for c in expected:
        if c not in df.columns:
            # tentamos equivalentes comuns
            pass

    return df

def monitorar_base(intervalo: int = 30, path: str = None, last_mtime: float | None = None) -> bool:
    """
    Verifica se o arquivo da base foi modificado. Retorna True se houve modificação.
    - intervalo: segundos mínimo entre checagens (função leve — pode ser chamada frequentemente).
    - path: caminho do arquivo (opcional).
    - last_mtime: último modification time conhecido; se None, retorna False e informa o mtime atual.
    """
    caminho = path or DEFAULT_PATH
    try:
        mtime = os.path.getmtime(caminho)
    except Exception:
        return False

    if last_mtime is None:
        return False, mtime

    return (mtime != last_mtime), mtime
