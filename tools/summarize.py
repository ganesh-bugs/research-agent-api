import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


from transformers import pipeline

# Load once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    print("🧠 Summarizing using Hugging Face model...")

    # Trim if too long
    trimmed_text = text[:1024]

    # Calculate max_length intelligently
    input_length = len(trimmed_text.split())
    max_len = min(130, int(input_length * 0.8))
    max_len = max(max_len, 20)  # Never less than 20 tokens

    summary = summarizer(trimmed_text, max_length=max_len, min_length=20, do_sample=False)
    return summary[0]['summary_text']
