import streamlit as st
import os
import time
import traceback

from normalization import run_normalization
from generate_pdf import generate_pdf_from_sql
from report_pdf import generate_pdf2_from_sql
from config_cloud import *
# ===============================
# Streamlit Page Config
# ===============================
st.set_page_config(page_title="CM Connect Report Automation", layout="centered")
st.title("📊 CM Connect Automated Reporting Dashboard")
st.markdown("---")

# ===============================
# Utility: Display latest generated report
# ===============================
def get_latest_pdf():
    try:
        pdf_files = [f for f in os.listdir(REPORT_PATH) if f.endswith(".pdf")]
        if not pdf_files:
            return None
        latest_file = max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(REPORT_PATH, f)))
        return os.path.join(REPORT_PATH, latest_file)
    except Exception:
        return None


# ===============================
# Sidebar Navigation
# ===============================
st.sidebar.title("🔧 Actions")
action = st.sidebar.radio(
    "Select Task:",
    [
        "🏁 Run Data Normalization",
        "📄 Generate Nodal Officer Report",
        "📄 Generate Pending Summary Report",
        "📂 View Latest Report",
        "📜 View Logs",
    ],
)

# ===============================
# Run Data Normalization
# ===============================
if action == "🏁 Run Data Normalization":
    st.subheader("🧹 Normalize & Upload Data to PostgreSQL")

    if st.button("Run Normalization"):
        try:
            start = time.time()
            from normalization import engine, RAW_DATA_PATH, LOG_DIR  # ensure imports load fresh config

            st.info("Running normalization pipeline... Please wait.")
            # Execute normalization script logic directly
            success = run_normalization()
            if success:
                st.success("✅ Normalization completed successfully!")
            else:
                st.error("❌ Normalization failed! Check logs for details.")
            duration = round(time.time() - start, 2)
            st.success(f"✅ Normalization completed successfully in {duration} seconds!")

        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.code(traceback.format_exc())

# ===============================
# Generate Nodal Officer Report
# ===============================
elif action == "📄 Generate Nodal Officer Report":
    st.subheader("📘 Generate Nodal Officer Grievance Summary Report")

    if st.button("Generate Report"):
        try:
            generate_pdf_from_sql()
            st.success("✅ Nodal Officer Report generated successfully!")

            latest_pdf = get_latest_pdf()
            if latest_pdf:
                st.download_button(
                    label="⬇️ Download Latest Report",
                    data=open(latest_pdf, "rb").read(),
                    file_name=os.path.basename(latest_pdf),
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.code(traceback.format_exc())

# ===============================
# Generate Pending Summary Report
# ===============================
elif action == "📄 Generate Pending Summary Report":
    st.subheader("📗 Generate Officer Pending Summary Report")

    if st.button("Generate Pending Report"):
        try:
            generate_pdf2_from_sql()
            st.success("✅ Pending Summary Report generated successfully!")

            latest_pdf = get_latest_pdf()
            if latest_pdf:
                st.download_button(
                    label="⬇️ Download Latest Report",
                    data=open(latest_pdf, "rb").read(),
                    file_name=os.path.basename(latest_pdf),
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.code(traceback.format_exc())

# ===============================
# View Latest Report
# ===============================
elif action == "📂 View Latest Report":
    st.subheader("🗂️ Latest Generated PDF")

    latest_pdf = get_latest_pdf()
    if latest_pdf:
        st.success(f"📄 Found latest report: `{os.path.basename(latest_pdf)}`")
        st.download_button(
            label="⬇️ Download Report",
            data=open(latest_pdf, "rb").read(),
            file_name=os.path.basename(latest_pdf),
            mime="application/pdf",
        )
    else:
        st.warning("⚠️ No PDF reports found yet. Please generate one first.")

# ===============================
# View Logs
# ===============================
elif action == "📜 View Logs":
    st.subheader("🧾 Application Logs")

    log_files = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
    if not log_files:
        st.warning("⚠️ No logs found.")
    else:
        selected_log = st.selectbox("Select a log file", log_files)
        if st.button("View Log Content"):
            log_path = os.path.join(LOG_DIR, selected_log)
            with open(log_path, "r", encoding="utf-8") as f:
                log_content = f.read()
            st.text_area("📋 Log Content", log_content, height=400)
