init_db()

import streamlit as st
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import pandas as pd
from tools.search_articles import search_articles
from tools.summarize import summarize_text
from tools.save_to_excel import save_articles_to_excel
from tools.pdf_utils import download_pdf, extract_text_from_pdf
from tools.send_email import send_email_with_attachment
from tools.memory import init_db, save_memory, get_memory


st.set_page_config(page_title="AI Research Agent", layout="centered")
st.title("📚 AI Research Assistant")
st.markdown("Search research papers, summarize them, and receive a report by email.")

# 🔤 Input: topic
topic = st.text_input("🔍 Enter a research topic:")

# 🔢 Input: number of results
num_results = st.number_input("📄 How many articles to fetch?", min_value=1, max_value=100, value=5, step=1)

# 📬 Input: email address (before running agent)
st.markdown("### 📬 Where should we send your report?")
recipient_email = st.text_input("Enter recipient email address")

# ▶️ Button to run the agent
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

            for i, article in enumerate(articles):
                title = article.get("title")
                snippet = article.get("snippet", "")
                link = article.get("link")

                st.write(f"📄 **{i+1}. {title}**")
                st.write(f"🔗 {link}")

                summary = ""
                used_pdf = False

                # 📥 Try downloading PDF
                pdf_path = download_pdf(link, save_path=f"temp_article_{i}.pdf")
                if pdf_path:
                    full_text = extract_text_from_pdf(pdf_path)

                    if full_text and len(full_text) > 500:
                        st.write("🧠 Summarizing full paper...")
                        summary = summarize_text(full_text[:3000])
                        used_pdf = True
                    else:
                        st.write("⚠️ PDF was empty or too short. Using snippet.")

                    os.remove(pdf_path)
                else:
                    st.write("❌ No PDF found. Using snippet.")

                # 🧠 Fallback to snippet
                if not used_pdf:
                    summary = summarize_text(snippet)

                processed_articles.append({
                    "Title": title,
                    "Snippet": snippet,
                    "Summary": summary,
                    "Link": link,
                    "Used Full PDF": "Yes" if used_pdf else "No"
                })

            # 💾 Save to Excel
            output_file = "research_results.xlsx"
            save_articles_to_excel(processed_articles, output_file)
            st.session_state["output_file"] = output_file

            st.success("✅ Summary complete. Report ready.")

            pdf_count = sum(1 for a in processed_articles if a["Used Full PDF"] == "Yes")
            save_memory(topic, len(processed_articles), pdf_count)


            # ⬇️ Download button
            with open(output_file, "rb") as f:
                st.download_button("⬇️ Download Excel", data=f, file_name=output_file)

            # ✉️ Auto-send email
            if recipient_email:
                subject = f"Your AI Research Report on '{topic}'"
                body = "Attached is your research summary report."
                email_status = send_email_with_attachment(recipient_email, subject, body, output_file)
                st.info(email_status)
            else:
                st.warning("Email was not sent because no address was entered.")

if st.checkbox("🧠 View Agent Memory"):
    memory = get_memory()
    if memory:
        st.markdown("### 🔂 Previous Sessions")
        for row in memory:
            st.markdown(f"- **{row[1][:19]}** | 🔍 Topic: _{row[2]}_ | 📄 {row[3]} articles | 📥 PDFs used: {row[4]}")
    else:
        st.info("No memory yet.")
