
import os
import pandas as pd
from reed_api import get_reed_jobs
from adzuna_api import get_adzuna_jobs
from get_lat_long import add_lat_long_if_missing
from standardize import standardize_dataframe
from assing_job_level import assign_job_level
from predict_missing_salaries import predict_missing_salaries
from inserts_jobs_daily import df_to_db
from dotenv import load_dotenv
from datetime import datetime


import os
from dotenv import load_dotenv
from predict_and_update_salaries import predict_and_update_salaries

def main():
    load_dotenv()  # Load variables from .env file
    print("🚀 New data has been inserted into the DB (simulated).")
    predict_and_update_salaries()

if __name__ == "__main__":
    main()

