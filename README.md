# I'M - Insight Manifest

Insight Manifest is a robust, modular project designed to generate and publish **test coverage** and **test result** reports. It reads test coverage data from an Excel file, generates insightful visualizations (such as static heatmaps and summary statistics), compiles a detailed LaTeX report, and integrates the output into a MkDocs-powered documentation site. The system also features an email notification service and CI/CD pipelines via GitHub Actions for continuous delivery.

---

## Table of Contents

- [Features](#features)
- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Continuous Integration / Deployment](#continuous-integration--deployment)
- [Local Testing with act](#local-testing-with-act)
- [Logging and Monitoring](#logging-and-monitoring)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Data Ingestion:**  
  Reads test coverage data from an Excel file and validates the content.

- **Coverage Oracle:**  
  Generates comprehensive visualizations—including static heatmaps and summary statistics—to analyze code coverage.

- **Insight Manifest:**  
  Compiles a detailed LaTeX report that embeds PNG images (heatmap, summary statistics, full data table) for an intuitive overview of test results.

- **Pulse Dispatch:**  
  Sends email notifications (with the compiled PDF report attached) using Python’s `smtplib`, ensuring timely alerts to your team.

- **CI/CD Automation:**  
  Automates deployment of the MkDocs site and LaTeX reports via GitHub Actions, ensuring seamless updates.

- **Centralized Configuration:**  
  Uses a single `config.yaml` file (with support for environment variable overrides) for easy project customization.

- **Comprehensive Logging:**  
  Features detailed logging with console output and rotating file handlers for effective monitoring and troubleshooting.

- **Command Center GUI:**  
  An optional PySide6-based GUI (the “Command Center”) provides an interactive interface to execute key tasks like data loading, visualization, report generation, and notifications.

---

## Prerequisites

- **Python 3.9+**  
  Ensure Python is installed (preferably within the range >=3.9 and < 3.14).

- **Poetry**  
  For dependency management and virtual environments.

- **Docker**  
  Required for local testing of workflows with [act](https://github.com/nektos/act).

- **LaTeX Distribution**  
  (e.g., TeX Live) for compiling LaTeX reports.

- **GitHub Account**  
  For setting up CI/CD workflows via GitHub Actions.

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/Insight-Manifest.git
   cd Insight-Manifest
   ```

2. **Install Dependencies with Poetry:**

   ```bash
   poetry install
   ```

3. **(Optional) Activate the Virtual Environment:**

   On Windows:
   ```powershell
   poetry env info --path
   # Then activate using the provided path:
   <venv_path>\Scripts\activate
   ```

   Or use `poetry run <command>` to execute commands in the virtual environment.

---

## Configuration

1. **Edit the Configuration File:**

   Update `config/config.yaml` with your settings. For example:

   ```yaml
   excel_file: "../data/test_coverage.xlsx"
   sheet_name: "Sheet1"
   heatmap_output: "../docs/images/test_coverage.png"
   latex_template: "../templates/report_template.tex"
   report_output_dir: "../report"
   report_filename: "report.tex"

   email:
     smtp_server: "smtp.example.com"
     smtp_port: 587
     username: "sender@example.com"
     password: "yourpassword"
     recipients:
       - "recipient1@example.com"
       - "recipient2@example.com"
   ```

   _Note:_ Since `config.yaml` is in the `config` folder, the paths use `../` to reference directories in the project root.

2. **Local Secrets for Testing:**

   For local testing with act, create a `.secrets` file in the project root (and add it to `.gitignore`) with the required key-value pairs.

---

## Usage

To generate the reports and send notifications, run the main script:

```bash
poetry run python src/main.py
```

This script will:
- Load and validate the Excel test coverage data.
- Generate a heatmap visualization.
- Compile a LaTeX report (which is optionally exported to HTML).
- Send an email notification with the PDF report attached.

---

## Continuous Integration / Deployment

The project includes multiple GitHub Actions workflows located in `.github/workflows/`:

1. **deploy-mkdocs.yml:**  
   - **Trigger:** Push to the main branch.  
   - **Action:** Builds and deploys the MkDocs site to GitHub Pages.

2. **build-latex-report.yml:**  
   - **Trigger:** `workflow_run` on completion of the "Deploy MkDocs" workflow.  
   - **Action:** Installs LaTeX, compiles the report, and uploads the PDF as an artifact.

3. **deploy-and-notify.yml:**  
   - **Trigger:** `workflow_run` on completion of the "Build LaTeX Report" workflow.  
   - **Action:** Rebuilds and deploys the MkDocs site, then sends an email notification with the report attached.

Refer to these YAML files for detailed configurations.

---

## Local Testing with act

To test your GitHub Actions workflows locally on Windows:

1. **Install act:**  
   Use Chocolatey, Scoop, or download the binary from [act Releases](https://github.com/nektos/act/releases).  
   _Tip:_ Run your shell as Administrator if needed.

2. **Configure Secrets:**  
   Create a `.secrets` file in the project root with your secret key-value pairs. Ensure it is added to `.gitignore`.

3. **Run act:**

   ```powershell
   act -W .github/workflows/deploy-mkdocs.yml
   ```

   Use the `-e` flag to specify an event file if needed.

---

## Logging and Monitoring

- **Logging:**  
  The project configures logging in `src/main.py` with both console output and a rotating file handler (`project.log`).

- **Monitoring:**  
  Check `project.log` for detailed execution logs. Additional monitoring tools can be integrated as needed.

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes with clear messages.
4. Submit a pull request for review.

Please follow the coding standards and test your changes before submitting.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
