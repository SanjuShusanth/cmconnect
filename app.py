import streamlit as st
import os
import time
import traceback

from normalization import run_normalization
from generate_pdf import generate_pdf_from_sql
from report_pdf import generate_pdf2_from_sql
from config_cloud import *

# =======================================================
# MUST be first Streamlit command
# =======================================================
st.set_page_config(page_title="CM Connect Report Automation", layout="centered")

# Background Image
def set_bg_center_transparent(image_path):
    import base64
    if not os.path.exists(image_path):
        return
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: none;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 50%;
        left: 50%;
        width: 60%;
        height: 60%;
        transform: translate(-50%, -50%);
        background-image: url("data:image/png;base64,{encoded}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.5;
        z-index: -1;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_bg_center_transparent(PICTURE_PATH)

st.title("📊 CM Connect Automated Reporting Webapp")
st.markdown("---")

# =======================================================
# Utils
# =======================================================
def get_latest_pdf():
    try:
        files = [f for f in os.listdir(REPORT_PATH) if f.endswith(".pdf")]
        if not files:
            return None
        latest = max(files, key=lambda x: os.path.getmtime(os.path.join(REPORT_PATH, x)))
        return os.path.join(REPORT_PATH, latest)
    except:
        return None

# =======================================================
# Sidebar
# =======================================================
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

# =======================================================
# NORMALIZATION — Synchronous + Progress Bar
# =======================================================
if action == "🏁 Run Data Normalization":

    st.subheader("🧹 Upload Excel & Normalize Data")

    uploaded_file = st.file_uploader("Upload Latest EPS & CRM Excel File", type=["xlsx"])

    if uploaded_file:
        st.info("📁 Upload received. Saving to RAW_DATA_PATH...")

        # Clear old files
        for old in os.listdir(RAW_DATA_PATH):
            os.remove(os.path.join(RAW_DATA_PATH, old))

        # Save file
        new_path = os.path.join(RAW_DATA_PATH, uploaded_file.name)
        with open(new_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ File uploaded: {uploaded_file.name}")

        # Run Button
        if st.button("Run Normalization"):
            st.info("⚙️ Normalization running... Please wait")

            # Progress UI
            progress = st.progress(0)
            status = st.empty()

            # Visual-only progress updates
            for i in range(1, 30):
                progress.progress(i)
                status.write("Reading Excel...")
                time.sleep(0.05)

            # Actual normalization
            success = run_normalization()

            if success:
                progress.progress(100)
                status.write("Completed!")
                st.success("🎉 Normalization completed successfully!")
                st.balloons()
            else:
                st.error("❌ Normalization failed! Check logs.")

# =======================================================
# Generate Nodal Officer Report
# =======================================================
elif action == "📄 Generate Nodal Officer Report":
    st.subheader("📘 Generate Nodal Officer Report")

    if st.button("Generate Report"):
        try:
            generate_pdf_from_sql()
            st.success("✅ Report generated!")

            latest = get_latest_pdf()
            if latest:
                st.download_button(
                    "⬇️ Download Report",
                    data=open(latest, "rb").read(),
                    file_name=os.path.basename(latest),
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(str(e))
            st.code(traceback.format_exc())

# =======================================================
# Generate Pending Summary Report
# =======================================================
elif action == "📄 Generate Pending Summary Report":
    st.subheader("📗 Generate Summary Report")

    if st.button("Generate Pending Report"):
        try:
            generate_pdf2_from_sql()
            st.success("✅ Summary Report generated!")

            latest = get_latest_pdf()
            if latest:
                st.download_button(
                    "⬇️ Download Report",
                    data=open(latest, "rb").read(),
                    file_name=os.path.basename(latest),
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(str(e))
            st.code(traceback.format_exc())

# =======================================================
# View Latest Report
# =======================================================
elif action == "📂 View Latest Report":
    st.subheader("🗂️ Latest PDF")

    latest = get_latest_pdf()
    if latest:
        st.success(f"📄 Latest: {os.path.basename(latest)}")
        st.download_button(
            "⬇️ Download Report",
            data=open(latest, "rb").read(),
            file_name=os.path.basename(latest),
            mime="application/pdf",
        )
    else:
        st.warning("No reports available.")

# =======================================================
# Logs
# =======================================================
elif action == "📜 View Logs":
    st.subheader("🧾 Application Logs")

    logs = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
    if not logs:
        st.warning("No logs found.")
    else:
        selected = st.selectbox("Choose log", logs)
        if st.button("View Log"):
            with open(os.path.join(LOG_DIR, selected)) as f:
                st.text_area("Log Content", f.read(), height=400)
