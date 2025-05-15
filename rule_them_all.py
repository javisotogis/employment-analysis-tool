import os
import pandas as pd
from reed_api import get_reed_jobs
from adzuna_api import get_adzuna_jobs
from get_lat_long import add_lat_long_if_missing
from standardize import standardize_dataframe
from assing_job_level import assign_job_level
from inserts_jobs_daily import df_to_db
from check_duplicates import remove_duplicates, filter_new_jobs_from_api
from dotenv import load_dotenv
from datetime import datetime
from predict_and_update_salaries import predict_and_update_salaries

if __name__ == "__main__":
    queries = ["data analyst", "data science", "GIS"]
    locations = ["England", "Scotland", "Wales", "Northern Ireland", "remote"]

    all_dfs = []

    for query in queries:
        for location in locations:
            print(f"📥 REED: {query} in {location}")
            df = get_reed_jobs(query, location)
            if not df.empty:
                all_dfs.append(standardize_dataframe(df, source="reed"))

    for query in queries:
        for location in locations:
            print(f"📥 ADZUNA: {query} in {location}")
            df = get_adzuna_jobs(query, location, total_results=100)
            if not df.empty:
                df["search_query"] = query
                df["search_location"] = location
                df["date_downloaded"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                all_dfs.append(standardize_dataframe(df, source="adzuna"))

    
   
    # remove duplicates
    clean_df = remove_duplicates(all_dfs)

    # remove barista jobs
    clean_df = clean_df[~(clean_df['title'].str.contains('barista', case=False, na=False) | clean_df['description'].str.contains('barista', case=False, na=False))]


    # remove existing jobs from the database

    new_jobs_from_api_df = filter_new_jobs_from_api(clean_df)


    
    if not new_jobs_from_api_df.empty:
        coords_df = new_jobs_from_api_df.copy() 
        print(f"✅ Combined dataset has {len(coords_df)} rows")
        coords_df = add_lat_long_if_missing(coords_df, location_column="location")

        ## Assign job levels
        job_levels_df = assign_job_level(coords_df)

        ## Calculate missing salaries
        #calculated_salaries_df = predict_missing_salaries(job_levels_df)

        ## Import to the database
        print(f"✅ Final dataset loaded with {len(job_levels_df)} rows")
        if job_levels_df.empty:
            raise ValueError("The DataFrame is empty. Please check the data source.")
        ## Import to the database
        DB_PARAMETERS = os.getenv("DB_PARAMETERS")
        if not DB_PARAMETERS:
            raise ValueError("Database parameters not found in environment variables.")
        
        df_to_db(job_levels_df, DB_PARAMETERS)


        ## Predict and update salaries
        load_dotenv()  # Load variables from .env file
        print("🚀 New data has been inserted into the DB (simulated).")
        predict_and_update_salaries()

        ## Save the final dataset
        os.makedirs("tmp_outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # e.g., 20250507194500
        filename = f"tmp_outputs/all_jobs_{timestamp}.csv"
        job_levels_df.to_csv(filename, index=False)
        print(f"✅ Final dataset saved with {len(job_levels_df)} rows")
    else:
        print("⚠ No data collected.")
    
    

    
