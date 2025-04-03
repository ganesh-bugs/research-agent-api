import streamlit as st
import os
from tools.search_articles import search_articles
from tools.summarize import summarize_text
from tools.save_to_excel import save_articles_to_excel
from tools.pdf_utils import download_pdf, extract_text_from_pdf, extract_abstract_from_pdf
from tools.send_email import send_email_with_attachment
from tools.memory import init_db, save_memory, get_memory

st.set_page_config(page_title="AI Research Agent", layout="centered")
st.title("📚 AI Research Assistant")
st.markdown("Search, summarize, and get research reports via email.")

init_db()

topic = st.text_input("🔍 Enter a research topic:")
num_results = st.number_input("📄 How many articles to fetch?", min_value=1, max_value=100, value=5, step=1)
st.markdown("### 📬 Where should we send your report?")
recipient_email = st.text_input("Enter recipient email address")

if st.button("Run Agent"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        st.info("🔍 Searching Google Scholar...")
        articles = search_articles(topic, max_results=num_results)

        if not articles:
            st.error("No articles found.")
        else:
            st.success(f"Found {len(articles)} articles. Summarizing...")
            processed_articles = []
            pdf_count = 0

            for i, article in enumerate(articles):
                title = article.get("title")
                snippet = article.get("snippet", "")
                link = article.get("link")

                st.write(f"📄 **{i+1}. {title}**")
                st.write(f"🔗 {link}")

                summary = ""
                used_pdf = False
                abstract = ""

                pdf_path = download_pdf(link, save_path=f"temp_article_{i}.pdf")
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

                processed_articles.append({
                    "Title": title,
                    "Link": link,
                    "Abstract": abstract,
                    "Snippet": snippet,
                    "Summary": summary,
                    "Used Full PDF": "Yes" if used_pdf else "No"
                })

            output_file = "research_results.xlsx"
            save_articles_to_excel(processed_articles, output_file)
            st.session_state["output_file"] = output_file

            st.success("✅ Summary complete. Report ready.")

            with open(output_file, "rb") as f:
                st.download_button("⬇️ Download Excel", data=f, file_name=output_file)

            if recipient_email:
                subject = f"Your AI Research Report on '{topic}'"
                body = "Attached is your research summary report."
                email_status = send_email_with_attachment(recipient_email, subject, body, output_file)
                st.info(email_status)
            else:
                st.warning("Email was not sent because no address was entered.")

            save_memory(topic, len(processed_articles), pdf_count)

if st.checkbox("🧠 View Agent Memory"):
    memory = get_memory()
    if memory:
        st.markdown("### 🔂 Previous Sessions")
        for row in memory:
            st.markdown(f"- **{row[1][:19]}** | 🔍 Topic: _{row[2]}_ | 📄 {row[3]} articles | 📥 PDFs used: {row[4]}")
    else:
        st.info("No memory yet.")
