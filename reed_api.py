import requests
import base64
import time
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("REED_API_KEY")
time_sleep = 0.25

def get_reed_jobs(job_title, location, total_results=1000, results_per_page=100):
    url = "https://www.reed.co.uk/api/1.0/search"
    auth_value = base64.b64encode(f"{API_KEY}:".encode()).decode()
    headers = {"Accept": "application/json", "Authorization": f"Basic {auth_value}"}
    all_jobs = []

    for skip in range(0, total_results, results_per_page):
        params = {
            "keywords": job_title,
            "locationName": location,
            "resultsToTake": results_per_page,
            "resultsToSkip": skip
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            jobs = response.json().get("results", [])
            if not jobs: break
            all_jobs.extend(jobs)
            time.sleep(time_sleep)
        else:
            print(f"❌ REED error {response.status_code}: {response.text}")
            break

    if not all_jobs:
        return pd.DataFrame()

    df = pd.DataFrame(all_jobs)
    df["search_query"] = job_title
    df["search_location"] = location
    df["date_downloaded"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df
