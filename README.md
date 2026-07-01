# 🧠 Company Brain — AI-Powered Product & Customer Analytics

> **Live Demo:** [company-brain-ybnweiv4yuajaemcflqhws.streamlit.app](https://company-brain-ybnweiv4yuajaemcflqhws.streamlit.app/)

An end-to-end analytics platform that makes company operations **queryable in plain English**. Built to simulate how modern product and SaaS companies monitor customer health, product usage, and revenue — with an AI layer that lets anyone ask business questions without writing SQL.

---

## The Business Problem

Product and customer success teams struggle to get fast answers from operational data scattered across support tickets, CRM systems, product event logs, and meeting notes. This project simulates that environment and solves it with a unified analytics layer + natural language querying.

**Business questions this dashboard answers:**
- Which customers are at risk of churning — and what's the revenue impact?
- Which product features drive the most engagement?
- Which support ticket categories take the longest to resolve?
- Which industries have the highest churn rates?
- Which high-value customers have unresolved critical tickets right now?

---

## Architecture

```
Mock Data Generation (Python + Faker)
        ↓
Snowflake Cloud Data Warehouse
        ↓
Business SQL Layer (CTEs, Window Functions, CASE Statements)
        ↓
Streamlit Dashboard + Plotly Charts
        ↓
AI Natural Language Query Layer (Groq + Llama 3.3)
```

---

## Features

### 📊 Analytics Dashboard
- **KPI Metrics** — Total customers, active customers, churn rate, MRR, open tickets
- **Churn Risk Breakdown** — Active customers segmented by risk level (High / Medium / Low) based on ticket volume, satisfaction scores, and product engagement
- **MRR by Plan** — Revenue distribution across Free, Starter, Pro, and Enterprise tiers
- **Feature Adoption** — Which product features are used most and by how many customers
- **Ticket Trends** — Support ticket volume by category and priority
- **Churn by Industry** — Which industries have the highest customer loss rates
- **Meeting Outcomes** — Win/loss patterns across customer touchpoints

### 🤖 AI Query Layer
- Type any business question in plain English
- Llama 3.3 (via Groq) generates the SQL query automatically
- Query runs live against Snowflake and returns results instantly
- Auto-generates bar charts for two-column result sets

**Example questions you can ask:**
- *"Which customers churned last quarter?"*
- *"Show me Enterprise customers with unresolved critical tickets"*
- *"What is the average resolution time by ticket category?"*
- *"Which features are used by the most customers?"*
- *"What is total MRR at risk from high-risk customers?"*

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data Generation | Python, Faker |
| Cloud Data Warehouse | Snowflake |
| Data Loading | Python, snowflake-connector-python |
| SQL Analysis | Snowflake SQL (CTEs, CASE, aggregations, JOINs) |
| AI / NL Query | Groq API, Llama 3.3 70B |
| Dashboard | Streamlit, Plotly |
| Deployment | Streamlit Cloud |
| Version Control | GitHub |

---

## Dataset

Realistic mock data generated with Python's Faker library:

| Table | Rows | Description |
|---|---|---|
| customers | 200 | Company accounts with plan, MRR, industry, status |
| tickets | 500 | Support tickets with category, priority, resolution time, satisfaction |
| meetings | 150 | Customer meetings with type, outcome, action items |
| events | 2,000 | Product usage events across features and platforms |

---

## Key SQL Concepts Used

- `CTEs` (Common Table Expressions) for churn risk segmentation
- `CASE WHEN` for multi-condition classification
- `JOINs` across customers, tickets, and events
- `GROUP BY` with aggregations for trend analysis
- `DATE_TRUNC` for time-series analysis
- `UNION ALL` for multi-table result sets

---

## Run Locally

```bash
# Clone the repo
git clone https://github.com/kpooja2597/company-brain.git
cd company-brain

# Set up virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your credentials
mkdir .streamlit
# Create .streamlit/secrets.toml with your Snowflake + Groq keys

# Run the app
streamlit run app.py
```

---

## Project Structure

```
company-brain/
├── app.py                        # Main Streamlit dashboard
├── pages/
│   └── 1_AI_Query.py             # AI natural language query page
├── data/
│   ├── customers.csv
│   ├── tickets.csv
│   ├── meetings.csv
│   └── events.csv
├── sql/
│   └── business_queries.sql      # Core business SQL queries
├── generate_data.py              # Mock data generation script
├── load_to_snowflake.py          # Snowflake data loader
├── requirements.txt
└── .gitignore
```

---

## Skills Demonstrated

`Python` `SQL` `Snowflake` `Data Modeling` `ETL Pipeline` `Business Analytics` `Data Visualization` `AI/LLM Integration` `Streamlit` `Plotly` `Natural Language to SQL` `Customer Analytics` `Churn Analysis` `Product Analytics`

---