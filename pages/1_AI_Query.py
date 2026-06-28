import streamlit as st
import snowflake.connector
import pandas as pd
from groq import Groq

st.set_page_config(page_title="AI Query", page_icon="🤖", layout="wide")

# --- Clients ---
groq_client = Groq(api_key=st.secrets["groq"]["api_key"])

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

def run_query(sql):
    conn = get_connection()
    return pd.read_sql(sql, conn)

# --- Schema Context for GPT ---
SCHEMA = """
You are a data analyst assistant. Convert the user's business question into a Snowflake SQL query.
Only return the SQL query — no explanation, no markdown, no code blocks.

Database: company_brain
Schema: analytics

Tables:

customers (
    customer_id     VARCHAR,   -- unique customer ID e.g. CUST0001
    company_name    VARCHAR,
    industry        VARCHAR,   -- Fintech, Healthcare, Retail, SaaS, Logistics, Education
    plan            VARCHAR,   -- Free, Starter, Pro, Enterprise
    status          VARCHAR,   -- Active, Churned, Trial
    signup_date     DATE,
    mrr             NUMBER,    -- monthly recurring revenue in dollars
    country         VARCHAR,
    account_manager VARCHAR
)

tickets (
    ticket_id           VARCHAR,
    customer_id         VARCHAR,
    category            VARCHAR,   -- Bug, Feature Request, Billing, Onboarding, Performance, Integration
    priority            VARCHAR,   -- Low, Medium, High, Critical
    status              VARCHAR,   -- Open, In Progress, Resolved, Closed
    created_date        DATE,
    resolved_date       DATE,
    resolution_days     NUMBER,
    satisfaction_score  NUMBER,    -- 1 to 5
    subject             VARCHAR
)

meetings (
    meeting_id      VARCHAR,
    customer_id     VARCHAR,
    meeting_type    VARCHAR,   -- Demo, Onboarding, QBR, Support Call, Upsell, Churn Risk Review
    date            DATE,
    duration_mins   NUMBER,
    outcome         VARCHAR,   -- Positive, Neutral, Negative, Follow-up Required
    attendees       NUMBER,
    action_items    NUMBER,
    notes_summary   VARCHAR
)

events (
    event_id              VARCHAR,
    customer_id           VARCHAR,
    event_type            VARCHAR,   -- Login, Feature_A_Used, Feature_B_Used, Report_Generated,
                                     -- Integration_Connected, Dashboard_Viewed, Export_Downloaded, Invite_Sent
    event_date            DATE,
    session_duration_secs NUMBER,
    platform              VARCHAR    -- Web, Mobile, API
)
"""

def generate_sql(question):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SCHEMA},
            {"role": "user",   "content": question}
        ],
        temperature=0
    )
    sql = response.choices[0].message.content.strip()
    if sql.startswith("```"):
        sql = sql.split("```")[1]
        if sql.startswith("sql"):
            sql = sql[3:]
    return sql.strip()

# --- UI ---
st.title("🤖 Ask Your Data")
st.caption("Type a business question in plain English — the AI will query your Snowflake data and return the answer.")

st.divider()

# Example questions
st.markdown("**Try asking:**")
cols = st.columns(3)
examples = [
    "Which industries have the highest churn rate?",
    "Show me Enterprise customers with unresolved critical tickets",
    "What is the total MRR by plan for active customers?",
    "Which features are used by the most customers?",
    "What are the top 5 customers by MRR?",
    "Show average resolution days by ticket category"
]
for i, ex in enumerate(examples):
    if cols[i % 3].button(ex, key=f"ex_{i}"):
        st.session_state["question"] = ex

st.divider()

question = st.text_input(
    "Your question:",
    value=st.session_state.get("question", ""),
    placeholder="e.g. Which customers churned last quarter?"
)

if question:
    with st.spinner("Thinking..."):
        try:
            sql = generate_sql(question)

            with st.expander("Generated SQL", expanded=True):
                st.code(sql, language="sql")

            df = run_query(sql)

            st.success(f"Returned {len(df)} rows")
            st.dataframe(df, use_container_width=True)

            # Auto-chart if 2 columns returned
            if len(df.columns) == 2:
                col_names = df.columns.tolist()
                try:
                    import plotly.express as px
                    fig = px.bar(df, x=col_names[0], y=col_names[1])
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

        except Exception as e:
            st.error(f"Something went wrong: {e}")