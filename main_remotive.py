import os
import pandas as pd
from remotive_api import get_remotive_jobs  # Import the function

def main():
    all_data = []  # This will now be a list of DataFrames
    queries = ["Data analyst", "Data Science", "GIS"]
    locations = [
        "London", "Edinburgh", "Cardiff", "Belfast", "Manchester", "Birmingham",
        "Glasgow", "Liverpool", "Leeds", "Bristol", "Newcastle upon Tyne", "Swansea",
        "Sheffield", "Nottingham", "Leicester", "Coventry", "Southampton",
        "Portsmouth", "York", "Derby", "Harrogate"
    ]

    for query in queries:
        for location in locations:
            job_df = get_remotive_jobs([query])  # Remotive is remote-first, location is ignored
            if not job_df.empty:
                all_data.append(job_df)  # Append each DataFrame

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        os.makedirs("tmp_outputs", exist_ok=True)
        combined_df.to_csv("tmp_outputs/remotive_all_jobs.csv", index=False)
        print(f"✅ Exported {len(combined_df)} jobs to tmp_outputs/remotive_all_jobs.csv")
    else:
        print("⚠ No job data found.")


if __name__ == "__main__":
    main()

