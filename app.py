import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import random
import time
from prototype_classifier import SupportAgentMock

# Initialize the shared mock classifier
if "agent_classifier" not in st.session_state:
    st.session_state.agent_classifier = SupportAgentMock()

# Mock categories
CATEGORIES = [
    "Order Tracking", "Refund Requests", "Delivery Delays", 
    "Product Complaints", "Payment Failures", "Subscription Issues", 
    "General Questions"
]

# Set page config
st.set_page_config(page_title="Beastlife Support Pulse", layout="wide", page_icon="🦁")

st.title("🦁 Beastlife Support Intelligence")
st.markdown("Real-time AI-driven customer care analytics dashboard.")

# Simulated Database/Logs
if "logs" not in st.session_state:
    st.session_state.logs = []
    # Seed with some initial data
    for i in range(150):
        # Weighted random choice to reflect initial percentage
        cat = random.choices(
            CATEGORIES, 
            weights=[35, 22, 18, 10, 8, 5, 2], 
            k=1
        )[0]
        t_offset = random.randint(0, 7200)
        st.session_state.logs.append({"id": i + 1, "category": cat, "timestamp": time.time() - t_offset})

# Layout: Stats at the top
st.subheader("Live Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Queries Today", len(st.session_state.logs))


# Calculate current percentages
df = pd.DataFrame(st.session_state.logs)
counts = df['category'].value_counts()
highest_cat = counts.idxmax()

col2.metric("Most Common Issue", highest_cat)
col3.metric("Automation Success Rate", "68.2%", delta="1.5%")
# Dynamic Spike Calculation
current_time = time.time()
recent_1h = df[df['timestamp'] > current_time - 3600]
prev_1h = df[(df['timestamp'] <= current_time - 3600) & (df['timestamp'] > current_time - 7200)]

spike_issue = "No Spikes"
spike_delta = "Normal"
d_color = "normal"

if not recent_1h.empty and not prev_1h.empty:
    recent_counts = recent_1h['category'].value_counts()
    prev_counts = prev_1h['category'].value_counts()
    
    max_spike_pct = 0
    max_spike_cat = None
    
    for c in recent_counts.index:
        c_recent = recent_counts[c]
        c_prev = prev_counts.get(c, 0)
        if c_prev > 0:
            increase = ((c_recent - c_prev) / c_prev) * 100
        else:
            increase = c_recent * 100
            
        if increase > max_spike_pct:
            max_spike_pct = increase
            max_spike_cat = c
            
    if max_spike_cat and max_spike_pct > 30:  # Threshold for spike alert
        spike_issue = max_spike_cat
        spike_delta = f"{int(max_spike_pct)}% (Last 1h)"
        d_color = "inverse"

col4.metric("Spike Alert", spike_issue, delta=spike_delta, delta_color=d_color)

st.divider()

# Layout: Dashboard charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Issue Distribution")
    # Interactive Pie Chart using matplotlib
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        counts.values, 
        labels=counts.index, 
        autopct='%1.1f%%', 
        startangle=140,
        textprops=dict(color="w")
    )
    plt.setp(autotexts, size=10, weight="bold")
    # Beautiful styling
    ax.legend(wedges, counts.index,
              title="Categories",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    st.pyplot(fig)

with col_right:
    st.subheader("Simulate New Query")
    
    with st.form("query_form"):
        new_query = st.text_area("Customer Query:", "I want a refund for my damaged product.")
        submitted = st.form_submit_button("Submit to AI Classifier")
        
        if submitted:
            # Use the imported SupportAgent for classification
            new_cat = st.session_state.agent_classifier.classify(new_query)
            
            st.success(f"**AI Classification Result:** {new_cat}")
            
            # Log it
            next_id = max([log["id"] for log in st.session_state.logs]) + 1 if st.session_state.logs else 1
            st.session_state.logs.append({"id": next_id, "category": new_cat, "timestamp": time.time()})
            st.rerun()

st.divider()
st.subheader("Recent Automated Actions Log")
# Display all accumulated logs, reversed (newest first)
recent_df = df.iloc[::-1].reset_index(drop=True)
action_mapping = {
    "Order Tracking": "API call to FedEx > Auto-Replied to Customer",
    "Refund Requests": "Triggered Stripe Refund API > Sent Return Label",
    "Delivery Delays": "Flagged Logistics > Sent Apology Email",
    "Product Complaints": "Escalated to Tier-2 Agent (High Priority)",
    "Payment Failures": "Checked Gateway Logs > Sent Retry Link",
    "Subscription Issues": "Checked Sub Status > Modified Billing Cycle",
    "General Questions": "Searched Knowledge Base > RAG Output Generated"
}

recent_df["Automated Action Taken"] = recent_df["category"].map(action_mapping)
st.dataframe(recent_df[["id", "category", "Automated Action Taken"]], width='stretch')
