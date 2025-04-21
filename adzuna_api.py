# adzuna_api.py

import requests
import time
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv()

APP_ID = os.getenv("ADZUNA_ID")
API_KEY = os.getenv("ADZUNA_API_KEY")
COUNTRY = "gb"
SLEEP_TIME = 0.25


def fetch_job_listings(app_id, app_key, search_query, location, page=1, results_per_page=50, country='gb'):
    base_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = {
        'app_id': app_id,
        'app_key': app_key,
        'what': search_query,
        'where': location,
        'results_per_page': results_per_page
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Request failed with status {response.status_code}")
        return None


def parse_jobs(results, query, location):
    simplified_jobs = []

    for job in results:
        simplified_jobs.append({
            "title": job.get("title", ""),
            "company": job.get("company", {}).get("display_name", ""),
            "redirect_url": job.get("redirect_url", ""),
            "latitude": job.get("latitude"),
            "longitude": job.get("longitude"),
            "location": job.get("location", {}).get("display_name", ""),
            "description": job.get("description", ""),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "area": job.get("area"),
            "created": job.get("created"),
            "search_query": query,
            "search_location": location
        })

    return simplified_jobs


def get_adzuna_jobs(query, location, total_results=200, results_per_page=50):
    all_jobs = []

    for skip in range(0, total_results, results_per_page):
        page = (skip // results_per_page) + 1
        print(f"📄 Fetching page {page} for '{query}' in {location}...")

        response = fetch_job_listings(APP_ID, API_KEY, query, location, page=page, results_per_page=results_per_page, country=COUNTRY)

        if response and "results" in response:
            jobs = parse_jobs(response["results"], query, location)
            if not jobs:
                break
            all_jobs.extend(jobs)
            time.sleep(SLEEP_TIME)
        else:
            break

    # Convert to DataFrame and add today's date
    df = pd.DataFrame(all_jobs)
    df["date_downloaded"] = datetime.today().strftime('%Y-%m-%d')

    return df
