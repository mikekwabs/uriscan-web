import streamlit as st
from services import api
import pandas as pd
from urllib.parse import urlparse
import re
from datetime import datetime

st.set_page_config(page_title="Submissions Queue", layout="wide")


def show_submission_detail(submission_id: str):
    """Show details of a single submission"""

    try:
        submission = api.get_submission_details(submission_id)

        URINE_COLOR_MAP = {
            "LIGHT_YELLOW": "#FFFACD",   # Light yellow (LemonChiffon)
            "YELLOW": "#FFFF00",         # Bright yellow
            "DARK_YELLOW": "#FFD700",    # Golden yellow
            "AMBER": "#FFBF00",          # Amber
            "BROWN": "#8B4513",          # SaddleBrown
            "RED": "#B22222",            # Firebrick red
        }

        submission_info_html = f"""
        <div style="
            background-color:#f8f9fa;
            border:1px solid #e0e0e0;
            border-radius:8px;
            padding:16px;
            margin-bottom:20px;
        ">
            <p style='margin:4px 0;'><b>🆔 Submission ID:</b> {submission_id}</p>
            <p style='margin:4px 0;'><b>📅 Created At:</b> {format_timestamp(submission['createdAt'])}</p>
        """

        # Add strip brand if available
        if submission.get("labStripBrand"):
            submission_info_html += f"<p style='margin:4px 0;'><b>🏷️ Strip Brand:</b> {submission['labStripBrand']}</p>"

        # Add urine characteristics (color + turbidity)
        urine_color = submission.get('urineColor')
        turbidity = submission.get("urineTurbidity")

        if urine_color or turbidity:
            submission_info_html += "<hr style='border:none;border-top:1px solid #ddd;margin:10px 0;'>"
            submission_info_html += "<p style='font-weight:bold;margin-bottom:6px;'>💧 Urine Characteristics</p>"

            if urine_color:
                #look up color from urine color map above
                color_hex = URINE_COLOR_MAP.get(urine_color.upper(), "#cccccc")
                submission_info_html += f"""
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                    <div style='width:24px;height:24px;background-color:{color_hex};
                                border:1px solid #ccc;border-radius:4px;'></div>
                    <span><b>Color:</b> {urine_color.replace("_", " ").title()}</span>
                </div>
                """

            if turbidity:
                submission_info_html += f"<p style='margin:4px 0;'><b>Turbidity:</b> {turbidity}</p>"

        submission_info_html += "</div>"

        st.markdown(submission_info_html, unsafe_allow_html=True)

        #STRIP & PAD Images
        st.markdown("### Images")
        cols = st.columns(3)

        with cols[0]:
            st.image(
                submission["imageUrl"],
                caption="Strip Image",
                width='stretch'
            )

        with cols[1]:
            st.image(
                submission["padBoxesUrl"],
                caption="Detected Pads",
                width='stretch'
            )

        with cols[2]:
            urine_image = submission.get("urineImageUrl")
            if urine_image:
                st.image(
                    urine_image,
                    caption="Urine Image",
                    width='stretch'
                )
            else:
                st.markdown(
                    "<p style='text-align:center;color:gray;'>No urine image available</p>",
                    unsafe_allow_html=True
                )
        
        #Pad Crops
        st.markdown("### Pad Crops")
        crops_cols = st.columns(4)
        for i, crop in enumerate(submission.get("padCrops", [])):
            with crops_cols[i % 4]:
                label = extract_pad_label(crop)
                st.image(crop, caption=label, width=100)

        #Test Table
        uriscan_results = submission.get("urs14eaResults", [])
        lab_manual_strip_results = submission.get("labStripResults", [])
        analyzer_results = submission.get("analyzerResults", [])

        if uriscan_results:
            st.markdown("### Test Results Comparison")

            #Convert both to dict for comparison
            uriscan_dict = {r["parameter"]: r["selectedValue"] for r in uriscan_results }
            lab_manual_strip_dict = {r["parameter"]: r["selectedValue"] for r in lab_manual_strip_results } 
            analyzer_results_dict = {r["parameter"]: r["selectedValue"] for r in analyzer_results } if analyzer_results else {}

            data = []
            for param, uriscan_val in uriscan_dict.items():
                lab_manual_test_val = lab_manual_strip_dict.get(param, "-")
                analyzer_val = analyzer_results_dict.get(param, "-")
                data.append({
                    "Parameter": param,
                    "URS-14EA Reading": uriscan_val,
                    "URIT Reading": lab_manual_test_val,
                    "MEDITAPE UC-11A Reading": analyzer_val,
                })
            df = pd.DataFrame(data)

            styled_df = (
            df.style
            .hide(axis="index")  # removes the index column
            .set_properties(**{
                "background-color": "#ffffff",
                "border": "1px solid #ddd",
                "border-radius": "4px",
                "font-size": "14px",
                "padding": "6px 8px",
            })
        )
            
            st.dataframe(styled_df, width='stretch')
        else:
            st.info("No test results available")

        #Accept/Reject buttons
        st.markdown("---")
        col1, col2 = st.columns([1, 1])

        st.markdown("""
        <style>
        div[data-testid="column"] > div > button[kind="secondary"] {
            width: 100%;
            height: 42px;
            border-radius: 8px;
            font-weight: 600 !important;
            font-size: 15px;
        }
        div[data-testid="column"]:first-child button {
            background-color: #28a745 !important;  /* Accept - Green */
            color: white !important;
            border: none !important;
        }
        div[data-testid="column"]:last-child button {
            background-color: #dc3545 !important;  /* Reject - Red */
            color: white !important;
            border: none !important;
        }
        div[data-testid="column"] > div > button:hover {
            opacity: 0.85;
        }
        </style>
        """, unsafe_allow_html=True)

        with col1:
            if st.button("✅ Accept", key=f"accept_{submission_id}"):
                api.accept_submission(submission_id)
                st.success("Submission accepted")
                del st.session_state.selected_submission_id
                st.rerun()
        
        with col2:
            if f"show_reject_{submission_id}" not in st.session_state:
                st.session_state[f"show_reject_{submission_id}"] = False

            if not st.session_state[f"show_reject_{submission_id}"]:
                if st.button("❌ Reject", key=f"reject_{submission_id}"):
                    st.session_state[f"show_reject_{submission_id}"] = True
                    st.rerun()

            else:
                st.markdown('### Select a rejection reason')
                rejection_reasons = [
                    "Blurry Image — Please retake the photo with steady hands and ensure the strip is in clear focus.",
                    "Poor Lighting — The image is too dark/bright. Retake the photo in a well-lit area without glare.",
                    "Background Interference — Background objects are affecting clarity. Use a plain surface and retake the photo.",
                    "Multiple Objects in Frame — Extra objects are visible. Ensure only the strip is in the frame and retake.",
                    "Low Resolution — The image is unclear/pixelated. Use the device’s full resolution and retake.",
                    "Dirty or Wet Strip — The strip is smudged or has excess liquid. Please use a clean, dry strip and retake."
                ]

                selected_reason = st.radio(
                    "Choose a reason for rejection:",
                    rejection_reasons,
                    key=f"reject_reason_{submission_id}"
                )

                if st.button("Confirm Rejection", key=f"confirm_reject_{submission_id}"):
                    if selected_reason:
                        api.reject_submission(submission_id, selected_reason)
                        st.warning(f"Submission rejected: {selected_reason}")
                        del st.session_state.selected_submission_id
                        st.rerun()
                    else:
                        st.error("Please select a reason")

    except Exception as e:
        st.error(f"Error loading submision detail: {e}")

