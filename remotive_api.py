# remotive_api.py

import requests
import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Constants
REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"
SLEEP_TIME = 0.25


def fetch_remotive_jobs(query):
    """
    Fetch jobs from the updated Remotive API.
    """
    params = {"search": query}
    try:
        response = requests.get(REMOTIVE_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching Remotive jobs for '{query}': {e}")
        return None


def clean_html(raw_html):
    """
    Convert HTML to clean readable plain text, preserving paragraph breaks.
    """
    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove scripts, styles, and image tags
    for tag in soup(["script", "style", "img"]):
        tag.decompose()

    # Replace structural tags with line breaks
    for tag in soup.find_all(["br", "p", "div", "ul", "li"]):
        tag.insert_before("\n")

    # Get raw text
    text = soup.get_text()

    # Normalize whitespace
    text = re.sub(r'\n{2,}', '\n\n', text)  # keep paragraph breaks
    text = text.strip()

    return text


def parse_jobs(results, query):
    """
    Parse and normalize Remotive jobs into a fixed schema.
    """
    parsed = []

    for job in results.get("jobs", []):
        parsed.append({
            "website_employerid": None,
            "website_jobid": job.get("id"),
            "employer_name": job.get("company_name"),
            "job_url": job.get("url"),
            "applications": None,
            "job_title": job.get("title"),
            "job_description": clean_html(job.get("description", "")),
            "location": job.get("candidate_required_location"),
            "latitude": None,
            "longitude": None,
            "job_type_uuid": job.get("job_type"),
            "city_uuid": None,
            "currency": None,
            "country": None,
            "minimum_salary": None,
            "maximum_salary": None,
            "estimated_salary": None,
            "expiration_date": None,
            "date_downloaded": datetime.today().strftime('%Y-%m-%d'),
            "job_created_date": job.get("publication_date")
        })

    return parsed


def get_remotive_jobs(query_list):
    """
    Fetch and normalize job results for multiple queries from Remotive.
    """
    all_jobs = []

    for query in query_list:
        print(f"🔎 Searching Remotive for '{query}'...")
        results = fetch_remotive_jobs(query)
        if results:
            jobs = parse_jobs(results, query)
            all_jobs.extend(jobs)
        time.sleep(SLEEP_TIME)

    df = pd.DataFrame(all_jobs)

    expected_columns = [
        "website_employerid", "website_jobid", "employer_name", "job_url", "applications",
        "job_title", "job_description", "location", "latitude", "longitude",
        "job_type_uuid", "city_uuid", "currency", "country", "minimum_salary",
        "maximum_salary", "estimated_salary", "expiration_date", "date_downloaded", "job_created_date"
    ]

    # Ensure consistent schema
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    df = df[expected_columns]
    return df
