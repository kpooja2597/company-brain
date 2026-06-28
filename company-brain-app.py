import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(
    page_title="Company Brain",
    page_icon="🧠",
    layout="wide"
)

# --- Snowflake Connection ---
@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

@st.cache_data(ttl=300)
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

# --- Header ---
st.title("🧠 Company Brain")
st.caption("AI-powered product & customer analytics dashboard")
st.divider()

# --- KPI Metrics ---
customers_df   = run_query("SELECT * FROM customers")
tickets_df     = run_query("SELECT * FROM tickets")
events_df      = run_query("SELECT * FROM events")
meetings_df    = run_query("SELECT * FROM meetings")

total_customers = len(customers_df)
active          = len(customers_df[customers_df["STATUS"] == "Active"])
churned         = len(customers_df[customers_df["STATUS"] == "Churned"])
churn_rate      = round(churned / total_customers * 100, 1)
total_mrr       = customers_df["MRR"].sum()
open_tickets    = len(tickets_df[tickets_df["STATUS"].isin(["Open", "In Progress"])])

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Customers", total_customers)
col2.metric("Active Customers", active)
col3.metric("Churn Rate", f"{churn_rate}%")
col4.metric("Total MRR", f"${total_mrr:,}")
col5.metric("Open Tickets", open_tickets)

st.divider()

# --- Row 1: Churn Risk + MRR by Plan ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Churn Risk Breakdown")
    churn_risk_df = run_query("""
        WITH ticket_summary AS (
            SELECT customer_id,
                   COUNT(*) AS total_tickets,
                   AVG(satisfaction_score) AS avg_satisfaction
            FROM tickets GROUP BY customer_id
        ),
        event_summary AS (
            SELECT customer_id, COUNT(*) AS total_events
            FROM events GROUP BY customer_id
        )
        SELECT
            CASE
                WHEN ts.total_tickets > 5 AND ts.avg_satisfaction < 3 AND es.total_events < 10 THEN 'High Risk'
                WHEN ts.total_tickets > 3 AND ts.avg_satisfaction < 4 THEN 'Medium Risk'
                ELSE 'Low Risk'
            END AS churn_risk,
            COUNT(*) AS customers,
            SUM(c.mrr) AS mrr_at_risk
        FROM customers c
        LEFT JOIN ticket_summary ts ON c.customer_id = ts.customer_id
        LEFT JOIN event_summary es  ON c.customer_id = es.customer_id
        WHERE c.status = 'Active'
        GROUP BY churn_risk
    """)
    fig = px.pie(
        churn_risk_df, values="CUSTOMERS", names="CHURN_RISK",
        color="CHURN_RISK",
        color_discrete_map={"High Risk": "#ef4444", "Medium Risk": "#f59e0b", "Low Risk": "#22c55e"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("MRR by Plan")
    mrr_df = run_query("""
        SELECT plan, SUM(mrr) AS total_mrr, COUNT(*) AS customers
        FROM customers WHERE status = 'Active'
        GROUP BY plan ORDER BY total_mrr DESC
    """)
    fig2 = px.bar(
        mrr_df, x="PLAN", y="TOTAL_MRR", text="TOTAL_MRR",
        color="PLAN", color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig2.update_traces(texttemplate="$%{text:,}", textposition="outside")
    fig2.update_layout(showlegend=False, yaxis_title="MRR ($)")
    st.plotly_chart(fig2, use_container_width=True)

# --- Row 2: Feature Adoption + Ticket Categories ---
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("Feature Adoption")
    feature_df = run_query("""
        SELECT event_type, COUNT(*) AS total_events,
               COUNT(DISTINCT customer_id) AS unique_customers
        FROM events GROUP BY event_type ORDER BY total_events DESC
    """)
    fig3 = px.bar(
        feature_df, x="TOTAL_EVENTS", y="EVENT_TYPE",
        orientation="h", color="UNIQUE_CUSTOMERS",
        color_continuous_scale="Blues", labels={"EVENT_TYPE": "Feature", "TOTAL_EVENTS": "Total Uses"}
    )
    fig3.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig3, use_container_width=True)

with col_right2:
    st.subheader("Tickets by Category & Priority")
    ticket_cat_df = run_query("""
        SELECT category, priority, COUNT(*) AS total
        FROM tickets GROUP BY category, priority ORDER BY total DESC
    """)
    fig4 = px.bar(
        ticket_cat_df, x="CATEGORY", y="TOTAL", color="PRIORITY",
        barmode="stack",
        color_discrete_map={"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#22c55e"}
    )
    fig4.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig4, use_container_width=True)

# --- Row 3: Churn by Industry + Meeting Outcomes ---
col_left3, col_right3 = st.columns(2)

with col_left3:
    st.subheader("Churn Rate by Industry")
    churn_ind_df = run_query("""
        SELECT industry,
               COUNT(*) AS total,
               SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END) AS churned,
               ROUND(SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) AS churn_rate
        FROM customers GROUP BY industry ORDER BY churn_rate DESC
    """)
    fig5 = px.bar(
        churn_ind_df, x="INDUSTRY", y="CHURN_RATE",
        color="CHURN_RATE", color_continuous_scale="Reds",
        labels={"CHURN_RATE": "Churn Rate (%)"}
    )
    st.plotly_chart(fig5, use_container_width=True)

with col_right3:
    st.subheader("Meeting Outcomes")
    outcome_df = run_query("""
        SELECT outcome, COUNT(*) AS total
        FROM meetings GROUP BY outcome ORDER BY total DESC
    """)
    fig6 = px.pie(
        outcome_df, values="TOTAL", names="OUTCOME",
        color="OUTCOME",
        color_discrete_map={
            "Positive": "#22c55e", "Neutral": "#3b82f6",
            "Negative": "#ef4444", "Follow-up Required": "#f59e0b"
        }
    )
    st.plotly_chart(fig6, use_container_width=True)

# --- Footer ---
st.divider()
st.caption("Built with Python · Snowflake · Streamlit | Company Brain Portfolio Project")