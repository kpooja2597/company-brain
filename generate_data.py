import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

# --- Config ---
NUM_CUSTOMERS = 200
NUM_TICKETS = 500
NUM_MEETINGS = 150
NUM_EVENTS = 2000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

def random_date(start=START_DATE, end=END_DATE):
    return start + timedelta(days=random.randint(0, (end - start).days))

# --- 1. Customers ---
plans = ["Free", "Starter", "Pro", "Enterprise"]
industries = ["Fintech", "Healthcare", "Retail", "SaaS", "Logistics", "Education"]
statuses = ["Active", "Churned", "Trial"]

customers = []
for i in range(NUM_CUSTOMERS):
    signup = random_date()
    plan = random.choices(plans, weights=[30, 30, 25, 15])[0]
    status = random.choices(statuses, weights=[60, 25, 15])[0]
    customers.append({
        "customer_id": f"CUST{i+1:04d}",
        "company_name": fake.company(),
        "industry": random.choice(industries),
        "plan": plan,
        "status": status,
        "signup_date": signup.date(),
        "mrr": {"Free": 0, "Starter": 49, "Pro": 149, "Enterprise": 499}[plan],
        "country": random.choices(["US", "UK", "Canada", "India"], weights=[60, 15, 15, 10])[0],
        "account_manager": fake.name()
    })

customers_df = pd.DataFrame(customers)
customers_df.to_csv("data/customers.csv", index=False)
print(f"✓ customers.csv — {len(customers_df)} rows")

# --- 2. Support Tickets ---
categories = ["Bug", "Feature Request", "Billing", "Onboarding", "Performance", "Integration"]
priorities = ["Low", "Medium", "High", "Critical"]
ticket_statuses = ["Open", "In Progress", "Resolved", "Closed"]

tickets = []
for i in range(NUM_TICKETS):
    cust = random.choice(customers)
    created = random_date()
    resolved_days = random.randint(1, 20)
    status = random.choices(ticket_statuses, weights=[15, 20, 40, 25])[0]
    tickets.append({
        "ticket_id": f"TKT{i+1:05d}",
        "customer_id": cust["customer_id"],
        "category": random.choice(categories),
        "priority": random.choices(priorities, weights=[30, 40, 20, 10])[0],
        "status": status,
        "created_date": created.date(),
        "resolved_date": (created + timedelta(days=resolved_days)).date() if status in ["Resolved", "Closed"] else None,
        "resolution_days": resolved_days if status in ["Resolved", "Closed"] else None,
        "satisfaction_score": random.randint(1, 5) if status in ["Resolved", "Closed"] else None,
        "subject": fake.sentence(nb_words=6)
    })

tickets_df = pd.DataFrame(tickets)
tickets_df.to_csv("data/tickets.csv", index=False)
print(f"✓ tickets.csv — {len(tickets_df)} rows")

# --- 3. Meetings ---
meeting_types = ["Demo", "Onboarding", "QBR", "Support Call", "Upsell", "Churn Risk Review"]
outcomes = ["Positive", "Neutral", "Negative", "Follow-up Required"]

meetings = []
for i in range(NUM_MEETINGS):
    cust = random.choice(customers)
    date = random_date()
    meetings.append({
        "meeting_id": f"MTG{i+1:04d}",
        "customer_id": cust["customer_id"],
        "meeting_type": random.choice(meeting_types),
        "date": date.date(),
        "duration_mins": random.choice([30, 45, 60, 90]),
        "outcome": random.choices(outcomes, weights=[40, 30, 15, 15])[0],
        "attendees": random.randint(2, 6),
        "action_items": random.randint(0, 5),
        "notes_summary": fake.paragraph(nb_sentences=3)
    })

meetings_df = pd.DataFrame(meetings)
meetings_df.to_csv("data/meetings.csv", index=False)
print(f"✓ meetings.csv — {len(meetings_df)} rows")

# --- 4. Product Events ---
event_types = ["Login", "Feature_A_Used", "Feature_B_Used", "Report_Generated",
               "Integration_Connected", "Dashboard_Viewed", "Export_Downloaded", "Invite_Sent"]

events = []
for i in range(NUM_EVENTS):
    cust = random.choice(customers)
    events.append({
        "event_id": f"EVT{i+1:06d}",
        "customer_id": cust["customer_id"],
        "event_type": random.choice(event_types),
        "event_date": random_date().date(),
        "session_duration_secs": random.randint(30, 3600),
        "platform": random.choices(["Web", "Mobile", "API"], weights=[60, 25, 15])[0]
    })

events_df = pd.DataFrame(events)
events_df.to_csv("data/events.csv", index=False)
print(f"✓ events.csv — {len(events_df)} rows")

print("\nAll data generated successfully in /data folder.")