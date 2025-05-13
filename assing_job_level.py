import re
import pandas as pd

def assign_job_level(df):
    """
    Takes a DataFrame with 'title' and 'description' columns,
    returns the same DataFrame with an added 'job_level' column.
    """
    # --- Define expanded keyword patterns ---
    apprentice_terms = r"\b(apprentice|apprenticeship|intern(ship)?|trainee)\b"
    graduate_terms = r"\b(graduate|entry[- ]level|early[- ]career|recent[- ]graduate)\b"
    junior_terms = r"\b(junior|jr|early[- ]level|entry[- ]position)\b"
    senior_terms = r"\b(senior|sr|lead|principal|head|expert|specialist|manager|architect|chief|consultant|director)\b"
    mid_terms = r"\b(mid[- ]?level|associate|intermediate|experienced|analyst)\b"

    # --- Classifier function ---
    def classify_job_level(row):
        title = str(row.get('title', '')).lower()
        description = str(row.get('description', '')).lower()
        text = f"{title} {description}"

        if re.search(apprentice_terms, text):
            return "Apprentice"
        elif re.search(graduate_terms, text):
            return "Graduate"
        elif re.search(junior_terms, text):
            return "Junior"
        elif re.search(senior_terms, text):
            return "Senior"
        elif re.search(mid_terms, text):
            return "Mid-level"
        # Fallback checks (title-only)
        if re.search(apprentice_terms, title):
            return "Apprentice"
        elif re.search(graduate_terms, title):
            return "Graduate"
        elif re.search(junior_terms, title):
            return "Junior"
        elif re.search(senior_terms, title):
            return "Senior"
        elif re.search(mid_terms, title):
            return "Mid-level"

        return "Unknown"

    # --- Apply the classifier ---
    df['job_level'] = df.apply(classify_job_level, axis=1)

    return df
