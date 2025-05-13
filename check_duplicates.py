import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import NoSuchTableError
from dotenv import load_dotenv



def remove_duplicates(df):
    """
    Removes duplicate rows from a DataFrame (or list of DataFrames) where the values in
    'title', 'description', 'salary_min', 'salary_max', and 'redirect_url' are the same.
    """
    columns_to_check = ['title', 'description', 'salary_min', 'salary_max', 'redirect_url']

    if isinstance(df, list):
        df = pd.concat([d for d in df if not d.empty], ignore_index=True)

    cleaned_df = df.drop_duplicates(subset=columns_to_check, keep='first').reset_index(drop=True)
    return cleaned_df


def filter_new_jobs_from_api(api_df):
    """
    Filters out jobs from the API dataframe that already exist in the 'jobs' table in the database.
    The comparison is based on 'title', 'description', 'salary_min', 'salary_max', and 'redirect_url'.

    Parameters:
        api_df (pd.DataFrame): DataFrame containing job listings from an API.

    Returns:
        pd.DataFrame: Filtered DataFrame containing only new job listings.
    """
    db_url = os.getenv("DB_PARAMETERS")
    if not db_url:
        raise ValueError("Database parameters not found in environment variables.")

    engine = create_engine(db_url)

    # Try loading the jobs table, handle empty or missing table gracefully
    try:
        database_df = pd.read_sql_table("jobs", con=engine)
    except (ValueError, NoSuchTableError):
        # Return original API dataframe if table doesn't exist or is empty
        return api_df.reset_index(drop=True)

    # If table exists but is empty
    if database_df.empty:
        return api_df.reset_index(drop=True)

    columns_to_check = ['title', 'description', 'salary_min', 'salary_max', 'redirect_url']

    # Ensure comparison is based on the relevant columns
    db_subset = database_df[columns_to_check].drop_duplicates()
    api_subset = api_df[columns_to_check]

    # Keep only new jobs that are not already in the database
    mask = ~api_subset.apply(tuple, axis=1).isin(db_subset.apply(tuple, axis=1))
    return api_df[mask].reset_index(drop=True)