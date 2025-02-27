import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/analyze_risks"  

st.title("📊 Supply Chain Risk Dashboard")

st.write("Fetching real-time risk reports...")

# Fetch data from FastAPI backend
response = requests.get(API_URL)
if response.status_code == 200:
    risk_reports = response.json()
    
    if risk_reports:
        for report in risk_reports:
            st.subheader(f"🔴 {report['title']}")
            st.write(f"**Source:** {report['source']}")
            st.write(f"**Risk Score:** {report['risk_score']} / 10")
            st.write(f"**Summary:** {report['summary']}")
            st.markdown("---")
    else:
        st.write("✅ No major risks detected.")
else:
    st.error("❌ Failed to fetch risk reports. Check API server.")

