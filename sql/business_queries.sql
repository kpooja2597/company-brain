-- ============================================================
-- COMPANY BRAIN — Business SQL Queries
-- Database: company_brain | Schema: analytics
-- ============================================================

USE DATABASE company_brain;
USE SCHEMA analytics;


-- ------------------------------------------------------------
-- 1. CUSTOMER OVERVIEW
-- How many customers per plan, and what's the total MRR?
-- ------------------------------------------------------------
SELECT
    plan,
    status,
    COUNT(*)            AS customer_count,
    SUM(mrr)            AS total_mrr,
    ROUND(AVG(mrr), 2)  AS avg_mrr
FROM customers
GROUP BY plan, status
ORDER BY total_mrr DESC;


-- ------------------------------------------------------------
-- 2. CHURN RATE BY INDUSTRY
-- Which industries are losing the most customers?
-- ------------------------------------------------------------
SELECT
    industry,
    COUNT(*)                                                        AS total_customers,
    SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END)            AS churned,
    ROUND(SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END)
          / COUNT(*) * 100, 1)                                      AS churn_rate_pct
FROM customers
GROUP BY industry
ORDER BY churn_rate_pct DESC;


-- ------------------------------------------------------------
-- 3. SUPPORT TICKET TRENDS
-- What categories take the longest to resolve?
-- ------------------------------------------------------------
SELECT
    category,
    priority,
    COUNT(*)                            AS total_tickets,
    ROUND(AVG(resolution_days), 1)      AS avg_resolution_days,
    ROUND(AVG(satisfaction_score), 2)   AS avg_satisfaction
FROM tickets
WHERE status IN ('Resolved', 'Closed')
GROUP BY category, priority
ORDER BY avg_resolution_days DESC;


-- ------------------------------------------------------------
-- 4. HIGH-VALUE CUSTOMERS WITH OPEN CRITICAL TICKETS
-- Which Enterprise/Pro customers have unresolved critical issues?
-- Useful for: customer success prioritization
-- ------------------------------------------------------------
SELECT
    c.customer_id,
    c.company_name,
    c.plan,
    c.mrr,
    COUNT(t.ticket_id) AS open_critical_tickets
FROM customers c
JOIN tickets t
    ON c.customer_id = t.customer_id
WHERE t.priority = 'Critical'
  AND t.status IN ('Open', 'In Progress')
  AND c.plan IN ('Enterprise', 'Pro')
GROUP BY c.customer_id, c.company_name, c.plan, c.mrr
ORDER BY c.mrr DESC, open_critical_tickets DESC;


-- ------------------------------------------------------------
-- 5. PRODUCT FEATURE ADOPTION
-- Which features are most/least used?
-- ------------------------------------------------------------
SELECT
    event_type,
    COUNT(*)                        AS total_events,
    COUNT(DISTINCT customer_id)     AS unique_customers,
    ROUND(AVG(session_duration_secs) / 60, 1) AS avg_session_mins
FROM events
GROUP BY event_type
ORDER BY total_events DESC;


-- ------------------------------------------------------------
-- 6. CHURN RISK SIGNALS
-- Customers who are Active but show warning signs:
-- high ticket volume + low satisfaction + low product usage
-- ------------------------------------------------------------
WITH ticket_summary AS (
    SELECT
        customer_id,
        COUNT(*)                            AS total_tickets,
        ROUND(AVG(satisfaction_score), 2)   AS avg_satisfaction
    FROM tickets
    GROUP BY customer_id
),
event_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS total_events
    FROM events
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.company_name,
    c.plan,
    c.mrr,
    c.industry,
    ts.total_tickets,
    ts.avg_satisfaction,
    es.total_events,
    CASE
        WHEN ts.total_tickets > 5 AND ts.avg_satisfaction < 3 AND es.total_events < 10
            THEN 'High Risk'
        WHEN ts.total_tickets > 3 AND ts.avg_satisfaction < 4
            THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS churn_risk
FROM customers c
LEFT JOIN ticket_summary ts ON c.customer_id = ts.customer_id
LEFT JOIN event_summary es  ON c.customer_id = es.customer_id
WHERE c.status = 'Active'
ORDER BY c.mrr DESC;


-- ------------------------------------------------------------
-- 7. MONTHLY MEETING OUTCOMES
-- Are customer meetings trending positive or negative?
-- ------------------------------------------------------------
SELECT
    DATE_TRUNC('month', date)       AS month,
    meeting_type,
    outcome,
    COUNT(*)                        AS meeting_count
FROM meetings
GROUP BY month, meeting_type, outcome
ORDER BY month, meeting_count DESC;


-- ------------------------------------------------------------
-- 8. REVENUE AT RISK
-- Total MRR from churned customers by plan
-- ------------------------------------------------------------
SELECT
    plan,
    COUNT(*)    AS churned_customers,
    SUM(mrr)    AS lost_mrr
FROM customers
WHERE status = 'Churned'
GROUP BY plan
ORDER BY lost_mrr DESC;