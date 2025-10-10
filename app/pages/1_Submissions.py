import streamlit as st
from services import api
import pandas as pd
from urllib.parse import urlparse
import re

st.set_page_config(page_title="Submissions Queue", layout="wide")


def show_submission_detail(submission_id: str):
    """Show details of a single submission"""

    try:
        submission = api.get_submission_details(submission_id)

        submission_info_html = f"""
        <div style="
            background-color:#f8f9fa;
            border:1px solid #e0e0e0;
            border-radius:8px;
            padding:16px;
            margin-bottom:20px;
        ">
            <p style='margin:4px 0;'><b>🆔 Submission ID:</b> {submission_id}</p>
            <p style='margin:4px 0;'><b>📅 Created At:</b> {submission['createdAt']}</p>
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
                submission_info_html += f"""
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                    <div style='width:24px;height:24px;background-color:{urine_color};
                                border:1px solid #ccc;border-radius:4px;'></div>
                    <span><b>Color:</b> {urine_color}</span>
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
        uriscan_results = submission.get("results", [])
        lab_reference = submission.get("labReferenceResults", [])

        if uriscan_results:
            st.markdown("### Test Results Comparison")

            #Convert both to dict for comparison
            uriscan_dict = {r["parameter"]: r["selectedValue"] for r in uriscan_results }
            lab_dict = {r["parameter"]: r["selectedValue"] for r in lab_reference } if lab_reference else {}

            data = []
            for param, uriscan_val in uriscan_dict.items():
                lab_val = lab_dict.get(param, "-")
                match = uriscan_val.strip().lower() == lab_val.strip().lower() if lab_val != "-" else None
                data.append({
                    "Parameter": param,
                    "Uriscan Reading": uriscan_val,
                    "Lab Reading": lab_val,
                    "Match": "✅" if match else ("⚠️" if lab_val != "-" else "—")
                })
            df = pd.DataFrame(data)

            def highlight_match(val):
                if val == "✅":
                    color = "#d1e7dd"   # light green
                elif val == "⚠️":
                    color = "#fff3cd"   # light yellow
                else:
                    color = "#f8f9fa"   # light gray
                return f"background-color: {color}; text-align:center; font-weight:bold;"

            styled_df = (
            df.style
            .hide(axis="index")  # removes the index column
            .applymap(highlight_match, subset=["Match"])
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
                    "Shadows Present — Shadows are covering parts of the strip. Adjust the angle or light source and retake.",
                    "Strip Not Centered — The strip is not properly centered. Align the strip fully within the frame and retake.",
                    "Partial Strip Captured — Only part of the strip is visible. Capture the entire strip clearly.",
                    "Background Interference — Background objects are affecting clarity. Use a plain surface and retake the photo.",
                    "Angle Distortion — The photo was taken at a slant. Hold the camera directly above the strip and retake.",
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



def extract_pad_label(url):
    path = urlparse(url).path
    filename = path.split("/")[-1]

    base = re.sub(r'^pad_|(_\d+)?\.png(\.png)?$', '', filename, flags=re.IGNORECASE)
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
        <div><b>📅 Created:</b> {sub['createdAt']}</div>
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
                f"🧾 {sub['id']}  |  📅 {sub['createdAt']}  |  👨‍🔬 "
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
