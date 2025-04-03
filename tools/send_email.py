import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email_with_attachment(receiver_email, subject, body, file_path):
    sender_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not password:
        return "❌ Email credentials missing in .env file"

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(body)

    # Attach the file
    with open(file_path, 'rb') as f:
        file_data = f.read()
        filename = os.path.basename(file_path)
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(msg)
        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Failed to send email: {e}"
