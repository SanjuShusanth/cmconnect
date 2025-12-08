import pandas as pd
import logging
import os
import time
from config_cloud import *

# ---------------------------------------------------------
# Setup logging
# ---------------------------------------------------------
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, "normalization.log")

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)


# ---------------------------------------------------------
# Normalization Script
# ---------------------------------------------------------
def run_normalization():
    start_time = time.time()
    logging.info("🚀 Normalization pipeline started")

    try:
        # ---------------------------------------------------------
        # Step 1: Get latest uploaded raw Excel file
        # ---------------------------------------------------------
        raw_files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith(".xlsx")]

        if not raw_files:
            raise FileNotFoundError("❌ No Excel files found inside RAW_DATA_PATH. Please upload a file first.")

        latest_file = max(raw_files, key=lambda f: os.path.getmtime(os.path.join(RAW_DATA_PATH, f)))
        excel_path = os.path.join(RAW_DATA_PATH, latest_file)

        logging.info(f"📂 Step 1: Using Excel file: {excel_path}")

        # ---------------------------------------------------------
        # Step 2: Read EPS RAW & CRM RAW sheets
        # ---------------------------------------------------------
        logging.info("📖 Step 2: Reading sheets ['EPS RAW', 'CRM RAW'] from Excel")

        df_eps = pd.read_excel(excel_path, sheet_name='EPS RAW')
        df_crm = pd.read_excel(excel_path, sheet_name='CRM RAW')

        logging.info(f"✅ Sheets read successfully | EPS RAW rows: {len(df_eps)}, CRM RAW rows: {len(df_crm)}")

        # ---------------------------------------------------------
        # Step 3: Normalize column names
        # ---------------------------------------------------------
        for df in [df_eps, df_crm]:
            df.columns = (
                df.columns.str.strip()
                .str.replace(r'\s+', '_', regex=True)
                .str.replace(r'[^\w]', '', regex=True)
                .str.lower()
            )

        logging.info("✅ Column normalization completed")

        # ---------------------------------------------------------
        # Step 4: Additional column renaming (if required)
        # ---------------------------------------------------------
        df_eps = df_eps.rename(columns={
            'source': 'source_primary',
            'source1': 'source_secondary'
        })

        if '' in df_eps.columns:
            df_eps = df_eps.rename(columns={'': 'officer_name'})

        df_eps['district'].replace('Ri-Bhoi', 'Ri Bhoi', inplace=True)

        df_eps['block'] = (
            df_eps['block'].str.strip().str.replace(r'\s*C\s*&\s*RD\s*Block', '', regex=True).str.replace(r'\s+', ' ', regex=True)
            .str.title())


        logging.info("🔤 Column & values renaming completed")

        # ---------------------------------------------------------
        # Step 5: Upload to PostgreSQL (overwrite tables)
        # ---------------------------------------------------------
        logging.info("💾 Step 5: Uploading data to PostgreSQL database")

        df_eps.to_sql('staging_grievance', engine, if_exists='replace', index=False)
        df_crm.to_sql('crm_raw', engine, if_exists='replace', index=False)

        # ---------------------------------------------------------
        # Completed
        # ---------------------------------------------------------
        elapsed = round(time.time() - start_time, 2)
        logging.info(f"🏁 Normalization completed successfully in {elapsed} seconds")

        print(f"✅ Normalization completed successfully in {elapsed} seconds.")
        return True

    except Exception as e:
        logging.exception(f"❌ Error during normalization: {str(e)}")
        print("❌ Error! Check normalization.log for details.")
        return False


if __name__ == "__main__":
    run_normalization()
