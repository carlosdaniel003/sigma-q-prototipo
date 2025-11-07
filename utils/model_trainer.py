# utils/model_trainer.py
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import streamlit as st

# Caminho oficial da base do SIGMA-Q
BASE_PATH = os.path.join("data", "base_de_dados_unificada.xlsx")
MODEL_PATH = os.path.join("model", "modelo_classificacao.pkl")
VECTORIZER_PATH = os.path.join("model", "vectorizer.pkl")


def treinar_modelo():
    """
    Treina o modelo de IA SIGMA-Q com base na planilha Quality Control.
    """
    if not os.path.exists(BASE_PATH):
        st.error(f"❌ Arquivo não encontrado: {BASE_PATH}")
        return None, None

    st.info("🚀 Iniciando treinamento do modelo SIGMA-Q...")

    try:
        # Carregar a planilha oficial
        df = pd.read_excel(BASE_PATH)
        df.columns = (
            df.columns.str.strip()
            .str.upper()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("ascii")
            .str.replace(" ", "_")
        )

        # Detecta a coluna de texto
        texto_col = None
        for c in ["DESC_FALHA", "DESC._FALHA", "DESCRICAO_DA_FALHA", "DESCRICAO"]:
            if c in df.columns:
                texto_col = c
                break

        if not texto_col:
            st.error("⚠️ Nenhuma coluna de texto (descrição de falha) encontrada na base.")
            return None, None

        # Detecta a coluna de rótulo
        if "CATEGORIA" not in df.columns:
            st.error("⚠️ Coluna 'CATEGORIA' não encontrada na base.")
            return None, None

        # Remove linhas inválidas
        df = df.dropna(subset=[texto_col, "CATEGORIA"])
        df = df[df[texto_col].astype(str).str.strip() != ""]

        # Divisão treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            df[texto_col], df["CATEGORIA"], test_size=0.2, random_state=42
        )

        # Cria pipeline de vetor + modelo
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=1000, solver="lbfgs", multi_class="auto")),
        ])

        # Treinamento
        pipeline.fit(X_train, y_train)

        # Avaliação rápida
        score = pipeline.score(X_test, y_test)
        st.success(f"✅ Treinamento concluído — acurácia: {score*100:.2f}%")

        # Salvar modelo e vetor
        os.makedirs("model", exist_ok=True)
        joblib.dump(pipeline, MODEL_PATH)
        joblib.dump(pipeline.named_steps["tfidf"], VECTORIZER_PATH)

        st.toast("💾 Modelo e vetorizador salvos com sucesso!")
        return pipeline.named_steps["clf"], pipeline.named_steps["tfidf"]

    except Exception as e:
        st.error(f"❌ Erro durante o treinamento: {e}")
        return None, None
