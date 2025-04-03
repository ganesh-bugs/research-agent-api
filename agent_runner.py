from tools.search_articles import search_articles
from tools.summarize import summarize_text
from tools.save_to_excel import save_articles_to_excel
from tools.pdf_utils import download_pdf, extract_text_from_pdf, extract_abstract_from_pdf
from tools.send_email import send_email_with_attachment
from tools.memory import init_db, save_memory
import os

# CONFIG
EMAIL = "ganesh.bugs@gmail.com"  # Replace with your actual email
NUM_ARTICLES = 5

def run_agent():
    init_db()

    # ✅ Ask user for topic
    topic = input("📌 Enter the research topic: ").strip()
    if not topic:
        print("❌ No topic entered. Exiting.")
        return

    articles = search_articles(topic, max_results=NUM_ARTICLES)
    if not articles:
        print("❌ No articles found.")
        return

    processed = []
    pdf_count = 0

    for i, a in enumerate(articles):
        title = a.get("title")
        link = a.get("link")
        snippet = a.get("snippet", "")
        abstract = ""
        summary = ""
        used_pdf = False

        pdf_path = download_pdf(link, save_path=f"auto_{i}.pdf")
        if pdf_path:
            full_text = extract_text_from_pdf(pdf_path)
            if full_text and len(full_text) > 500:
                abstract = extract_abstract_from_pdf(full_text) or snippet
                summary = summarize_text(full_text[:3000])
                used_pdf = True
                pdf_count += 1
            else:
                abstract = snippet
                summary = summarize_text(snippet)
            os.remove(pdf_path)
        else:
            abstract = snippet
            summary = summarize_text(snippet)

        processed.append({
            "Title": title,
            "Link": link,
            "Abstract": abstract,
            "Snippet": snippet,
            "Summary": summary,
            "Used Full PDF": "Yes" if used_pdf else "No"
        })

    output_file = "automated_report.xlsx"
    save_articles_to_excel(processed, output_file)
    save_memory(topic, len(processed), pdf_count)

    send_email_with_attachment(
        EMAIL,
        subject=f"[AUTO] Research Report on '{topic}'",
        body="Attached is your automated research summary.",
        file_path=output_file
    )

    print(f"✅ Report created and emailed for topic: {topic}")

if __name__ == "__main__":
    run_agent()
