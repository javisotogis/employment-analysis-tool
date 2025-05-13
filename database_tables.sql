CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL UNIQUE
);
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    location_name TEXT NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);
CREATE TABLE jobs (
    job_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    predicted_salary_min NUMERIC,
    predicted_salary_max NUMERIC,
    redirect_url TEXT,
    created TIMESTAMP,
    source TEXT,
    
    company_id INTEGER REFERENCES companies(company_id),
    location_id INTEGER REFERENCES locations(location_id),
    job_level_id INTEGER REFERENCES job_levels(job_level_id)
);
CREATE TABLE job_metadata (
    metadata_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(job_id) ON DELETE CASCADE,
    search_query TEXT,
    search_location TEXT,
    date_downloaded DATE
);
CREATE TABLE job_levels (
    job_level_id SERIAL PRIMARY KEY,
    level_name TEXT NOT NULL UNIQUE
);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_metadata_query ON job_metadata(search_query);
