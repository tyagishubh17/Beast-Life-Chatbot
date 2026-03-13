# Beastlife AI Customer Care Automation System

## 1. Query Understanding
The first stage involves ingesting customer queries across multiple channels (email, chat, tickets) and using Natural Language Processing (NLP) to parse the text, identify intent, and extract relevant entities (e.g., Order ID, Product Name, Customer Name).

- **Input:** Raw text from customer queries.
- **NLP Processing:** 
  - Tokenization and stop-word removal.
  - Named Entity Recognition (NER) to extract Order IDs, email addresses, etc.
  - Intent classification to understand the core reason for the query.

**Example Queries & Intent Extraction:**
- *"Where is my order?":* Intent = Order Status, Entity = None (needs fallback to user profile).
- *"My payment was deducted but order not placed.":* Intent = Payment Failure, Entity = None.
- *"I want a refund for my last purchase.":* Intent = Refund Request, Entity = Last Purchase (linked to DB).
- *"The product arrived damaged.":* Intent = Product Complaint, Entity = Product Condition (Damaged).

## 2. Problem Classification
Once the query is understood, an AI classifier categorizes it into predefined buckets. A fine-tuned Small Language Model (SLM) like Llama-3-8B or an API-based LLM (e.g., OpenAI GPT-4o-mini) works best for high accuracy and context understanding.

**Categories:**
- Order Tracking
- Delivery Delays
- Refund Requests
- Product Complaints
- Subscription Issues
- Payment Failures
- General Product Questions

## 3. Automation Layer
After classification, the system routes the query to an automated workflow:
- **Order Tracking:** Trigger an API call to the logistics provider (e.g., FedEx, UPS) using the extracted Order ID. Auto-respond with the current status and tracking link.
- **Delivery Delay:** Automatically notify the logistics partner, flag the order in the internal system, and send a proactive, apologetic email to the customer with an updated ETA.
- **Refund Request:** Check eligibility (e.g., within 30 days of purchase). If eligible, trigger the Stripe/PayPal refund workflow and initiate a return shipping label generation.
- **Product Complaint:** High priority. Escalate immediately to a human Tier-2 support agent via Zendesk/Intercom with all context pre-filled.
- **Payment Failure:** Check Stripe/payment gateway logs. Send an automated email with a secure retry checkout link.

## 4. Analytics & Intelligence
All processed queries are logged into a centralized database (e.g., PostgreSQL) to compute key metrics:
- Percentage distribution of each issue type.
- Most common problems (e.g., "Size too small" under Product Complaints).
- Trend analysis over time to identify systemic issues (e.g., a specific batch of products causing complaints).
- Daily / weekly spikes alerting the team.

**Example Weekly Output:**
- Order Tracking: 35%
- Refund Requests: 22%
- Delivery Delays: 18%
- Product Complaints: 10%
- Payment Failures: 8%
- Subscription Issues: 5%
- General Questions: 2%

## 5. Dashboard
A visual dashboard built for the customer support management team.
- **Pie Chart:** Real-time distribution of issue types.
- **Time Series Trend Chart:** Line chart showing the volume of complaints over the last 30 days to spot anomalies.
- **Most Common Queries:** A word cloud or top-10 list of exact phrases or keywords.
- **Automation Success Rate:** Percentage of queries resolved without human intervention (Target: >60%).
- **Alerts Panel:** Flashing indicators for sudden volume spikes (e.g., a 200% increase in Payment Failures indicating a Stripe integration issue).

## 6. Technical Architecture
A modern, scalable cloud-native stack:

- **Data Ingestion Pipeline:** Webhooks from Zendesk/Shopify/Email provider ingested via **AWS API Gateway + Lambda** or **FastAPI**.
- **NLP Model Choice:** 
  - *Zero-shot Classification:* Google Gemini Flash API (`gemini-2.5-flash`) for rapid prototyping.
  - *Production alternative:* Fine-tuned **HuggingFace** model (e.g., `distilbert-base-uncased` fine-tuned on past tickets) for lower latency and cost.
