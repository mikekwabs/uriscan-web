import streamlit as st
from pages.login import login


def main():
    if "token" not in st.session_state:
        login()
        return
    
    role = st.session_state.get("role")

    if role not in ["REVIEWER", "ADMIN"]:
        st.error("Access Denied. Reviewers/admins only.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
        return
    
    
    
    #Side bar
    st.sidebar.write(f"Logged in as {st.session_state['fullname']}  ({role})")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    
    #Role based-navigation
    if role == "REVIEWER":
        st.sidebar.page_link("/pages/1_Submissions.py", label="Submissions Queue")
    elif role == "ADMIN":
        st.sidebar.page_link("./pages/1_Submissions.py", label="Submissions Queue")
        st.sidebar.page_link("./pages/2_Transactions.py", label="Transactions")
        st.sidebar.page_link("./pages/3_Export.py", label="Export for accountant")

if __name__ == "__main__":
    main()
    
