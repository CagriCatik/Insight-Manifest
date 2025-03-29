# coverage/command_center_pyside.py

import sys
import os
import threading
import logging

from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                               QWidget, QLabel, QMessageBox, QFileDialog, QProgressBar, QTextEdit)
from PySide6.QtCore import Qt

# Add the project root to PYTHONPATH so that our modules are found.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your project modules (update if your package name differs)
from src import data_loader, plotter, reporter

# Construct absolute path to config.yaml (assuming it's in the project root)
CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.yaml"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CommandCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Command Center")
        self.setGeometry(100, 100, 600, 500)
        self.config = data_loader.load_config(CONFIG_FILE)
        self.initUI()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # File selection button
        self.btn_select_excel = QPushButton("Select Excel File")
        self.btn_select_excel.clicked.connect(self.select_excel_file)
        layout.addWidget(self.btn_select_excel)
        
        # Button to load data and generate heatmap
        self.btn_load = QPushButton("Load & Analyze Coverage")
        self.btn_load.clicked.connect(self.load_and_plot)
        layout.addWidget(self.btn_load)
        
        # Button to generate and compile the report
        self.btn_report = QPushButton("Generate Report")
        self.btn_report.clicked.connect(self.generate_report)
        layout.addWidget(self.btn_report)
        
        # Button to send notifications
        self.btn_notify = QPushButton("Notify Colleagues")
        self.btn_notify.clicked.connect(self.notify_colleagues)
        layout.addWidget(self.btn_notify)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Log output text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        central_widget.setLayout(layout)
        
        # Setup logging to also output to the log_text widget.
        self.setup_logging()

    def setup_logging(self):
        # Create a custom logging handler that writes to our QTextEdit.
        class QTextEditLogger(logging.Handler):
            def __init__(self, text_edit):
                super().__init__()
                self.text_edit = text_edit

            def emit(self, record):
                msg = self.format(record)
                # Append the log message to the QTextEdit.
                self.text_edit.append(msg)
        
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        text_edit_handler = QTextEditLogger(self.log_text)
        text_edit_handler.setFormatter(formatter)
        text_edit_handler.setLevel(logging.DEBUG)
        logger.addHandler(text_edit_handler)

    def select_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            self.config["excel_file"] = file_path
            self.status_label.setText(f"Selected: {file_path}")
            logger.info("Excel file updated to: %s", file_path)

    def load_and_plot(self):
        self.status_label.setText("Loading data and generating heatmap...")
        self.progress_bar.setValue(10)
        QApplication.processEvents()
        try:
            df = data_loader.read_excel_file(self.config["excel_file"], self.config["sheet_name"])
            self.progress_bar.setValue(50)
            plotter.create_heatmap(df, self.config["heatmap_output"])
            self.progress_bar.setValue(100)
            self.status_label.setText("Heatmap generated successfully!")
            logger.info("Heatmap generated successfully!")
        except Exception as e:
            logger.exception("Error during load and plot")
            QMessageBox.critical(self, "Error", f"Failed to generate heatmap: {e}")
            self.status_label.setText("Error generating heatmap.")
            self.progress_bar.setValue(0)

    def generate_report(self):
        self.status_label.setText("Generating report...")
        QApplication.processEvents()
        try:
            # Generate the LaTeX report
            report_path = reporter.generate_latex_report(
                df=data_loader.read_excel_file(self.config["excel_file"], self.config["sheet_name"]),
                image_path=self.config["heatmap_output"],
                output_dir=self.config["report_output_dir"],
                template_path=self.config["latex_template"],
                output_filename=self.config["report_filename"]
            )
            threading.Thread(target=self._compile_report, args=(report_path,)).start()
        except Exception as e:
            logger.exception("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
            self.status_label.setText("Error generating report.")

    def _compile_report(self, report_path):
        try:
            reporter.compile_latex_report(report_path)
            reporter.export_report_to_html(report_path)
            self.status_label.setText("Report compiled successfully!")
            logger.info("Report compiled successfully!")
        except Exception as e:
            logger.exception("Error compiling report")
            QMessageBox.critical(self, "Error", f"Report compilation failed: {e}")
            self.status_label.setText("Error compiling report.")

    def notify_colleagues(self):
        self.status_label.setText("Sending notifications...")
        QApplication.processEvents()
        try:
            email_config = self.config.get("email", {})
            # Assuming the report filename ends with .tex and the compiled PDF has the same base name.
            pdf_attachment = self.config["report_filename"].replace(".tex", ".pdf")
            subject = "Insight Manifest Report"
            body = "The latest Insight Manifest report has been generated and is attached."
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
            self.status_label.setText("Notifications sent successfully!")
            logger.info("Notifications sent successfully!")
        except Exception as e:
            logger.exception("Error sending notification")
            QMessageBox.critical(self, "Error", f"Failed to send notification: {e}")
            self.status_label.setText("Error sending notifications.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommandCenter()
    window.show()
    sys.exit(app.exec())
