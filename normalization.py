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
        # ------------------------------
        # Step 1: Locate Excel file
        # ------------------------------
        raw_files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith(".xlsx")]
        if not raw_files:
            raise FileNotFoundError("No Excel files found.")

        latest_file = max(raw_files, key=lambda f: os.path.getmtime(os.path.join(RAW_DATA_PATH, f)))
        excel_path = os.path.join(RAW_DATA_PATH, latest_file)
        logging.info(f"Using file: {excel_path}")

        # ------------------------------
        # Step 2: Read Excel FAST
        # ------------------------------
        df_eps = pd.read_excel(excel_path, sheet_name='EPS RAW', engine="openpyxl")
        df_crm = pd.read_excel(excel_path, sheet_name='CRM RAW', engine="openpyxl")

        df_eps.columns = df_eps.columns.astype(str)
        df_crm.columns = df_crm.columns.astype(str)

        # ------------------------------
        # Step 3: Normalize column names
        # ------------------------------
        def normalize_cols(cols):
            cols = cols.str.strip()
            cols = cols.str.replace(r"[^\w]+", "_", regex=True)
            return cols.str.lower()

        df_eps.columns = normalize_cols(df_eps.columns)
        df_crm.columns = normalize_cols(df_crm.columns)

        # ------------------------------
        # Step 4: Fix value issues
        # ------------------------------
        rename_map = {
            'source': 'source_primary',
            'source1': 'source_secondary'
        }
        df_eps.rename(columns=rename_map, inplace=True)

        # rename blank unnamed columns
        df_eps.rename(columns=lambda c: "officer_name" if c.strip()=="" else c, inplace=True)

        # district fix
        if 'district' in df_eps.columns:
            df_eps['district'] = df_eps['district'].replace({'ri-bhoi': 'ri bhoi', 'Ri-Bhoi': 'Ri Bhoi'})

        # better block cleanup
        if 'block' in df_eps.columns:
            df_eps['block'] = (
                df_eps['block']
                .astype(str)
                .str.replace(r"c\s*(&|and)?\s*rd\s*block", "", regex=True, flags=re.I)
                .str.replace(r"\s+", " ", regex=True)
                .str.title()
            )

        # date column fallback
        date_cols = [c for c in df_eps.columns if "date" in c and "complaint" in c]
        if date_cols:
            col = date_cols[0]
            df_eps[col] = pd.to_datetime(df_eps[col], errors="coerce")
            df_eps.rename(columns={col: "date_of_complaint"}, inplace=True)

        # ------------------------------
        # Step 5: SQL Upload
        # ------------------------------
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

        # ------------------------------
        # Finish
        # ------------------------------
        logging.info(f"🏁 Normalization finished in {round(time.time() - t0, 2)} sec")
        return True

    except Exception as e:
        logging.exception(f"❌ Error: {str(e)}")
        return False
