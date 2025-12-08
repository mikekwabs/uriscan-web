import streamlit as st
from services import api
from pages.submissions import format_timestamp, show_submission_detail


st.set_page_config(page_title="Accepted Submissions", layout="wide")


def main():
    st.title("📕Rejected Submissions")

    search = st.text_input("Search submissions", placeholder="Search by ID")

    # Track state
    if "rejected_page" not in st.session_state:
        st.session_state.rejected_page = 0

    if "rejected_search" not in st.session_state:
        st.session_state.rejected_search = ""

    if search != st.session_state.rejected_search:
        st.session_state.rejected_search = search
        st.session_state.rejected_page = 0
        st.rerun()

    #Pagination Values
    limit = 50
    offset = st.session_state.rejected_page * limit


    try:
        submissions = api.get_admin_submissions(status="rejected", search=search, limit=limit, offset=offset)

        if not submissions and st.session_state.rejected_page > 0:
            st.session_state.rejected_page -= 1
            st.rerun()

        if not submissions:
            st.info("No rejected submissions found.")
            return

        #List submissions
        for sub in submissions:
            is_selected = (
                st.session_state.get("selected_submission_id") == sub["id"]
            )

            label = (
                 f"🧾 {sub['id']}  |  "
                f"📅 {format_timestamp(sub['created_at'])}  |  "
            )

            with st.expander(label, expanded=is_selected):

                #Show comment if available
                comment = sub.get("rejection_comment") or sub.get("rejectionComment")
                if comment:
                    st.markdown(
                        f"""
                        <div style="
                            padding: 12px 15px;
                            background: #ffecec;
                            border-left: 4px solid #ff4d4d;
                            border-radius: 6px;
                            margin-bottom: 12px;
                        ">
                            <b>❌ Rejection Comment:</b><br>
                            {comment}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                brand = sub.get("labStripBrand")
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

                if st.button("🔍 View Details", key=f"view_{sub['id']}"):
                    st.session_state.selected_submission_id = sub["id"]
                    st.rerun()

                if is_selected:
                    show_submission_detail(sub["id"], mode="readonly")


        #Pagination controls
        col_prev, col_next = st.columns([0.2, 0.8])

        with col_prev:
            if st.session_state.rejected_page > 0:
                if st.button("⬅️ Previous Page"):
                    st.session_state.rejected_page -= 1
                    st.rerun()

        with col_next:
            if len(submissions) == limit:
                if st.button("Next Page ➡️"):
                    st.session_state.rejected_page += 1
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading submissions: {e}")


if __name__ == "__main__":
    main()






