import pandas as pd

def save_articles_to_excel(articles, filename="research_results.xlsx"):
    df = pd.DataFrame(articles)
    df.to_excel(filename, index=False)
    return f"✅ Results saved to {filename}"
