import os
from urllib.parse import unquote, urlparse
import streamlit as st
import requests
from services.api import _auth_headers, API_BASE_URL


st.title("📦 URISCAN — Research Dataset Export")
st.write("Download the full URISCAN dataset (URS14EA + Analyzer + Metadata).")
st.caption("This operation may take a few seconds while the backend prepares the Excel file.")

st.divider()


# ----------------------------
# Section: Generate Export
# ----------------------------
with st.container():
    st.subheader("🛠️ Generate New Dataset Export")
    st.write("Click the button below to request a fresh dataset export.")

    generate_clicked = st.button("🔄 Generate Dataset Export", use_container_width=True)

    if generate_clicked:
        with st.spinner("Creating dataset... please wait..."):
            resp = requests.get(f"{API_BASE_URL}/exports/dataset", headers=_auth_headers())
            resp.raise_for_status()
            task_id = resp.json()["task_id"]
            st.session_state["export_task_id"] = task_id
        
        st.success(f"Dataset export requested.\n\n**Task ID:** `{task_id}`")


# ----------------------------
# Section: Task Status
# ----------------------------
task_id = st.session_state.get("export_task_id")

if task_id:
    st.divider()
    st.subheader("📡 Export Status")

    with st.status("Checking export task status..."):
        status_resp = requests.get(
            f"{API_BASE_URL}/exports/dataset/status/{task_id}",
            headers=_auth_headers(),
        )
        data = status_resp.json()

    state = data.get("state")
    download_url = data.get("download_url")

    st.write(f"**Status:** {state}")

    # SUCCESS
    if state == "SUCCESS" and download_url:
        st.success("Your dataset is ready! 🎉")

        parsed = urlparse(download_url)
        raw_name = os.path.basename(parsed.path)
        file_name = unquote(raw_name) or "uriscan_dataset.xlsx"

        # Download stream
        resp = requests.get(download_url)
        resp.raise_for_status()
        file_bytes = resp.content

        st.download_button(
            label="⬇️ Download Excel File",
            data=file_bytes,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    elif state == "ERROR":
        st.error("Dataset export failed. Please try again.")