- **Backend System:** **Python (FastAPI)** for microservices orchestrating the workflow.
- **Database Structure:** **PostgreSQL** for relational data (Orders, Users, Tickets) and **Redis** for fast cache and rate-limiting.
- **Dashboard Framework:** **Streamlit** for rapid prototyping and internal tools, progressing to **React/Next.js + Recharts** or **Tableau** for enterprise-scale.
- **Orchestration:** **LangChain** or **Google AI Studio / Vertex AI** to build the AI Agent workflow.

## 7. AI Workflow Pipeline

1. **Customer Query:** User sends a message via email/chat.
2. **NLP Processing:** System cleans text, handles spelling errors, and extracts entities.
3. **Intent Classification:** LLM categorizes the message into one of the predefined categories.
4. **Automation Decision:** A rule engine (or LangChain Agent) decides the next best action based on category + extracted entities.
5. **Response Generation:** Draft an empathetic, context-aware response using an LLM.
6. **Data Logging:** Store metadata (timestamp, category, sentiment) in PostgreSQL.
7. **Analytics Dashboard:** Streamlit app queries the DB to refresh visuals.

## 8. Prototype Implementation

Below are sample code snippets demonstrating the core logic of the prototype. **(See `classifier.py` and `app.py` for actual Python files.)**

### A. Query Classification (using Google Gemini API)
```python
import os
import google.generativeai as genai

# Configure the Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

categories = [
    "Order Tracking", "Delivery Delays", "Refund Requests", 
    "Product Complaints", "Subscription Issues", 
    "Payment Failures", "General Product Questions"
]

def classify_query(query: str):
    prompt = f"""You are a customer support triage AI for the brand 'Beastlife'.
Classify the following customer query into exactly ONE of the following categories:
{", ".join(categories)}

Query: "{query}"
Category:"""
    
    response = model.generate_content(prompt)
    return response.text.strip()

# Example usage
print(classify_query("Where is my order?")) 
# Output: Order Tracking
```

### B. Issue Percentage Calculation & Data Logging
```python
import pandas as pd

# Simulated database log of today's queries
ticket_logs = [
    {"id": 1, "category": "Order Tracking"},
    {"id": 2, "category": "Refund Requests"},
    {"id": 3, "category": "Order Tracking"},
    {"id": 4, "category": "Delivery Delays"},
    {"id": 5, "category": "Product Complaints"},
]

def calculate_distribution(logs):
    df = pd.DataFrame(logs)
    counts = df['category'].value_counts()
    percentages = (counts / len(df)) * 100
    return percentages.to_dict()

distribution = calculate_distribution(ticket_logs)
for cat, pct in distribution.items():
    print(f"{cat}: {pct:.1f}%")
```

### C. Dashboard Visualization (using Streamlit)
```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Beastlife Support Intelligence")

data = {
    "Category": ["Order Tracking", "Refund Requests", "Delivery Delays", "Product Complaints", "Payment Failures", "Subscription Issues", "General Questions"],
    "Percentage": [35, 22, 18, 10, 8, 5, 2]
}
df = pd.DataFrame(data)

st.subheader("Issue Distribution")
fig, ax = plt.subplots()
ax.pie(df["Percentage"], labels=df["Category"], autopct='%1.1f%%', startangle=90)
ax.axis('equal') 
st.pyplot(fig)
```

## 9. Scalability Suggestions
To transition this prototype to handle tens of thousands of daily queries:

1. **Message Queuing:** Introduce **Kafka** or **RabbitMQ** between the data ingestion webhook and the processing layer to ensure no messages are lost during high traffic or LLM API outages.
2. **Model Optimization:** Transition from generalized LLMs (like Gemini Pro) to a fine-tuned small model (e.g., DistilBERT or Llama-3-8B fine-tuned for classification) deployed via **AWS SageMaker** or **vLLM**. This drastically reduces inference latency and AI API costs.
3. **Caching & Deduplication:** Implement **Redis** to cache identical queries or rate-limit repetitive automated spam.
4. **Vector Database:** For complex QA (e.g., General Product Questions), implement a **RAG (Retrieval-Augmented Generation)** architecture using **Pinecone** or **Milvus** indexed with your product knowledge base, enabling grounded, hallucination-free responses.
5. **Horizontal Scaling:** Deploy the FastAPI and background worker services using **Kubernetes (EKS/GKE)** with auto-scaling rules based on queue depth to dynamically handle traffic spikes (e.g., Black Friday sales).
