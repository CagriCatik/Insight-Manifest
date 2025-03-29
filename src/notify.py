import os
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuration
THRESHOLD = 80.0

# Read the Excel file (adjust path and sheet name as needed)
df = pd.read_excel("test_coverage.xlsx", sheet_name="Coverage", index_col=0)

# Compute the overall average coverage
average_coverage = df.mean().mean()
print(f"Average Coverage: {average_coverage:.2f}%")

if average_coverage < THRESHOLD:
    # Prepare email content
    subject = "Test Coverage Alert"
    body = (
        f"Warning: The average test coverage is {average_coverage:.2f}%, "
        f"which is below the threshold of {THRESHOLD}%."
    )
    message = MIMEMultipart()
    message["From"] = os.environ["EMAIL_SENDER"]
    message["To"] = os.environ["EMAIL_RECIPIENT"]
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Email server configuration
        smtp_server = os.environ["EMAIL_HOST"]
        smtp_port = int(os.environ.get("EMAIL_PORT", 587))
        smtp_username = os.environ["EMAIL_USERNAME"]
        smtp_password = os.environ["EMAIL_PASSWORD"]

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
            print("Email notification sent.")
    except Exception as e:
        print("Failed to send email notification.")
        print(str(e))
else:
    print("Coverage is above threshold. No email notification sent.")
