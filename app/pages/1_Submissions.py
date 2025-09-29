import streamlit as st
from services import api
from urllib.parse import urlparse
import re

st.set_page_config(page_title="Submissions Queue", layout="wide")


def show_submission_detail(submission_id: str):
    """Show details of a single submission"""

    try:
        submission = api.get_submission_details(submission_id)
        st.subheader(f"Submission {submission_id}")
        st.write(f"Created At: {submission['createdAt']}")


        #Display images
        col1, col2 = st.columns(2)
        with col1:
            st.image(submission["imageUrl"], caption="Strip image", width='stretch')

        with col2:
            st.image(submission["padBoxesUrl"], caption="Pad Boxes", width='stretch')

        st.markdown("### Pad Crops")
        crops_cols = st.columns(4)
        for i, crop in enumerate(submission.get("padCrops", [])):
            with crops_cols[i % 4]:
                label = extract_pad_label(crop)
                st.image(crop, caption=label, width=100)

        st.markdown("### Test Results")
        results = submission.get("results")
        if results:
            st.table([{"Parameter": r["parameter"], "Value": r["selectedValue"]} for r in results])
        else:
            st.info("No results available.")

        #Accept/Reject buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Accept", key=f"accept_{submission_id}"):
                api.accept_submission(submission_id)
                st.success("Submission accepted")
                del st.session_state.selected_submission_id
                st.rerun()
        
        with col2:
            if f"show_reject_{submission_id}" not in st.session_state:
                st.session_state[f"show_reject_{submission_id}"] = False

            if not st.session_state[f"show_reject_{submission_id}"]:
                if st.button("Reject", key=f"reject_{submission_id}"):
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


def main():
    st.title("📨 Submissions In Review")

    try:
        submissions = api.get_submissions_in_review(limit=20)

        if not submissions:
            st.error("No submissions available")
            return
        
        #List submissions
        st.write(" #### Submissions")
        for sub in submissions:
            
            is_selected = (
                'selected_submission_id'in st.session_state and
                st.session_state.selected_submission_id == sub['id']
            )

            with st.expander(f"Submission {sub['id']} - {sub['createdAt']}", expanded=is_selected):
                st.write(f"Lab Technician: {sub.get('labTechName', 'Unknown')}")

                if st.button("View Details", key=f"view_{sub['id']}"):
                    st.session_state.selected_submission_id = sub["id"]
                    st.rerun()

                if is_selected:
                    show_submission_detail(sub['id'])
        
        
                      

    except Exception as e:
        st.error(f"Failed to load submission: {e}")

if __name__ == "__main__":
    main()
