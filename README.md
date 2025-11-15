📘 CMConnect – Grievance Report Automation System

CMConnect is an automated reporting and data processing system that extracts raw Excel grievance data, normalizes it, loads it into a PostgreSQL database, and generates clean PDF reports — all accessible through a Streamlit web interface.

🚀 Features
🔄 Automated Data Normalization

Reads raw Excel sheets (EPS RAW and CRM RAW).

Cleans, standardizes, renames, and validates columns.

Uploads normalized tables into PostgreSQL:

staging_grievance

crm_raw

📄 Automated PDF Reporting

Officer-wise grievance summary reports.

Pending category report with grouped formatting.

PDF outputs with Candara font and professional styling.

🌐 Streamlit Web App

Buttons to run normalization and generate each report.

Shows download links for the most recent PDF.

Built-in log viewer for debugging.

🔐 Secure Configuration

config.py (real credentials) is local only and excluded from Git.

config_template.py is included for safe sharing.

📁 Project Structure
CMConnect/
│
├── app.py                    # Streamlit Web App Interface
├── normalization.py          # Excel → Clean → PostgreSQL pipeline
├── generate_pdf.py           # Officer summary PDF generator
├── report_pdf.py             # Category-wise pending PDF generator
├── config.py                 # Real DB credentials (ignored)
├── config_template.py        # Safe placeholder configuration
├── Sqlqueries/
│   ├── NodalOfficersqlQueries.sql
│   └── NodalAnalysisReport.sql
├── Reports/                  # Output PDF files (ignored)
├── Data/                     # Raw & processed Excel files (ignored)
├── logs/                     # System logs (ignored)
├── fonts/                    # Candara.ttf (ignored)
└── README.md                 # Documentation

🧱 Architecture Diagram
                        ┌─────────────────────┐
                        │     User (UI)       │
                        │ Streamlit Web App   │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │   Normalization     │
                        │  (Excel → Cleaned)  │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ PostgreSQL Database │
                        │  staging_grievance  │
                        │      crm_raw        │
                        └──────────┬──────────┘
                                   │
                   ┌───────────────┴────────────────┐
                   ▼                                ▼
      ┌───────────────────────┐         ┌────────────────────────┐
      │ generate_pdf.py       │         │ report_pdf.py          │
      │ Officer Summary PDF   │         │ Pending Category PDF   │
      └───────────┬──────────┘         └──────────┬─────────────┘
                  │                               │
                  ▼                               ▼
        ┌────────────────────┐         ┌──────────────────────┐
        │   PDF Reports      │         │   PDF Reports        │
        │ (Stored Locally)   │         │ (Stored Locally)     │
        └────────────────────┘         └──────────────────────┘

🔄 Workflow Diagram (ETL + Reporting)
┌─────────────────────────────────────────────────────┐
│                     WORKFLOW                         │
└─────────────────────────────────────────────────────┘

1. User uploads / places Excel file in Data/raw files
            │
            ▼
2. User clicks “Run Normalization” in Streamlit
            │
            ▼
3. normalization.py executes:
      - Load Excel sheets
      - Clean + standardize
      - Normalize column names
      - Upload to PostgreSQL tables
            │
            ▼
4. User selects a report to generate:
      - Nodal Officer Summary
      - Pending Category Report
            │
            ▼
5. SQL query executes → Pandas dataframe
            │
            ▼
6. ReportLab generates structured PDF:
      - Officer header section
      - Category tables
      - Professional styling
            │
            ▼
7. PDF saved to Reports/ folder
            │
            ▼
8. Streamlit shows “Download Latest Report” button

🛠️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/cmconnect.git
cd cmconnect

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Configure Database Locally

Create a real config.py file:

copy config_template.py config.py


Then edit config.py with your real DB credentials.

▶️ Running the App
Start Streamlit:
streamlit run app.py


Open in browser:

https://digigov-cmconnect.streamlit.app/

📄 Generate Reports via Web UI

Inside the Streamlit UI:

Normalize Data → cleans & loads Excel into database

Generate Nodal Officer Report → PDF

Generate Pending Summary Report → PDF

View Latest Report → download button

View Logs → see processing history

👨‍💻 Author

Sanju Shusanth
Data Analytics & Automation
