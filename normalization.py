import pandas as pd
import logging
import os
import time
import re
from config_cloud import *

os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, "normalization.log")

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

def run_normalization():
    t0 = time.time()
    logging.info("🚀 Normalization started (optimized mode)")

    try:
        raw_files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith(".xlsx")]
        if not raw_files:
            raise FileNotFoundError("No Excel files found.")

        latest_file = max(raw_files, key=lambda f: os.path.getmtime(os.path.join(RAW_DATA_PATH, f)))
        excel_path = os.path.join(RAW_DATA_PATH, latest_file)
        logging.info(f"Using file: {excel_path}")

        df_eps = pd.read_excel(excel_path, sheet_name='EPS RAW', engine="openpyxl")
        df_crm = pd.read_excel(excel_path, sheet_name='CRM RAW', engine="openpyxl")

        df_eps.columns = df_eps.columns.astype(str)
        df_crm.columns = df_crm.columns.astype(str)

        # Column normalization
        def normalize_cols(cols):
            cols = cols.str.strip()
            cols = cols.str.replace(r"[^\w]+", "_", regex=True)
            return cols.str.lower()

        df_eps.columns = normalize_cols(df_eps.columns)
        df_crm.columns = normalize_cols(df_crm.columns)

        # Value cleanup
        rename_map = {
            'source': 'source_primary',
            'source1': 'source_secondary'
        }
        df_eps.rename(columns=rename_map, inplace=True)

        if '' in df_eps.columns:
            df_eps.rename(columns={'': 'officer_name'}, inplace=True)

        if 'district' in df_eps.columns:
            df_eps['district'] = df_eps['district'].replace({'Ri-Bhoi': 'Ri Bhoi'})

        if 'block' in df_eps.columns:
            df_eps['block'] = (
                df_eps['block']
                .astype(str)
                .str.replace(r"c\s*&\s*rd\s*block", "", regex=True, flags=re.I)
                .str.replace(r"\s+", " ", regex=True)
                .str.title()
            )

        if 'date_of_complaint' in df_eps.columns:
            df_eps['date_of_complaint'] = pd.to_datetime(df_eps['date_of_complaint'], errors='coerce')

        # Upload to DB
        df_eps.to_sql(
            'staging_grievance',
            con=engine,
            if_exists='replace',
            index=False,
            chunksize=5000,
            method="multi"
        )

        df_crm.to_sql(
            'crm_raw',
            con=engine,
            if_exists='replace',
            index=False,
            chunksize=5000,
            method="multi"
        )

        logging.info(f"🏁 Normalization finished in {round(time.time() - t0, 2)} sec")
        return True

    except Exception as e:
        logging.exception(f"❌ Error: {str(e)}")
        return False
