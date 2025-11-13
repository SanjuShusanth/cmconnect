import pandas as pd
import logging
import os
import time
from config_cloud import *

# ---------------------------------------------------------
# Setup logging
# ---------------------------------------------------------
log_file_path = os.path.join(LOG_DIR, "normalization.log")
os.makedirs(LOG_DIR, exist_ok=True)

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
    import time
    start_time = time.time()
    logging.info("🚀 Normalization pipeline started")

    try:
        excel_path = os.path.join(RAW_DATA_PATH, "EPS_and_CRM_Overall_RAW Data-12_Nov.xlsx")
        logging.info(f"📂 Step 1: Excel file path resolved -> {excel_path}")

        logging.info("📖 Step 2: Reading sheets ['EPS RAW', 'CRM RAW'] from Excel")
        df = pd.read_excel(excel_path, sheet_name='EPS RAW')
        df1 = pd.read_excel(excel_path, sheet_name='CRM RAW')
        logging.info(f"✅ Sheets read successfully | EPS RAW rows: {len(df)}, CRM RAW rows: {len(df1)}")

        for d in [df, df1]:
            d.columns = (
                d.columns.str.strip()
                .str.replace(r'\s+', '_', regex=True)
                .str.replace(r'[^\w]', '', regex=True)
                .str.lower()
            )

        logging.info("✅ Column normalization completed")

        df = df.rename(columns={'source': 'source_primary', 'source1': 'source_secondary'})
        if '' in df.columns:
            df = df.rename(columns={'': 'officer_name'})
        logging.info("✅ Column renaming completed")

        logging.info("💾 Step 5: Uploading data to PostgreSQL database")
        df.to_sql('staging_grievance', engine, if_exists='replace', index=False)
        df1.to_sql('crm_raw', engine, if_exists='replace', index=False)
        elapsed_time = round(time.time() - start_time, 2)

        logging.info(f"🏁 Normalization pipeline completed successfully in {elapsed_time} seconds")
        print(f"✅ Normalization complete in {elapsed_time} seconds. Check logs/normalization.log for details.")
        return True

    except Exception as e:
        logging.exception(f"❌ Error during normalization pipeline: {str(e)}")
        print("❌ Error occurred. Check logs/normalization.log for details.")
        return False


if __name__ == "__main__":
    run_normalization()



