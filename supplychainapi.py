from fastapi import FastAPI
import requests
from pydantic import BaseModel
import spacy
import os
from dotenv import load_dotenv

# Load API Keys
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

app = FastAPI()
nlp = spacy.load("en_core_web_sm")  # Load NLP Model

class RiskAnalysisResponse(BaseModel):
    source: str
    title: str
    risk_score: float
    summary: str

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc?query=supply%20chain&mode=artlist&format=json"
KEYWORDS = ["strike", "shortage", "disruption", "protest", "inflation", "embargo"]

@app.get("/analyze_risks", response_model=list[RiskAnalysisResponse])
def analyze_risks():
    articles = fetch_serpapi_data() + fetch_gdelt_data()
    print("Fetched Articles:", articles)  # Debugging

    risk_reports = []
    for article in articles:
        title = article.get("title", "")
        description = article.get("summary", "")
        risk_score = calculate_risk_score(title + " " + description)
        risk_reports.append(RiskAnalysisResponse(
            source=article.get("source", "Unknown"),
            title=title,
            risk_score=risk_score,
            summary=description if description else "Summary not available"
        ))

    print("Generated Risk Reports:", risk_reports)  # Debugging
    return risk_reports

def fetch_serpapi_data():
    """Fetch news articles from SerpAPI."""
    url = f"https://serpapi.com/search.json?engine=google_news&q=supply+chain+disruptions&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json().get("news_results", [])
        return [{
            "source": article.get("source", {}).get("name", "Google News"),
            "title": article.get("title", ""),
            "summary": article.get("snippet", "")
        } for article in news_data]
    
    print("SerpAPI Response Error:", response.text)  # Debugging
    return []  # Return empty list instead of None

def fetch_gdelt_data():
    """Fetch global event data from GDELT."""
    response = requests.get(GDELT_URL)
    
    if response.status_code == 200:
        gdelt_articles = response.json().get("articles", [])
        return [{
            "source": "GDELT",
            "title": article.get("title", ""),
            "summary": article.get("snippet", "")
        } for article in gdelt_articles]
    
    print("GDELT Response Error:", response.text)  # Debugging
    return []  # Return empty list instead of None

def calculate_risk_score(text):
    """Uses NLP to assign a risk score based on keywords."""
    doc = nlp(text.lower())
    score = sum(1 for token in doc if token.text in KEYWORDS) / len(KEYWORDS)
    return round(score * 10, 2)  # Normalize to a 0-10 scale

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
