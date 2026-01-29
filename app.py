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
    """Set a centered, semi-transparent background image."""
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
# Utility: Get latest generated PDF file
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
# Sidebar Navigation
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
# BACKGROUND THREAD NORMALIZATION
# =======================================================

def start_normalization_thread():
    """Background thread target."""
    try:
        st.session_state["norm_done"] = False
        st.session_state["norm_error"] = None

        success = run_normalization()
        st.session_state["norm_done"] = True

        if not success:
            st.session_state["norm_error"] = "Normalization failed. Check logs."

    except Exception as e:
        st.session_state["norm_error"] = str(e)
        st.session_state["norm_done"] = True


# ===============================
# Run Data Normalization (With Upload)
# ===============================
if action == "🏁 Run Data Normalization":
    st.subheader("🧹 Upload Excel & Normalize Data")

    uploaded_file = st.file_uploader("Upload Latest EPS & CRM Excel File", type=["xlsx"])

    # Initialize session variables
    if "norm_started" not in st.session_state:
        st.session_state.norm_started = False
    if "norm_done" not in st.session_state:
        st.session_state.norm_done = False
    if "norm_error" not in st.session_state:
        st.session_state.norm_error = None
    if "norm_progress" not in st.session_state:
        st.session_state.norm_progress = 0
    if "norm_status" not in st.session_state:
        st.session_state.norm_status = "Waiting..."

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

        # -------------------------------
        # Background thread starter
        # -------------------------------
        def background_normalize():
            try:
                st.session_state.norm_status = "Reading Excel file..."
                st.session_state.norm_progress = 10

                success = run_normalization()

                if success:
                    st.session_state.norm_progress = 100
                    st.session_state.norm_status = "Completed successfully!"
                else:
                    st.session_state.norm_status = "Normalization failed!"
                    st.session_state.norm_error = "Error during normalization."

                st.session_state.norm_done = True

            except Exception as e:
                st.session_state.norm_done = True
                st.session_state.norm_error = str(e)

        # -------------------------------
        # Run button
        # -------------------------------
        if st.button("Run Normalization"):
            st.session_state.norm_started = True
            st.session_state.norm_done = False
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

        progress_bar = st.progress(st.session_state.norm_progress)

        # Auto-refresh every 1 second to update UI
        st.experimental_rerun()

    # -------------------------------
    # Completed
    # -------------------------------
    if st.session_state.norm_done:
        if st.session_state.norm_error:
            st.error(f"❌ {st.session_state.norm_error}")
        else:
            st.success("🎉 Normalization completed successfully!")

        st.balloons()
        st.session_state.norm_started = False
