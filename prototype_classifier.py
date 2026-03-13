# prototype_classifier.py
# This script demonstrates the NLP and automation pipeline.

import os
from collections import Counter
import pandas as pd

# In a real environment, you would use:
# import google.generativeai as genai
# model = genai.GenerativeModel('gemini-1.5-flash')

class SupportAgentMock:
    """
    Mocks the Gemini API setup for classification.
    """
    def __init__(self):
        self.categories = [
            "Order Tracking", "Delivery Delays", "Refund Requests", 
            "Product Complaints", "Subscription Issues", 
            "Payment Failures", "General Questions"
        ]
        print("SupportAgent initialized with categories:", self.categories)

    def classify(self, query: str) -> str:
        # Mocking LLM behavior using keyword heuristics
        # In production this would be: return llm.predict(...)
        q_low = query.lower()
        if "where" in q_low and ("order" in q_low or "package" in q_low):
            return "Order Tracking"
        if "deduct" in q_low or "payment" in q_low or "charged" in q_low:
            return "Payment Failures"
        if "refund" in q_low:
            return "Refund Requests"
        if "damaged" in q_low or "broken" in q_low or "bad" in q_low:
            return "Product Complaints"
        if "late" in q_low or "delay" in q_low:
            return "Delivery Delays"
        if "subscribe" in q_low or "subscription" in q_low:
            return "Subscription Issues"
        
        return "General Questions"

    def execute_automation(self, category: str, extracted_entities: dict):
        print(f"Executing automation for category: [{category}]")
        if category == "Order Tracking":
            print(" -> [Action] Fetching from Db/FedEx...")
        elif category == "Refund Requests":
            print(" -> [Action] Checking refund eligibility (30-day window)...")
            print(" -> [Action] Triggering payment gateway refund...")
        elif category == "Delivery Delays":
            print(" -> [Action] Notifying logistics and sending apology email...")
        elif category == "Product Complaints":
            print(" -> [Action] Escalating ticket to human support rep via Zendesk...")
        elif category == "Payment Failures":
            print(" -> [Action] Verifying transaction logs...")
            print(" -> [Action] Emailing secure payment retry link...")
        else:
            print(" -> [Action] Generating standard informational response...")


def run_pipeline(queries):
    agent = SupportAgentMock()
    print("="*40)
    print("Beastlife Analytics Pipeline Starting...")
    print("="*40)
    
    logs = []
    
    for i, query in enumerate(queries):
        print(f"\nProcessing Query #{i+1}: '{query}'")
        
        # 1. Classify Intent
        category = agent.classify(query)
        print(f" -> Predicted Category: {category}")
        
        # 2. Extract Entities (Mocked here)
        entities = {"customer_id": "CUST_123", "order_id": f"ORD_{8000+i}"}
        
        # 3. Automation Layer
        agent.execute_automation(category, entities)
        
        # 4. Log to DB
        logs.append({"id": entities["order_id"], "query": query, "category": category})

    print("\n" + "="*40)
    print("Analytics Output generated:")
    print("="*40)
    
    # 5. Calculate Metrics
    df = pd.DataFrame(logs)
    counts = df['category'].value_counts()
    total = len(df)
    
    print("\nIssue Percentage Distribution (Sample Size = {}):".format(total))
    for cat, count in counts.items():
        pct = (count / total) * 100
        print(f"- {cat}: {pct:.1f}%")

if __name__ == "__main__":
    sample_queries = [
        "Where is my order? I've been waiting for 2 weeks.",
        "My payment was deducted but order not placed.",
        "I want a refund for my last purchase. It doesn't fit.",
        "The product arrived damaged.",
        "How do I cancel my monthly protein subscription?",
        "Where can I find the tracking number for package?",
        "Why is my delivery late?",
        "Payment failed but it charged my card.",
        "Could I get a refund please?",
        "The flavor is really bad, I want to file a complaint."
    ]
    
    run_pipeline(sample_queries)
