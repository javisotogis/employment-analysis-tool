import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st

# ✅ Must be first Streamlit command
st.set_page_config(page_title="Chat with Your Data", layout="wide")

# ---- SETTINGS ----
load_dotenv()
DB_PARAMETERS = os.getenv("DB_PARAMETERS")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# ---- DATABASE CONNECTION ----
@st.cache_resource
def get_engine():
    return create_engine(DB_PARAMETERS)

engine = get_engine()

# ---- APP LAYOUT ----
st.title("🤖 Chat with your PostgreSQL Data")

# Chat input
user_question = st.text_input("Ask a question about jobs, locations, or salaries:")

# ---- QUERY LLM FOR SQL ----
from llama_cpp import Llama

# Load the model once
@st.cache_resource
def load_model():
    return Llama(
        model_path=r"C:\data_analytics\00ProyectoFinalDA\models\mistral-7b-instruct-v0.1.Q2_K.gguf",  # 🔁 Your actual path
        n_ctx=2048,
        n_threads=8,  # Set to number of CPU threads you want to use
        verbose=False
    )

llm = load_model()

def get_sql_from_gpt(question):
    system_prompt = """
You are a helpful assistant that writes safe PostgreSQL SQL queries.
The database has these tables:

1. jobs (job_id, title, description, salary_min, salary_max, location_id, company_id, created)
2. locations (location_id, location_name, latitude, longitude)
3. uk_countries (globalid, geometry)

Rules:
- Use table aliases.
- LIMIT to 10 results unless otherwise asked.
- Never use INSERT, UPDATE or DELETE.
"""

    full_prompt = f"[INST] {system_prompt}\n\nUser: {question} [/INST]"

    response = llm(full_prompt, stop=["</s>"], max_tokens=512)
    return response["choices"][0]["text"].strip()



# ---- RUN QUERY ----
if user_question:
    with st.spinner("🔍 Asking ChatGPT..."):
        try:
            sql = get_sql_from_gpt(user_question)
            st.code(sql, language="sql")

            df = pd.read_sql(sql, con=engine)
            st.success("✅ Query successful!")
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
