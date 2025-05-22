# Labor Market Analysis of Data Roles in the United Kingdom

# Deliverable 1

## 📌 Business Case Description

In recent years, data-related roles have seen accelerated growth in the job market. Companies across all industries are increasingly seeking professionals proficient in data analysis, statistics, and visualization tools. However, both job seekers and employers face challenges in understanding which skills are most in demand, what salary ranges are offered, and how job availability varies by region or industry.

This project is envisioned as a **market intelligence solution**: a deep analysis of job postings related to data analysis, data science, and other related roles published on UK platforms. The goal is to offer clear and updated insights to aid decision-making for:

- 🎯 Professionals looking to develop or redirect their careers.
- 🧠 Recruitment teams wanting to understand salary and technology trends.
- 🎓 Educational institutions aiming to adapt their programs to market needs.

---

## 🎯 Project Objectives & Expected Impact

### Objectives

1. Extract and process job vacancy data related to data roles in the UK from online job portals.
2. Clean, transform, and normalize data for meaningful analysis.
3. Identify key patterns: most requested technologies, soft skills, geographic distribution, salary ranges, and contract types.
4. Create interactive dashboards for exploring labor market trends.

### Expected Impact

- Gain insight into the evolution and demand for data analyst roles in the UK.
- Support the design of training programs based on actual market needs.
- Help professionals better prepare for high-potential job applications.
- Provide valuable insights for recruitment agencies to shape hiring strategies.

---

## 🛠️ Technologies and Tools

### ETL & Data Processing
- **Python** (`pandas`, `geopandas`, `requests`, `psycopg2`)
- **SQL** (SQLite or PostgreSQL) for structured storage

### Visualization
- **Power BI** or **Streamlit** for dashboard creation

### Management & Documentation
- **Git / GitHub** for version control and collaboration

---

## 🔗 Data Sources: Identification & Justification

The project will leverage multiple job platforms and APIs to gather data:

| API           | Description                                         | Auth    | HTTPS | CORS     |
|---------------|-----------------------------------------------------|---------|--------|----------|
| Adzuna        | Job board aggregator                                | apiKey  | Yes    | Unknown  |
| Arbeitnow     | Job board in Europe / Remote                        | No      | Yes    | Yes      |
| DevITjobs UK  | UK tech jobs via GraphQL                            | No      | Yes    | Yes      |
| Findwork      | Job board                                           | apiKey  | Yes    | Unknown  |
| Reed          | Job board aggregator                                | apiKey  | Yes    | Unknown  |
| Careerjet     | Job search engine                                   | apiKey  | No     | Unknown  |
| Jooble        | Job search engine                                   | apiKey  | Yes    | Unknown  |
| WhatJobs      | Job search engine                                   | apiKey  | Yes    | Unknown  |
| GraphQL Jobs  | Jobs using GraphQL                                  | No      | Yes    | Yes      |
| Others        | Additional sources like Upwork, USAJobs, The Muse   | Mixed   | Yes    | Varies   |

**Justification**:  
These platforms are selected for their frequency of updates, broad coverage (national and sometimes global), and richness of unstructured data (e.g., job descriptions, skill requirements). Their accessible APIs also allow seamless integration into ETL pipelines.

---

# Deliverable 2

## Project Description

This deliverable documents the complete **ETL (Extract, Transform, Load)** process applied to job data retrieved from two free public APIs: **Adzuna** and **Reed**. The goal is to unify, enrich, and store job listings in a structured format for further analysis and use.

---

## 1. Data Extraction (Extract)

Data was retrieved from the public APIs of **Adzuna** and **Reed**, which provide information about job vacancies across different regions and sectors.

---

## 2. Data Transformation (Transform)

After extraction, the following data transformation steps were performed:

- **Standardization**: Data from both APIs was standardized and merged into a single **DataFrame**.
- **Salary Prediction**: Machine learning techniques in **Python** were used to predict missing salary values. The model was trained using:
  - The **job description**
  - The **known salary** (when available)
  - The **job title**
- **Job Categorization**: Job descriptions were analyzed to categorize positions based on the presence of specific **keywords** in the text.
- **Duplicate Check**: The ETL script includes a validation step to ensure no duplicate records are inserted into the database.
- **Location API Filtering**: The location-enrichment API only processes **new and non-duplicate** location entries, improving efficiency and avoiding redundancy.

---

## 3. Data Loading (Load)

The transformed data is loaded into a relational **PostgreSQL** database. The database schema includes the following tables:

- `jobs`: Main table containing job listing information.
- `job_levels`: Table with information on job seniority or level.
- `locations`: Table with geographic location data.
- `keywords`: Table with the most frequently occurring keywords from job descriptions.

---

## Conclusion

This ETL pipeline automates the integration and enrichment of job data from multiple sources, resulting in a clean, structured database that is ready for advanced analysis such as visualization, clustering, or job-market intelligence applications.


## Database Schema

The PostgreSQL database consists of the following tables and relationships:

---

### 🏢 `companies`

Stores unique company information.

