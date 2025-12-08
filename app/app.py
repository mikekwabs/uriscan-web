import streamlit as st
from pages.login import login
from services.api import get_dashboard_stats
import pandas as pd

st.set_page_config(
    page_title="Uriscan Dashboard",
    layout="wide",
)

def metric_card(title, value, icon=None, color="#4F8BF9"):
    st.markdown(
        f"""
        <div style="
            background: white;
            padding: 18px 25px;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            border: 1px solid #eee;
        ">
            <div style="font-size: 14px; color: #666; margin-bottom: 4px; display:flex; align-items:center; gap:6px;">
                {'<span style="font-size:18px">' + icon + '</span>' if icon else ''}
                {title}
            </div>
            <div style="font-size: 32px; font-weight: 700; color:{color};">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_dashboard():
    st.markdown("<h1 style='margin-bottom:5px;'>📊 Uriscan Dashboard</h1>", unsafe_allow_html=True)
    
    stats = get_dashboard_stats(None, None)
    if not stats:
        return

    global_stats = stats["global"]
    today_stats = stats["today"]
    trends = stats["trend"]

    # -----------------------------------------------
    # OVERALL SUMMARY
    # -----------------------------------------------
    st.markdown("### 📈 Overall Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Total Submissions", global_stats["total_submissions"], "📨")
    with col2:
        metric_card("Accepted", global_stats["total_accepted"], "✅", color="green")
    with col3:
        metric_card("Rejected", global_stats["total_rejected"], "❌", color="red")

    st.write("")

    # -----------------------------------------------
    # TODAY SUMMARY
    # -----------------------------------------------
    st.markdown("### 📅 Today Summary")

    col4, col5, col6 = st.columns(3)
    with col4:
        metric_card("Today's Submissions", today_stats["today_submissions"], "📬")
    with col5:
        metric_card("Accepted Today", today_stats["today_accepted"], "👍", color="green")
    with col6:
        metric_card("Rejected Today", today_stats["today_rejected"], "⚠️", color="red")

    st.write("")

    # -----------------------------------------------
    # SUBMISSION TREND
    # -----------------------------------------------
    st.markdown("### 📊 Submission Trend (Daily)")

    if len(trends) > 0:
        df = pd.DataFrame(trends)
        df["date"] = pd.to_datetime(df["date"])

        st.line_chart(
            df.set_index("date")[["submissions", "accepted", "rejected"]],
            use_container_width=True
        )
    else:
        st.info("No data found for selected range.")


# ---------- Auth + Navigation ----------
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

    # Sidebar
    st.sidebar.write(f"Logged in as {st.session_state['fullname']}  ({role})")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    #Render UI dashboard
    render_dashboard()

    # Role Navigation
    if role == "REVIEWER":
        st.sidebar.page_link("./pages/research_dataset.py", label="Research Dataset")
    elif role == "ADMIN":
        st.sidebar.page_link("./pages/submissions.py", label="Pending Submissions")
        st.sidebar.page_link("./pages/export.py", label="Export for accountant")
        st.sidebar.page_link("./pages/transactions.py", label="Transactions")
        st.sidebar.page_link("./pages/research_dataset.py", label="Research Dataset")


if __name__ == "__main__":
    main()
