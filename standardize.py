import pandas as pd
from datetime import datetime

def standardize_dataframe(df, source):
    df_standard = pd.DataFrame()
    df_standard["title"] = df.get("title", df.get("jobTitle", ""))
    df_standard["company"] = df.get("employerName", df.get("company", ""))
    df_standard["location"] = df.get("locationName", df.get("location", ""))
    df_standard["latitude"] = df.get("latitude", None)
    df_standard["longitude"] = df.get("longitude", None)
    df_standard["description"] = df.get("jobDescription", df.get("description", ""))
    df_standard["salary_min"] = df.get("minimumSalary", df.get("salary_min", None))
    df_standard["salary_max"] = df.get("maximumSalary", df.get("salary_max", None))
    df_standard["redirect_url"] = df.get("jobUrl", df.get("redirect_url", ""))
    df_standard["created"] = df.get("date", df.get("created", ""))
    df_standard["search_query"] = df.get("search_query", "")
    df_standard["search_location"] = df.get("search_location", "")
    df_standard["source"] = source
    df_standard["date_downloaded"] = df.get("date_downloaded", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return df_standard
