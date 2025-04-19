# streamlit_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---- Paste your JSON data here ----
data = {
    "report": """Based on the provided context, here's an analysis of user feedback related to security cameras:

**Wyze Cam:** Users appreciate the affordability of Wyze cameras. They are considered a cheap security option for monitoring doors and providing phone notifications. 

**Ring:** Users generally express satisfaction with Ring cameras, highlighting fast delivery and easy setup. The Ring app is also praised. Picture quality is considered good, though not exceptional, especially when used behind windows. Users find the cameras make them feel more secure. The long power cord is a plus. The 180-day trial period for recordings is well-received, even by those intending to purchase a subscription.

**General Security System Feedback:** Some users are concerned about data privacy and security vulnerabilities. Facial recognition is a key feature, with users noting its surprising accuracy. However, the functionality within the app is considered basic and lacking in customization, particularly regarding notifications and actions tied to specific individuals. Users appreciate systems that don't require cloud storage and data sharing. The cost of subscriptions is a factor, with users valuing trial periods to assess the necessity of paid features. Some users want more control over which events trigger alerts (e.g., avoiding alerts for neighbors).""",
    "metrics": [
        {
            "title": "Ring Camera Review Count",
            "value": 2,
            "description": "Number of reviews specifically mentioning Ring cameras."
        },
        {
            "title": "Wyze Camera Mentions",
            "value": 2,
            "description": "Number of times Wyze cameras are mentioned."
        },
        {
            "title": "Ring Camera 4-Star Reviews",
            "value": 2,
            "description": "Number of 4-star reviews for Ring cameras."
        }
    ],
    "sentiments": {
        "description": "Overall sentiment distribution in the provided feedback related to security cameras.",
        "positive": 75,
        "neutral": 25,
        "negative": 0
    },
    "key_themes": [
        "Affordability (Wyze)",
        "Ease of Setup (Ring)",
        "Facial Recognition Functionality",
        "Data Privacy",
        "Subscription Necessity"
    ]
}

st.set_page_config(page_title="Market Research Dashboard", layout="wide")

st.title("🔍 Product Insights Dashboard")

# 1) Report
st.header("Report")
st.markdown(data["report"])

# 2) Metrics
st.header("Key Metrics")
df_metrics = pd.DataFrame(data["metrics"])
df_metrics = df_metrics.rename(columns={"title": "Metric", "value": "Value", "description": "Description"})
st.table(df_metrics)

# 3) Sentiment Distribution
st.header("Sentiment Distribution")
sent = data["sentiments"]
labels = ["Positive", "Neutral", "Negative"]
values = [sent["positive"], sent["neutral"], sent["negative"]]

fig, ax = plt.subplots()
ax.bar(labels, values)
ax.set_ylabel("Count / Percentage")
ax.set_title(sent["description"])
st.pyplot(fig)

# 4) Key Themes
st.header("Key Themes")
for theme in data["key_themes"]:
    st.markdown(f"- **{theme}**")