import streamlit  as st
from services import api
import pandas as pd


st.set_page_config(page_title="Transactions", layout="wide")

def main():
    st.title("Pending Transactions")

    if st.session_state.get("role") != "ADMIN":
        st.error("Access Denied. You do not have access.")
        return
    
    try:
        transactions = api.get_transactions_export()

        if not transactions:
            st.info("There are no pending transactions")
            return
        
        #Convert transactions into a dataframe
        df = pd.DataFrame(transactions)

        df = df.rename(columns= {
            'fullname': "Name",
            'email': "Email",
            "mobile": "Mobile",
            'pendingTests': "Pending Tests",
            "totalOwed": "Total Owed (GHS)"
        })

        st.write("##### Pending Transactions")
        
        for idx, row in df.iterrows():
            cols = st.columns([2,3,2,2,2,2])
            cols[0].write(row["Name"])
            cols[1].write(row["Email"])
            cols[2].write(row["Mobile"])
            cols[3].write(row["Pending Tests"])
            cols[4].write(f"GHS {row['Total Owed (GHS)']:.2f}")
            if cols[5].button("Mark Paid", key=f"paid_{idx}"):
                result = api.mark_transactions_paid(transactions[idx]["id"])
                st.success(f"{row['Name']} marked as paid")
                st.rerun()


        st.markdown("----")
        st.metric(
            label="Total Pending Owed",
            value= f"GHS {df['Total Owed (GHS)'].sum():,.2f}",
            delta=f"{df['Pending Tests'].sum()} tests"
        )
    except Exception as e:
        st.error(f"Error loading transactions: {e}")


if __name__== "__main__":
    main()
