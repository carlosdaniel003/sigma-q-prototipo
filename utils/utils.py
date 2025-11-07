import pandas as pd
import os

def carregar_dados(caminho_arquivo=None):
    """
    Carrega o arquivo Excel da base de dados e retorna um DataFrame limpo.
    Se nenhum caminho for informado, tenta localizar automaticamente 'base_de_dados_unificada.xlsx'
    dentro da pasta do projeto.
    """
    # Caminho padrão (caso o usuário não informe)
    if caminho_arquivo is None:
        caminho_arquivo = os.path.join(os.getcwd(), "data", "base_de_dados_unificada.xlsx")

        # Se não existir dentro de /data, tenta na raiz do projeto
        if not os.path.exists(caminho_arquivo):
            caminho_arquivo = os.path.join(os.getcwd(), "base_de_dados_unificada.xlsx")

    # Verifica se o arquivo existe
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {caminho_arquivo}")

    # Carrega a planilha
    df = pd.read_excel(caminho_arquivo, engine="openpyxl")


    # Padroniza nomes das colunas
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    # Remove linhas totalmente vazias
    df.dropna(how='all', inplace=True)

    # Remove espaços extras em strings
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()

    print(f"✅ Dados carregados de: {caminho_arquivo}")
    print(f"📊 Total de linhas: {len(df)}")

    return df