def format_timestamp(ts_str: str) -> str:
    try:
        dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%b %d, %Y — %I:%M %p UTC")
    except Exception:
        return ts_str


def extract_pad_label(url):
    path = urlparse(url).path
    filename = path.split("/")[-1]

    base = re.sub(r'^pad_|\.png$', '', filename, flags=re.IGNORECASE)
    label = base.replace("_", " ").title()
    return label

def make_submission_card(sub: dict) -> str:
    brand = sub.get("labStripBrand")
    labtech = sub.get("labTechName", "Unknown")
    return f"""
    <div style="
        background:#f9fafb;
        border:1px solid #e5e7eb;
        border-radius:10px;
        padding:12px 14px;
        margin:6px 0 12px;
        box-shadow:0 1px 2px rgba(0,0,0,0.03);
    ">
      <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;">
        <div><b>🆔 ID:</b> {sub['id']}</div>
        <div><b>📅 Created:</b> {format_timestamp(sub['createdAt'])}</div>
        <div><b>👨‍🔬 Lab Tech:</b> {labtech}</div>
        {f"<div><b>🏷️ Brand:</b> {brand}</div>" if brand else ""}
      </div>
    </div>
    """


def main():
    st.title("📨 Submissions In Review")

    try:
        submissions = api.get_submissions_in_review(limit=20)
        if not submissions:
            st.info("No submissions available at the moment.")
            return

        for sub in submissions:
            is_selected = (
                st.session_state.get("selected_submission_id") == sub["id"]
            )

            # --- concise, readable expander header
            label = (
                f"🧾 {sub['id']}  |  📅 {format_timestamp(sub['createdAt'])}  |  👨‍🔬 "
                f"{sub.get('labTechName','Unknown')}"
            )

            with st.expander(label, expanded=is_selected):
                # --- keep only secondary info here
                brand = sub.get("labStripBrand", None)
                if brand:
                    st.markdown(
                        f"""
                        <div style='padding:8px 12px;
                                    background:#f9fafb;
                                    border:1px solid #eee;
                                    border-radius:8px;
                                    margin-bottom:12px;'>
                            <b>🏷️ Strip Brand:</b> {brand}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # main action
                if st.button("🔍 View Details", key=f"view_{sub['id']}"):
                    st.session_state.selected_submission_id = sub["id"]
                    st.rerun()

                if is_selected:
                    show_submission_detail(sub["id"])
    except Exception as e:
        st.error(f"Error loading submissions: {e}")


if __name__ == "__main__":
    main()
