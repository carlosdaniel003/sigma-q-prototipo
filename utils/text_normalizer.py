import re
import unicodedata
import pandas as pd


# =========================
# 🔧 FUNÇÃO PRINCIPAL DE LIMPEZA
# =========================
def normalizar_texto(texto: str) -> str:
    """
    Limpa, corrige e padroniza textos técnicos da base SIGMA-Q.
    Corrige erros de digitação, acentuação, duplicidades e espaços extras.
    """

    if not isinstance(texto, str):
        return texto

    # Remove acentos mantendo apenas caracteres ASCII
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

    # Converte tudo para minúsculas
    texto = texto.lower().strip()

    # Corrige erros de digitação comuns (vocabulário técnico SIGMA-Q)
    substituicoes = {
        # termos técnicos frequentes
        "qeimado": "queimado",
        "qseimado": "queimado",
        "queimdo": "queimado",
        "qeimdo": "queimado",
        "queimmado": "queimado",
        "blutooth": "bluetooth",
        "bluetooh": "bluetooth",
        "bluetoth": "bluetooth",
        "tweter": "tweeter",
        "tweteer": "tweeter",
        "sem som": "sem áudio",
        "audio": "áudio",
        "autonaticamente": "automaticamente",
        "defeito": "defeito",
        "reincidencia": "reincidência",
        "vibracao": "vibração",
        "mancha escura": "mancha",
    }

    for errado, certo in substituicoes.items():
        texto = re.sub(rf"\b{errado}\b", certo, texto)

    # Remove palavras duplicadas consecutivas (ex: "ruido ruido")
    texto = re.sub(r'\b(\w+)( \1\b)+', r'\1', texto)

    # Remove pontuação no fim
    texto = re.sub(r'[;.,]+$', '', texto)

    # Normaliza espaços
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto


# =========================
# 🧩 FUNÇÃO PARA DATAFRAMES
# =========================
def normalizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica normalização textual e padronização de campos em toda a base.
    """
    colunas_texto = ["Descrição", "Desc. Falha", "Desc. Componente", "Análise"]

    for col in colunas_texto:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(normalizar_texto)

    # Padroniza colunas de categoria e motivo
    for col in ["Categoria", "Motivo"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    # Remove espaços de todas as colunas tipo string
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    return df
