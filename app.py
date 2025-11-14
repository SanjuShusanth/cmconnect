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

# Background image function
def set_bg(image_path):
    if os.path.exists(image_path):
        import base64
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
        css = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    else:
        st.warning("Background image not found.")

# Apply background image
set_bg(PICTURE_PATH)

st.title("📊 CM Connect Automated Reporting Webapp")
st.markdown("---")



# ===============================
# Utility: Get latest generated PDF file
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
# Run Data Normalization (With Upload)
# ===============================
if action == "🏁 Run Data Normalization":
    st.subheader("🧹 Upload Excel & Normalize Data")

    uploaded_file = st.file_uploader("Upload Latest EPS & CRM Excel File", type=["xlsx"])

    if uploaded_file:
        st.info("📁 Upload received. Saving to RAW_DATA_PATH...")

        # Delete existing files
        for old in os.listdir(RAW_DATA_PATH):
            os.remove(os.path.join(RAW_DATA_PATH, old))

        # Save uploaded file
        new_file_path = os.path.join(RAW_DATA_PATH, uploaded_file.name)
        with open(new_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ File uploaded: {uploaded_file.name}")

        # Run normalization button
        if st.button("Run Normalization"):
            try:
                start = time.time()
                st.info("⚙️ Running normalization pipeline...")

                success = run_normalization()

                if success:
                    st.success("✅ Normalization completed successfully!")
                else:
                    st.error("❌ Normalization failed! Check logs for details.")

                st.success(f"⏱ Completed in {round(time.time() - start, 2)} seconds")

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
            st.error(f"❌ Report generation failed: {e}")
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
