import streamlit as st
from services import api

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
                st.image(crop, caption=f"Pad {i+1}")

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
            if st.button("Reject", key=f"reject_{submission_id}"):
                api.reject_submission(submission_id)
                st.warning("Submission rejected")
                del st.session_state.selected_submission_id
                st.rerun()

    except Exception as e:
        st.error(f"Error loading submision detail: {e}")



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