| Column Name   | Data Type | Description                  |
|---------------|-----------|------------------------------|
| company_id    | SERIAL    | Primary key                  |
| company_name  | TEXT      | Company name (unique, not null) |

---

### 📍 `locations`

Stores geographic information for job listings.

| Column Name   | Data Type   | Description                      |
|---------------|-------------|----------------------------------|
| location_id   | SERIAL      | Primary key                      |
| location_name | TEXT        | Name of the location (not null) |
| latitude      | DECIMAL(9,6)| Latitude coordinate              |
| longitude     | DECIMAL(9,6)| Longitude coordinate             |

---

### 💼 `jobs`

Main table containing job listing details.

| Column Name          | Data Type | Description                                  |
|----------------------|-----------|----------------------------------------------|
| job_id               | SERIAL    | Primary key                                  |
| title                | TEXT      | Job title (not null)                         |
| description          | TEXT      | Job description                              |
| salary_min           | NUMERIC   | Minimum salary (if available)                |
| salary_max           | NUMERIC   | Maximum salary (if available)                |
| predicted_salary_min | NUMERIC   | Predicted minimum salary                     |
| predicted_salary_max | NUMERIC   | Predicted maximum salary                     |
| redirect_url         | TEXT      | URL to the original job post                 |
| created              | TIMESTAMP | Job creation date                            |
| source               | TEXT      | Source API (e.g., Adzuna or Reed)            |
| company_id           | INTEGER   | Foreign key → `companies(company_id)`        |
| location_id          | INTEGER   | Foreign key → `locations(location_id)`       |
| job_level_id         | INTEGER   | Foreign key → `job_levels(job_level_id)`     |

**Indexes:**

- `idx_jobs_title` on `title`

---

### 📋 `job_metadata`

Stores metadata related to the search and retrieval process.

| Column Name     | Data Type | Description                                  |
|------------------|-----------|----------------------------------------------|
| metadata_id      | SERIAL    | Primary key                                  |
| job_id           | INTEGER   | Foreign key → `jobs(job_id)` (cascade delete)|
| search_query     | TEXT      | Original search query used                   |
| search_location  | TEXT      | Location string used in the query            |
| date_downloaded  | DATE      | Date when the job data was retrieved         |

**Indexes:**

- `idx_metadata_query` on `search_query`

---

### 📊 `job_levels`

Stores predefined job seniority levels.

| Column Name | Data Type | Description                          |
|-------------|-----------|--------------------------------------|
| job_level_id| SERIAL    | Primary key                          |
| level_name  | TEXT      | Job level name (unique, not null)    |


# Deliverable 3: Power BI Dashboard for Job Analytics

As part of Deliverable 2, a comprehensive Power BI dashboard was developed to analyze data from the PostgreSQL job database.

The dashboard connects directly to the SQL database and presents multiple perspectives on the job market data using clean visuals and interactive filters.

---

## 📊 Dashboard Structure

The Power BI report contains **four main pages** (tabs), each focusing on a different analytical aspect of the data:

1. **Salary Analysis**  
   - Visual breakdowns of minimum, maximum, and predicted salaries.
   - Allows comparison by job levels or across time.

2. **Job Titles**  
   - Highlights the most common job titles.
   - Helps identify demand trends and role clustering.

3. **Job Locations**  
   - Maps and charts showing where jobs are concentrated.
   - Includes geolocation support via latitude and longitude fields.

4. **Companies**  
   - Provides insights into which companies are posting the most jobs.
   - Useful for identifying top hiring organizations.

---

## ⚙️ Data Source

- The dashboard uses live or imported data from the PostgreSQL database.
- Tables used include: `jobs`, `companies`, `locations`, `job_levels`, and `job_metadata`.

---

## 🎯 Purpose

The goal of this deliverable is to enable quick, intuitive exploration of the job market data and to support data-driven insights without writing queries manually.

---

## 📁 File

The final `.pbix` file is included in this repository (or can be provided upon request).



# Deliverable 4: JobBot - AI-Powered Job Database Assistant

This project is part of **Deliverable 3** for the Data Analytics portfolio.

## 🤖 About JobBot

**JobBot** is a local AI-powered chatbot that answers questions about job listings stored in a PostgreSQL database. It uses a locally hosted large language model (LLM) to interpret natural language questions, translate them into SQL, execute the queries, and return meaningful results — all from your own database.

And in case something goes wrong... it blames humanity 😈

---

## 🧠 Features

- **Natural language interface**: Ask questions like “What’s the highest paid job?” or “Show me 10 jobs in London”.
- **LLM-powered**: Uses [Mistral-7B-Instruct](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF) running locally with `llama-cpp-python`.
- **PostgreSQL integration**: Queries your custom job listings database.
- **Streamlit UI**: Clean, interactive web interface.
- **Skynet-style error handling**: When something breaks, the AI returns ironic and darkly humorous messages in Spanish.

---

## 💾 Requirements

- Python 3.8+
- Conda or virtual environment
- CPU with enough RAM to run quantized LLM models

### Python packages:

```bash
pip install -r requirements.txt


---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repository and submit a pull request.

---

## 📄 License

MIT License. See `LICENSE.md` for more information.
