# main_jooble.py

import os
import pandas as pd
from jooble_api import get_jooble_jobs

def main():
    all_data = []
    queries = ["Data analyst", "Data Science", "GIS"]
    locations = [
        "London", "Edinburgh", "Cardiff", "Belfast", "Manchester", "Birmingham",
        "Glasgow", "Liverpool", "Leeds", "Bristol", "Newcastle upon Tyne", "Swansea",
        "Sheffield", "Nottingham", "Leicester", "Coventry", "Southampton",
        "Portsmouth", "York", "Derby", "Harrogate"
    ]

    job_df = get_jooble_jobs(queries, locations)
    if not job_df.empty:
        all_data.append(job_df)

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        os.makedirs("tmp_outputs", exist_ok=True)
        combined_df.to_csv("tmp_outputs/jooble_all_jobs.csv", index=False, encoding="utf-8-sig")
        print(f"✅ Exported {len(combined_df)} jobs to tmp_outputs/jooble_all_jobs.csv")
    else:
        print("⚠ No job data found.")

if __name__ == "__main__":
    main()
