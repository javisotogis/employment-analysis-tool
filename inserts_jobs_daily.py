import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

def df_to_db(df: pd.DataFrame, db_url: str):
    """
    Inserts new job postings from a DataFrame into a PostgreSQL (or other SQLAlchemy-compatible) database.
    Deduplicates using a set of key fields and links related tables (companies, locations, job_levels).
    
    Parameters:
        df (pd.DataFrame): The job postings with all relevant fields.
        db_url (str): SQLAlchemy database URI string (e.g., postgresql://user:pass@host:port/db).
    """

    # Connect to the database
    engine = create_engine(db_url)

    # Parse datetime fields with day-first format (e.g., 13/05/2025)
    df['created'] = pd.to_datetime(df['created'], errors='coerce', dayfirst=True)
    df['date_downloaded'] = pd.to_datetime(df['date_downloaded'], errors='coerce', dayfirst=True)

    with engine.begin() as conn:
        # Helper function: insert new values into lookup tables and map names to IDs
        def get_or_create_ids(table, name_col, df_col):
            id_col_map = {
                'companies': 'company_id',
                'locations': 'location_id',
                'job_levels': 'job_level_id'
            }
            id_col = id_col_map[table]

            # Load existing mappings
            existing = pd.read_sql(f"SELECT {id_col}, {name_col} FROM {table}", conn)
            value_id_map = dict(zip(existing[name_col], existing[id_col]))

            # Insert any missing values
            new_values = df[df_col].dropna().unique()
            if table == 'locations':
                for val in new_values:
                    if val not in value_id_map:
                        try:
                            subset = df[df[df_col] == val][['latitude', 'longitude']].dropna()
                            if not subset.empty:
                                row = subset.iloc[0]
                                lat, lon = row['latitude'], row['longitude']
                            else:
                                lat, lon = None, None

                            conn.execute(
                                text(f"""
                                    INSERT INTO locations (location_name, latitude, longitude)
                                    VALUES (:val, :lat, :lon)
                                """),
                                {'val': val, 'lat': lat, 'lon': lon}
                            )
                        except IntegrityError:
                            continue



            # Refresh mapping after insertion
            updated = pd.read_sql(f"SELECT {id_col}, {name_col} FROM {table}", conn)
            return df[df_col].map(dict(zip(updated[name_col], updated[id_col])))

        # Map company, location, and job level names to IDs
        df['company_id'] = get_or_create_ids('companies', 'company_name', 'company')
        df['location_id'] = get_or_create_ids('locations', 'location_name', 'location')
        df['job_level_id'] = get_or_create_ids('job_levels', 'level_name', 'job_level')

        # Drop rows missing foreign key references
        df = df.dropna(subset=['company_id', 'location_id'])

        # Load existing job records for duplicate detection
        existing_jobs = pd.read_sql("""
            SELECT job_id, title, description, salary_min, salary_max, redirect_url, company_id, location_id
            FROM jobs
        """, conn)

        # Define the key fields to check for duplication
        merge_keys = ['title', 'description', 'salary_min', 'salary_max', 'redirect_url', 'company_id', 'location_id']

        # Merge to find new (non-duplicate) rows only
        df_merged = df.merge(existing_jobs, on=merge_keys, how='left', indicator=True)
        df_new = df_merged[df_merged['_merge'] == 'left_only'].copy().drop(columns=['_merge'])

        if df_new.empty:
            print("✅ No new jobs to insert today.")
            return

        # Prepare the job table fields
        job_fields = [
            'title', 'description', 'salary_min', 'salary_max',

            'redirect_url', 'created', 'source',
            'company_id', 'location_id', 'job_level_id'
        ]

        # Insert the new job records
        df_new[job_fields].to_sql('jobs', conn, if_exists='append', index=False)
        print(f"✅ Inserted {len(df_new)} new job(s).")

        # Fetch the most recent N job_ids that were just inserted
        limit = len(df_new)
        new_jobs = pd.read_sql(f"""
            SELECT job_id, title, created
            FROM jobs
            ORDER BY job_id DESC
            LIMIT {limit}
        """, conn)

        # Reverse the DataFrame to match original insertion order
        new_jobs = new_jobs.iloc[::-1].reset_index(drop=True)
        df_new = df_new.reset_index(drop=True)

        # Check row alignment before linking metadata
        if len(new_jobs) != len(df_new):
            print("⚠️ Warning: Could not match job_ids for metadata exactly.")
            return

        # Assign job_ids for metadata
        df_new['job_id'] = new_jobs['job_id']
        metadata_df = df_new[['job_id', 'search_query', 'search_location', 'date_downloaded']]
        metadata_df.dropna(subset=['job_id'], inplace=True)

        # Insert metadata records
        metadata_df.to_sql('job_metadata', conn, if_exists='append', index=False)
        print(f"📎 Linked metadata for {len(metadata_df)} job(s).")
