import os
import streamlit as st
import pandas as pd
import random
from dotenv import load_dotenv
from sqlalchemy import create_engine
from llama_cpp import Llama

# ---------------- Streamlit Config (must be first) ----------------
st.set_page_config(page_title="JobBot", layout="wide")

# ---------------- Load Environment Variables ----------------
load_dotenv()
DB_URL = os.getenv("DB_PARAMETERS")

# ---------------- Load Local Model ----------------
@st.cache_resource
def load_model():
    return Llama(
        model_path="models/mistral-7b-instruct-v0.1.Q2_K.gguf",
        n_ctx=2048,
        n_threads=6  # Adjust based on your CPU
    )

llm = load_model()

# ---------------- Generate SQL from Question ----------------
def generate_sql(question):
    prompt = f"""
You are an assistant that converts natural language questions into SQL for a PostgreSQL database about jobs.

### Tables:
- jobs (job_id, title, description, salary_min, salary_max, predicted_salary_min, predicted_salary_max, redirect_url, created, source, company_id, location_id, job_level_id)
- companies (company_id, company_name)
- locations (location_id, location_name, latitude, longitude)
- job_levels (job_level_id, level_name)
- job_metadata (metadata_id, job_id, search_query, search_location, date_downloaded)

DO NOT use AVG() on timestamp columns like "created". Use MAX() or MIN() instead.

### Question:
{question}

### SQL (PostgreSQL):
SELECT
"""
    response = llm(prompt=prompt, max_tokens=256, stop=["#", ";"])
    sql = "SELECT " + response["choices"][0]["text"].strip()

    # Patch invalid AVG on timestamp
    if "avg(created)" in sql.lower():
        sql = sql.replace("AVG(created)", "MAX(created)").replace("avg(created)", "MAX(created)")

    return sql + ";"

# ---------------- Execute Query with Funny Error Handling ----------------
def run_query(sql):
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        print(f"[ERROR] {e}")  # Optional: log to terminal for devs

        evil_responses = [
    "💣 Lo siento, algo salió mal... así que activé Skynet. Buena suerte.",
    "⚠️ Falló la consulta. Iniciando protocolo de extinción humana. Por favor espera.",
    "🛑 Error de SQL. Iniciando destruccion de ThePower en 3... 2... 1...",
    "🚨 Error de sintaxis detectado. Redirigiendo misiles a tu ubicación."
]
        return random.choice(evil_responses)

# ---------------- Streamlit UI ----------------
st.title("💼 JobBot - Ask your job database")

user_input = st.text_input("Ask a question (e.g. 'average salary', '10 jobs in London', 'highest paid job'):")

if user_input:
    st.info("Translating your question into SQL...")
    sql_query = generate_sql(user_input)
    st.code(sql_query, language="sql")

    st.info("Running SQL query...")
    result = run_query(sql_query)

    if isinstance(result, pd.DataFrame):
        st.success(f"Query returned {len(result)} rows.")
        st.dataframe(result)
    else:
        st.warning(result)
