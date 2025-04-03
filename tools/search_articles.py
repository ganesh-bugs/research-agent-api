import os
import requests
from dotenv import load_dotenv
import math

load_dotenv()

def search_articles(query, max_results=10):
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("❌ Missing SerpAPI key. Please add it to your .env file.")
        return []

    url = "https://serpapi.com/search"
    articles = []
    results_per_page = 10
    total_pages = math.ceil(max_results / results_per_page)

    for page in range(total_pages):
        start = page * results_per_page
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": api_key,
            "start": start
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"❌ SerpAPI error: {response.status_code}")
            break

        data = response.json()
        results = data.get("organic_results", [])
        if not results:
            break  # No more results

        for res in results:
            if len(articles) >= max_results:
                break

            pdf_link = None

            # ✅ Prefer PDF from resources if available
            if "resources" in res:
                for r in res["resources"]:
                    if r.get("file_format") == "PDF":
                        pdf_link = r.get("link")
                        break

            # Add to list
            articles.append({
                "title": res.get("title"),
                "link": pdf_link or res.get("link"),
                "snippet": res.get("snippet", "")
            })

    return articles
