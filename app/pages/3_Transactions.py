import streamlit  as st
from services import api
import pandas as pd


st.set_page_config(page_title="Transactions", layout="wide")

def main():
    st.title("💰 Pending Transactions")

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
            "totalOwed": "Total Owed (GHS)",
            "id": "LabTech ID"
        })

        #Checkbox column for selection
        df["Mark Paid"] = False

        st.write("#### Pending Transactions")


        #Columns to display
        visible_cols = ["Name", "Email", "Mobile", "Pending Tests", "Total Owed (GHS)", "Mark Paid"]

        edited_df = st.data_editor(
            df[visible_cols + ["LabTech ID"]],
            width='stretch',
            disabled=["Name", "Email", "Mobile", "Pending Tests", "Total Owed (GHS)", "LabTech ID"],
            hide_index=True
        )

        #Gather selected IDs
        selected_ids = edited_df.loc[edited_df["Mark Paid"], "LabTech ID"].tolist()

        if selected_ids:
            st.info(f"Selected {len(selected_ids)} lab tech(s) to mark as paid.")

            if st.button("Confirm Mark Paid"):
                try:
                    result = api.mark_transactions_paid_bulk(selected_ids)
                    st.success(f"Updated {result['updatedCount']} transactions.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to updated: {e}")
        
        else:
            st.caption("Tick rows above to select lab techs for payout.")


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
