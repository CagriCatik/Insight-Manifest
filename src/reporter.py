# test_coverage_project/reporter.py
import os
import logging
import subprocess
import jinja2
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

def generate_latex_report(df, image_path, output_dir="report", template_path="templates/report_template.tex", output_filename="report.tex"):
    """
    Generate a LaTeX report including data summary, a heatmap, and an inline table.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(template_path, "r") as f:
            template_content = f.read()
    except Exception as e:
        logger.exception("Failed to load LaTeX template: %s", e)
        raise
    
    template = jinja2.Template(template_content)
    
    # Create summary statistics and inline table in LaTeX format
    summary = df.describe().to_latex()
    inline_table = df.to_latex()
    
    rendered = template.render(
        title="Test Coverage Report",
        summary=summary,
        image_path=image_path,
        inline_table=inline_table
    )
    
    report_path = os.path.join(output_dir, output_filename)
    with open(report_path, "w") as f:
        f.write(rendered)
    logger.info("LaTeX report generated at %s", report_path)
    
    return report_path

def compile_latex_report(report_path):
    """
    Compile the LaTeX report to PDF using pdflatex.
    """
    try:
        cmd = ["pdflatex", "-interaction=nonstopmode", report_path]
        subprocess.run(cmd, check=True)
        logger.info("LaTeX report compiled successfully.")
    except FileNotFoundError as fnf_error:
        logger.error("pdflatex executable not found. Make sure it is installed and on your PATH.")
        raise fnf_error
    except subprocess.CalledProcessError as cpe:
        logger.exception("Error compiling LaTeX report: %s", cpe)
        raise cpe

def export_report_to_html(report_path):
    """
    Convert the LaTeX report to HTML using pandoc.
    """
    html_path = report_path.replace(".tex", ".html")
    try:
        cmd = ["pandoc", report_path, "-s", "-o", html_path]
        subprocess.run(cmd, check=True)
        logger.info("Report exported to HTML at %s", html_path)
    except subprocess.CalledProcessError as e:
        logger.exception("Error exporting report to HTML: %s", e)
        raise

def send_email_notification(subject, body, attachment_path=None):
    """
    Send an email notification with an optional attachment.
    Adjust SMTP server, port, sender, and recipient as needed.
    """
    # Configure these values or load them from configuration/environment
    SMTP_SERVER = "smtp.example.com"
    SMTP_PORT = 587
    SMTP_USER = "sender@example.com"
    SMTP_PASSWORD = "yourpassword"
    SENDER_EMAIL = "sender@example.com"
    RECIPIENT_EMAIL = "recipient@example.com"
    
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg.set_content(body)
    
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as f:
                file_data = f.read()
            # Assuming attachment is a PDF
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=os.path.basename(attachment_path))
            logger.info("Attached file %s to email.", attachment_path)
        except Exception as e:
            logger.exception("Error attaching file: %s", e)
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)
            logger.info("Email sent successfully to %s", RECIPIENT_EMAIL)
    except Exception as e:
        logger.exception("Failed to send email: %s", e)
        raise
