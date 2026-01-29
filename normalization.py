import pandas as pd
import logging
import os
import time
import streamlit as st
from config_cloud import *

os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, "normalization.log")

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)


def heartbeat(msg):
    st.toast(msg, icon="⚡")
    time.sleep(0.05)  # micro-sleep to avoid freeze


# -------------------------------------------------------
# OPTIMIZED Normalization
# -------------------------------------------------------
def run_normalization():
    t0 = time.time()
    logging.info("🚀 Normalization started (optimized mode)")
    heartbeat("Starting optimization...")

    try:
        # -----------------------------------------------
        # Step 1: Locate latest file
        # -----------------------------------------------
        raw_files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith(".xlsx")]
        if not raw_files:
            raise FileNotFoundError("No Excel files found.")

        latest_file = max(raw_files, key=lambda f: os.path.getmtime(os.path.join(RAW_DATA_PATH, f)))
        excel_path = os.path.join(RAW_DATA_PATH, latest_file)
        logging.info(f"Using file: {excel_path}")

        heartbeat("Reading Excel file fast...")

        # -----------------------------------------------
        # Step 2: FAST Excel Reader
        # -----------------------------------------------
        # Engine "openpyxl" is fastest for .xlsx
        df_eps = pd.read_excel(excel_path, sheet_name='EPS RAW', engine="openpyxl")
        df_crm = pd.read_excel(excel_path, sheet_name='CRM RAW', engine="openpyxl")

        # Reduce memory usage
        df_eps.columns = df_eps.columns.astype(str)
        df_crm.columns = df_crm.columns.astype(str)

        heartbeat("Excel loaded successfully")

        # -----------------------------------------------
        # Step 3: FAST Column normalization
        # -----------------------------------------------
        def normalize_cols(cols):
            cols = cols.str.strip()
            cols = cols.str.replace(r"[^\w]+", "_", regex=True)
            return cols.str.lower()

        df_eps.columns = normalize_cols(df_eps.columns)
        df_crm.columns = normalize_cols(df_crm.columns)

        logging.info("Column normalization complete")
        heartbeat("Normalizing columns...")

        # -----------------------------------------------
        # Step 4: Value cleanup (vectorized)
        # -----------------------------------------------
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

        if 'Date_of_Complaint'.lower() in df_eps.columns:
            col = 'date_of_complaint'
            df_eps[col] = pd.to_datetime(df_eps[col], errors='coerce')

        heartbeat("Cleaning values...")

        # -----------------------------------------------
        # Step 5: OPTIMIZED SQL Upload (fast chunks)
        # -----------------------------------------------
        logging.info("Uploading to database...")

        df_eps.to_sql(
            'staging_grievance',
            con=engine,
            if_exists='replace',
            index=False,
            chunksize=5000,      # 🚀 FAST
            method="multi"       # 🚀 FASTBATCH
        )

        df_crm.to_sql(
            'crm_raw',
            con=engine,
            if_exists='replace',
            index=False,
            chunksize=5000,
            method="multi"
        )

        heartbeat("Upload to DB complete")

        elapsed = round(time.time() - t0, 2)
        logging.info(f"🏁 Normalization finished in {elapsed} sec")
        st.success(f"🚀 Normalization completed in {elapsed} seconds")

        return True

    except Exception as e:
        logging.exception(f"❌ Error: {str(e)}")
        st.error(str(e))
        return False
