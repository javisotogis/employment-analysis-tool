# jooble_api.py

import os
import time
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import re

# Load API key
load_dotenv()
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")

BASE_URL = f"https://jooble.org/api/{JOOBLE_API_KEY}"
SLEEP_TIME = 0.25


def fetch_jooble_jobs(query, location):
    """
    Sends a POST request to Jooble API with job query and location.
    """
    payload = {
        "keywords": query,
        "location": location
    }

    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching Jooble jobs for '{query}' in '{location}': {e}")
        return None


def extract_salary_from_text(text):
    """
    Attempts to extract salary from the job description using regex.
    """
    if not text:
        return None

    patterns = [
        r"[£$]\s?\d{1,3}(?:,\d{3})+",                        # £62,500 / $62,500
        r"[£$]\s?\d{2,3}[kK]",                               # £100k / $100K
        r"[£$]\s?\d+(?:\.\d{2})?\s?-\s?[£$]?\s?\d+(?:\.\d{2})?",  # £18 - £21
        r"[£$]?\d+(?:[kK])?\s?(?:to|-)\s?[£$]?\d+(?:[kK])?"  # 100k to 120k
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()

    return None


def parse_jobs(results, query, location):
    """
    Normalizes Jooble job results into a fixed schema.
    """
    jobs = []

    for job in results.get("jobs", []):
        job_desc = job.get("snippet", "")
        job_loc = job.get("location", "")

        # 🛑 Skip jobs outside the UK
        if "UK" not in job_loc and "United Kingdom" not in job_loc:
            continue

        salary = job.get("salary") or extract_salary_from_text(job_desc)

        jobs.append({
            "website_employerid": None,
            "website_jobid": None,
            "employer_name": job.get("company", ""),
            "job_url": job.get("link", ""),
            "applications": None,
            "job_title": job.get("title", ""),
            "job_description": job_desc,
            "location": job_loc,
            "latitude": None,
            "longitude": None,
            "job_type_uuid": None,
            "city_uuid": None,
            "currency": None,
            "country": "UK",
            "minimum_salary": None,
            "maximum_salary": None,
            "estimated_salary": salary,
            "expiration_date": None,
            "date_downloaded": datetime.today().strftime('%Y-%m-%d'),
            "job_created_date": job.get("updated", "")
        })

    return jobs


def get_jooble_jobs(queries, locations):
    """
    Fetches jobs for all query-location combinations.
    """
    all_jobs = []

    for query in queries:
        for location in locations:
            location_query = f"{location}, UK"  # ✅ Force UK scope
            print(f"🔎 Searching Jooble for '{query}' in '{location_query}'...")
            results = fetch_jooble_jobs(query, location_query)

            if results and "jobs" in results:
                jobs = parse_jobs(results, query, location_query)
                all_jobs.extend(jobs)

            time.sleep(SLEEP_TIME)

    df = pd.DataFrame(all_jobs)

    # Ensure all required columns are present
    expected_columns = [
        "website_employerid", "website_jobid", "employer_name", "job_url", "applications",
        "job_title", "job_description", "location", "latitude", "longitude",
        "job_type_uuid", "city_uuid", "currency", "country", "minimum_salary",
        "maximum_salary", "estimated_salary", "expiration_date", "date_downloaded", "job_created_date"
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    df = df[expected_columns]
    return df
