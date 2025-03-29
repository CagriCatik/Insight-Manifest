# main.py

import logging
from logging.handlers import RotatingFileHandler
from tqdm import tqdm

import data_loader
import plotter
import reporter

def setup_logging():
    """Configure logging with console and rotating file handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    
    # Console handler for INFO level and above
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # Rotating file handler for DEBUG level
    fh = RotatingFileHandler("project.log", maxBytes=10*1024*1024, backupCount=5)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

def load_email_config(config):
    """Extract the email configuration from the full config."""
    return config.get("email", {})

def main():
    # Define the steps for our progress bar
    steps = [
        "Load configuration",
        "Load Excel data",
        "Generate heatmap",
        "Generate LaTeX report",
        "Compile report to PDF",
        "Export report to HTML",
        "Send email notification"
    ]
    
    with tqdm(total=len(steps), desc="Processing", unit="step") as pbar:
        # Step 1: Load configuration
        config = data_loader.load_config("config/config.yaml")
        pbar.set_postfix_str("Configuration loaded")
        pbar.update(1)
        
        # Step 2: Load data from Excel
        df = data_loader.read_excel_file(config["excel_file"], config["sheet_name"])
        pbar.set_postfix_str("Excel data loaded")
        pbar.update(1)
        
        # Step 3: Create heatmap plot
        plotter.create_heatmap(df, config["heatmap_output"])
        pbar.set_postfix_str("Heatmap generated")
        pbar.update(1)
        
        # Step 4: Generate LaTeX report
        report_path = reporter.generate_latex_report(
            df,
            image_path=config["heatmap_output"],
            output_dir=config["report_output_dir"],
            template_path=config["latex_template"],
            output_filename=config["report_filename"]
        )
        pbar.set_postfix_str("LaTeX report generated")
        pbar.update(1)
        
        # Step 5: Compile the report to PDF
        try:
            reporter.compile_latex_report(report_path)
        except Exception as e:
            logger.error("Compilation failed: %s", e)
            pbar.set_postfix_str("Compilation failed")
            return
        pbar.set_postfix_str("Report compiled")
        pbar.update(1)
        
        # Step 6: Export the report to HTML
        reporter.export_report_to_html(report_path)
        pbar.set_postfix_str("Report exported to HTML")
        pbar.update(1)
        
        # Step 7: Send email notification with the PDF attached
        email_config = load_email_config(config)
        pdf_attachment = report_path.replace(".tex", ".pdf")
        subject = "Test Coverage Report"
        body = "The latest test coverage report has been generated and is attached."
        reporter.send_email_notification(
            subject=subject,
            body=body,
            to_emails=email_config.get("recipients", []),
            smtp_server=email_config.get("smtp_server"),
            smtp_port=email_config.get("smtp_port"),
            username=email_config.get("username"),
            password=email_config.get("password"),
            attachment_path=pdf_attachment
        )
        pbar.set_postfix_str("Notification sent")
        pbar.update(1)

if __name__ == "__main__":
    main()
