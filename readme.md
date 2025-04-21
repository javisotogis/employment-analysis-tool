# Labor Market Analysis of Data Roles in the United Kingdom

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

## 🧱 SQL Database Schema

The relational database is structured to support efficient querying and analysis. Below is an overview of the main tables and their relationships:

### `job_postings` Table

| Column Name         | Data Type   | Description                                |
|---------------------|-------------|--------------------------------------------|
| job_uuid            | UUID        | Unique identifier for the job posting      |
| company_uuid        | UUID        | Foreign key referencing the `companies` table |
| job_title           | VARCHAR     | Name of the job position                   |
| job_description     | TEXT        | Detailed description of the job role       |
| location            | VARCHAR     | Free-text location of the job              |
| latitude            | DECIMAL     | Geographical latitude                      |
| longitude           | DECIMAL     | Geographical longitude                     |
| job_type_uuid       | UUID        | Foreign key referencing `job_types` table  |
| city_uuid           | UUID        | Foreign key referencing `cities` table     |
| country             | VARCHAR     | Country (typically 'UK')                   |
| salary_min          | NUMERIC     | Minimum salary offered                     |
| salary_max          | NUMERIC     | Maximum salary offered                     |
| estimated_salary    | BOOLEAN     | Whether the salary is an estimate          |

---

### `companies` Table

| Column Name     | Data Type | Description                  |
|-----------------|-----------|------------------------------|
| company_uuid    | UUID      | Unique identifier for company |
| company_name    | VARCHAR   | Name of the company           |

---

### `cities` Table

| Column Name   | Data Type | Description                   |
|---------------|-----------|-------------------------------|
| city_uuid     | UUID      | Unique identifier for the city |
| city_name     | VARCHAR   | Name of the city               |

---

### `job_types` Table

| Column Name     | Data Type | Description                    |
|-----------------|-----------|--------------------------------|
| job_type_uuid   | UUID      | Unique identifier for job type  |
| job_type_name   | VARCHAR   | Name of the job type (e.g., Full-time, Contract) |

---

## 📊 Final Deliverables

- ETL pipeline for automated data extraction and storage
- SQL database with normalized job market data
- Interactive dashboard (Power BI / Streamlit)
- Documentation for future maintenance and scalability

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repository and submit a pull request.

---

## 📄 License

MIT License. See `LICENSE.md` for more information.
