import streamlit as st
import os
import time
import threading
import traceback

from normalization import run_normalization
from generate_pdf import generate_pdf_from_sql
from report_pdf import generate_pdf2_from_sql
from config_cloud import *

# =======================================================
# MUST be first Streamlit command
# =======================================================
st.set_page_config(page_title="CM Connect Report Automation", layout="centered")

# Safe session initialization
if "ready" not in st.session_state:
    st.session_state.ready = True
    st.rerun()

# =======================================================
# Background image function
# =======================================================
def set_bg_center_transparent(image_path):
    import base64
    if not os.path.exists(image_path):
        st.warning("Background image not found.")
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
# Utility: Get latest generated PDF
# =======================================================
def get_latest_pdf():
    try:
        pdf_files = [f for f in os.listdir(REPORT_PATH) if f.endswith(".pdf")]
        if not pdf_files:
            return None
        latest = max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(REPORT_PATH, f)))
        return os.path.join(REPORT_PATH, latest)
    except Exception:
        return None


# =======================================================
# Sidebar Menu
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
# Background Thread (Normalization)
# =======================================================
def background_normalize():
    try:
        st.session_state.norm_status = "Reading Excel file..."
        st.session_state.norm_progress = 10

        success = run_normalization()

        if success:
            st.session_state.norm_progress = 100
            st.session_state.norm_status = "Completed successfully!"
        else:
            st.session_state.norm_status = "Normalization failed."
            st.session_state.norm_error = "Error during normalization."

        st.session_state.norm_done = True

    except Exception as e:
        st.session_state.norm_done = True
        st.session_state.norm_error = str(e)


# =======================================================
# Run Data Normalization (Main UI)
# =======================================================
if action == "🏁 Run Data Normalization":
    st.subheader("🧹 Upload Excel & Normalize Data")

    uploaded_file = st.file_uploader("Upload Latest EPS & CRM Excel File", type=["xlsx"])

    # Initialize session-state variables
    defaults = {
        "norm_started": False,
        "norm_done": False,
        "norm_error": None,
        "norm_progress": 0,
        "norm_status": "Waiting..."
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)

    if uploaded_file:
        st.info("📁 Upload received. Saving to RAW_DATA_PATH...")

        # Clear old files
        for old in os.listdir(RAW_DATA_PATH):
            os.remove(os.path.join(RAW_DATA_PATH, old))

        # Save uploaded file
        new_file_path = os.path.join(RAW_DATA_PATH, uploaded_file.name)
        with open(new_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ File uploaded: {uploaded_file.name}")

        if st.button("Run Normalization"):
            st.session_state.norm_started = True
            st.session_state.norm_done = False
            st.session_state.norm_error = None
            st.session_state.norm_progress = 5
            st.session_state.norm_status = "Starting..."
            threading.Thread(target=background_normalize, daemon=True).start()
            st.info("⚙️ Normalization started in background… Please wait ⏳")

    # -------------------------------
    # Show progress while running
    # -------------------------------
    if st.session_state.norm_started and not st.session_state.norm_done:
        st.warning("⏳ Normalization in progress…")
        st.write(st.session_state.norm_status)
        st.progress(st.session_state.norm_progress)

        # Safe timed auto-refresh for Streamlit 1.32
        if "last_refresh" not in st.session_state:
            st.session_state.last_refresh = time.time()

        if time.time() - st.session_state.last_refresh > 1:
            st.session_state.last_refresh = time.time()
            st.rerun()

    # -------------------------------
    # When Completed
    # -------------------------------
    if st.session_state.norm_done:

        # stop the timed refresh loop
        if "last_refresh" in st.session_state:
            del st.session_state.last_refresh

        if st.session_state.norm_error:
            st.error(f"❌ {st.session_state.norm_error}")
        else:
            st.success("🎉 Normalization completed successfully!")

        st.balloons()
        st.session_state.norm_started = False


# =======================================================
# Generate Nodal Officer Report
# =======================================================
elif action == "📄 Generate Nodal Officer Report":
    st.subheader("📘 Generate Nodal Officer Grievance Summary Report")

    if st.button("Generate Report"):
        try:
            generate_pdf_from_sql()
            st.success("✅ Report generated!")

            latest = get_latest_pdf()
            if latest:
                st.download_button(
                    label="⬇️ Download Latest Report",
                    data=open(latest, "rb").read(),
                    file_name=os.path.basename(latest),
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.code(traceback.format_exc())


# =======================================================
# Generate Pending Summary Report
# =======================================================
elif action == "📄 Generate Pending Summary Report":
    st.subheader("📗 Generate Officer Pending Summary Report")

    if st.button("Generate Pending Report"):
        try:
            generate_pdf2_from_sql()
            st.success("✅ Pending Summary Report generated!")

            latest = get_latest_pdf()
            if latest:
                st.download_button(
                    label="⬇️ Download Latest Report",
                    data=open(latest, "rb").read(),
                    file_name=os.path.basename(latest),
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(f"❌ Report generation failed: {e}")
            st.code(traceback.format_exc())


# =======================================================
# View Latest Report
# =======================================================
elif action == "📂 View Latest Report":
    st.subheader("🗂️ Latest Generated PDF")
    latest = get_latest_pdf()

    if latest:
        st.success(f"📄 Found latest: `{os.path.basename(latest)}`")
        st.download_button(
            label="⬇️ Download Report",
            data=open(latest, "rb").read(),
            file_name=os.path.basename(latest),
            mime="application/pdf",
        )
    else:
        st.warning("⚠️ No reports found yet.")


# =======================================================
# View Logs
# =======================================================
elif action == "📜 View Logs":
    st.subheader("🧾 Application Logs")

    log_files = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]

    if not log_files:
        st.warning("⚠️ No logs found.")
    else:
        selected = st.selectbox("Select a log file", log_files)
        if st.button("View Log Content"):
            with open(os.path.join(LOG_DIR, selected), "r", encoding="utf-8") as f:
                content = f.read()
            st.text_area("📋 Log Content", content, height=400)
