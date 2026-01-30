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

if "ready" not in st.session_state:
    st.session_state.ready = True
    st.rerun()

# =======================================================
# Background image function
# =======================================================
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
# Utility: Get latest PDF
# =======================================================
def get_latest_pdf():
    try:
        pdfs = [f for f in os.listdir(REPORT_PATH) if f.endswith(".pdf")]
        if not pdfs:
            return None
        latest = max(pdfs, key=lambda f: os.path.getmtime(os.path.join(REPORT_PATH, f)))
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
# SAFE THREAD VARIABLES (no Streamlit here)
# =======================================================
if "thread_status" not in st.session_state:
    st.session_state.thread_status = {
        "running": False,
        "done": False,
        "error": None,
        "progress": 0,
        "status": "Waiting..."
    }

# =======================================================
# Background thread (NO Streamlit calls!)
# =======================================================
def background_normalize_safe():
    status = st.session_state.thread_status

    try:
        status["progress"] = 10
        status["status"] = "Reading Excel file..."

        success = run_normalization()

        if success:
            status["progress"] = 100
            status["status"] = "Completed successfully!"
        else:
            status["error"] = "Normalization failed!"
            status["status"] = "Failed"

        status["done"] = True

    except Exception as e:
        status["error"] = str(e)
        status["done"] = True


# =======================================================
#  NORMALIZATION UI
# =======================================================
if action == "🏁 Run Data Normalization":

    st.subheader("🧹 Upload Excel & Normalize Data")

    uploaded = st.file_uploader("Upload EPS & CRM Excel File", type=["xlsx"])

    if uploaded:
        st.info("📁 Upload received, saving...")

        for old in os.listdir(RAW_DATA_PATH):
            os.remove(os.path.join(RAW_DATA_PATH, old))

        new_path = os.path.join(RAW_DATA_PATH, uploaded.name)
        with open(new_path, "wb") as f:
            f.write(uploaded.getbuffer())

        st.success(f"Uploaded: {uploaded.name}")

        if st.button("Run Normalization"):
            st.session_state.thread_status = {
                "running": True,
                "done": False,
                "error": None,
                "progress": 5,
                "status": "Starting..."
            }
            threading.Thread(target=background_normalize_safe, daemon=True).start()
            st.info("⚙️ Running normalization in background…")

    # Show progress
    status = st.session_state.thread_status

    if status["running"] and not status["done"]:
        st.warning("⏳ Running…")
        st.write(status["status"])
        st.progress(status["progress"])

        time.sleep(1)
        st.rerun()

    # Completed
    if status["done"]:
        if status["error"]:
            st.error("❌ " + status["error"])
        else:
            st.success("🎉 Normalization completed!")
            st.balloons()

        status["running"] = False


# =======================================================
#  REPORT GENERATION
# =======================================================
elif action == "📄 Generate Nodal Officer Report":
    st.subheader("📘 Generate Nodal Officer Report")
    if st.button("Generate Report"):
        try:
            generate_pdf_from_sql()
            st.success("Report generated!")

            pdf = get_latest_pdf()
            if pdf:
                st.download_button("⬇ Download", open(pdf, "rb").read(),
                                   file_name=os.path.basename(pdf))
        except Exception as e:
            st.error(str(e))
            st.code(traceback.format_exc())


elif action == "📄 Generate Pending Summary Report":
    st.subheader("📗 Pending Summary Report")
    if st.button("Generate Pending Report"):
        try:
            generate_pdf2_from_sql()
            st.success("Report generated!")
            pdf = get_latest_pdf()
            if pdf:
                st.download_button("⬇ Download", open(pdf, "rb").read(),
                                   file_name=os.path.basename(pdf))
        except Exception as e:
            st.error(str(e))
            st.code(traceback.format_exc())


elif action == "📂 View Latest Report":
    pdf = get_latest_pdf()
    if pdf:
        st.success("Report found: " + os.path.basename(pdf))
        st.download_button("⬇ Download", open(pdf, "rb").read(),
                           file_name=os.path.basename(pdf))
    else:
        st.warning("No reports found.")


elif action == "📜 View Logs":
    st.subheader("Logs")
    logs = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
    if logs:
        choose = st.selectbox("Select log:", logs)
        if st.button("View"):
            content = open(os.path.join(LOG_DIR, choose), "r").read()
            st.text_area("Log", content, height=400)
    else:
        st.warning("No logs available.")
