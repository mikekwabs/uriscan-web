import streamlit as st
import pandas as pd
from services import api

st.set_page_config(page_title="Export", layout="wide")


def main():
    st.title("📤 Export Pending Transactions")

    if st.session_state.get("role") != "ADMIN":
        st.error("Access denied. Login as an ADMIN")
        return
    
    try:
        st.write("##### Pending Transactions Export")
         
        #Fetch export data
        export_data = api.get_transactions_export()

        if not export_data:
            st.info("No pednding transactions")
            return
        
        #Convert to Dataframe
        df = pd.DataFrame(export_data)
        df = df.rename(columns={
            "fullname": "Name",
            "email": "Email",
            "mobile": "Mobile",
            "pendingTests": "Pending Tests",
            "totalOwed": "Total Owed (GHS)"
        })


        #Generate CSV
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="pending_payouts.csv",
            mime="text/csv"
        )

        st.metric(
            label="💵 Total Pending Payout",
            value=f"GHS {df['Total Owed (GHS)'].sum():,.2f}",
            delta=f"{df['Pending Tests'].sum()} tests"
        )

    except Exception as e:
        st.error(f"Error loading export data: {e}")



if __name__ == "__main__":
    main()