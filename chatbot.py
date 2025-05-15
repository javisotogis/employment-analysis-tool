import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st
import openai
import pandas as pd
from sqlalchemy import create_engine


DB_PARAMETERS = os.getenv("DB_PARAMETERS")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ---- SETTINGS ----
openai.api_key = DB_PARAMETERS


# ---- DATABASE CONNECTION ----
@st.cache_resource
def get_engine():
    return create_engine(DB_PARAMETERS)

engine = get_engine()

# ---- APP LAYOUT ----
st.set_page_config(page_title="Chat with Your Data", layout="wide")
st.title("🤖 Chat with your PostgreSQL Data")

# Chat input
user_question = st.text_input("Ask a question about jobs, locations, or salaries:")

# ---- QUERY LLM FOR SQL ----
def get_sql_from_gpt(question):
    system_prompt = """
You are a data analyst who writes safe SQL queries for PostgreSQL.
The database has the following tables:

1. jobs (job_id, title, description, salary_min, salary_max, location_id, company_id, created)
2. locations (location_id, location_name, latitude, longitude)
3. uk_countries (globalid, geometry)

Rules:
- Use table aliases.
- Join locations via location_id when needed.
- Always LIMIT results to 10 unless the user requests otherwise.
- Don't use DELETE, INSERT, or UPDATE.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write a SQL query for this: {question}"}
        ]
    )
    return response.choices[0].message.content.strip()

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



