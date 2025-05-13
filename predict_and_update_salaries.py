import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sqlalchemy import create_engine, text
import joblib

def predict_and_update_salaries(model_dir='models', metrics_path='metrics_results.csv'):
    db_url = os.getenv("DB_PARAMETERS")
    if not db_url:
        raise ValueError("❌ Environment variable DB_PARAMETERS is not set.")

    engine = create_engine(db_url)
    df = pd.read_sql("SELECT job_id, title, description, salary_min, salary_max FROM jobs", engine)

    df['title'] = df['title'].fillna('')
    df['description'] = df['description'].fillna('')
    df['text'] = df['title'] + ' ' + df['description']

    os.makedirs(model_dir, exist_ok=True)
    tfidf_path = os.path.join(model_dir, 'tfidf.joblib')

    if os.path.exists(tfidf_path):
        tfidf = joblib.load(tfidf_path)
    else:
        tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
        tfidf.fit(df['text'])
        joblib.dump(tfidf, tfidf_path)

    X_all = tfidf.transform(df['text'])

    metrics = []

    # ----- salary_min -----
    df_min_train = df[df['salary_min'].notna()]
    df_min_missing = df[df['salary_min'].isna()]
    model_min_path = os.path.join(model_dir, 'model_salary_min.joblib')

    if not df_min_train.empty:
        X_min_train = tfidf.transform(df_min_train['text'])
        y_min_train = df_min_train['salary_min']

        if os.path.exists(model_min_path):
            model_min = joblib.load(model_min_path)
        else:
            model_min = RandomForestRegressor(n_estimators=100, random_state=42)
            model_min.fit(X_min_train, y_min_train)
            joblib.dump(model_min, model_min_path)

        X_eval, X_test, y_eval, y_test = train_test_split(X_min_train, y_min_train, test_size=0.2, random_state=42)
        y_pred = model_min.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        metrics.append({'target': 'salary_min', 'MAE': mae, 'RMSE': rmse, 'R2': r2})
        print(f"📉 MAE (salary_min): £{mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.3f}")

        if not df_min_missing.empty:
            preds_min = model_min.predict(tfidf.transform(df_min_missing['text']))
            df.loc[df['salary_min'].isna(), 'predicted_salary_min'] = preds_min
    else:
        print("⚠️ No training data for salary_min")

    # ----- salary_max -----
    df_max_train = df[df['salary_max'].notna()]
    df_max_missing = df[df['salary_max'].isna()]
    model_max_path = os.path.join(model_dir, 'model_salary_max.joblib')

    if not df_max_train.empty:
        X_max_train = tfidf.transform(df_max_train['text'])
        y_max_train = df_max_train['salary_max']

        if os.path.exists(model_max_path):
            model_max = joblib.load(model_max_path)
        else:
            model_max = RandomForestRegressor(n_estimators=100, random_state=42)
            model_max.fit(X_max_train, y_max_train)
            joblib.dump(model_max, model_max_path)

        X_eval, X_test, y_eval, y_test = train_test_split(X_max_train, y_max_train, test_size=0.2, random_state=42)
        y_pred = model_max.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        metrics.append({'target': 'salary_max', 'MAE': mae, 'RMSE': rmse, 'R2': r2})
        print(f"📉 MAE (salary_max): £{mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.3f}")

        if not df_max_missing.empty:
            preds_max = model_max.predict(tfidf.transform(df_max_missing['text']))
            df.loc[df['salary_max'].isna(), 'predicted_salary_max'] = preds_max
    else:
        print("⚠️ No training data for salary_max")

    # ----- Save metrics -----
    pd.DataFrame(metrics).to_csv(metrics_path, index=False)

    # ----- Update database -----
    updated = df[(df['predicted_salary_min'].notna()) | (df['predicted_salary_max'].notna())]
    with engine.begin() as conn:
        for _, row in updated.iterrows():
            update_data = {
                "job_id": int(row["job_id"]),
                "predicted_salary_min": row.get("predicted_salary_min"),
                "predicted_salary_max": row.get("predicted_salary_max"),
            }
            update_fields = []
            if pd.notna(update_data["predicted_salary_min"]):
                update_fields.append("predicted_salary_min = :predicted_salary_min")
            if pd.notna(update_data["predicted_salary_max"]):
                update_fields.append("predicted_salary_max = :predicted_salary_max")

            if update_fields:
                query_str = f"""
                    UPDATE jobs
                    SET {', '.join(update_fields)}
                    WHERE job_id = :job_id
                """
                conn.execute(text(query_str), update_data)

    print("✅ Prediction and DB update complete.")
