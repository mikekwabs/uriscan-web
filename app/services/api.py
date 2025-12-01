import requests
import streamlit as st


API_BASE_URL = "https://api.knoxxi.net/knoxxi-uriscan"
LOCAL_API_BASE_URL = "http://localhost:8000"

def _auth_headers():
    token = st.session_state.get("token")
    if not token:
        raise ValueError("No token found is session state")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "PostmanRuntime/7.35.0",
    }



#Submissions
def get_submissions_in_review(limit: int = 10, offset: int = 0, labtech_id: str = None):
    params = {"limit": limit, "offset": offset}

    if labtech_id:
        params["lab_technician_id"] = labtech_id
    resp = requests.get(f"{API_BASE_URL}/submissions/in-review", headers=_auth_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def get_submission_details(submission_id: str):
    resp = requests.get(f"{API_BASE_URL}/admin/{submission_id}", headers=_auth_headers())
    resp.raise_for_status()
    return resp.json()


def accept_submission(submission_id: str):
    resp = requests.put(f"{API_BASE_URL}/submissions/{submission_id}/accept", headers=_auth_headers())
    resp.raise_for_status()
    return resp.json()

def reject_submission(submission_id: str, comment: str):
    """
    Reject a submission with a comment
    """
    payload = {"comment": comment }
    resp = requests.put(
        f"{API_BASE_URL}/submissions/{submission_id}/reject",
        headers=_auth_headers(),
        json=payload
    )
    resp.raise_for_status()
    return resp.json()


#Transactions
def get_transactions_export():
    resp = requests.get(f"{API_BASE_URL}/transactions/export", headers=_auth_headers())
    resp.raise_for_status()
    return resp.json()

def mark_transactions_paid_bulk(labtechIds: list[str]):
    url = f"{API_BASE_URL}/transactions/mark-paid-bulk"
    payload = {"labtechIds": labtechIds}
    resp = requests.post(url, json=payload, headers=_auth_headers())
    resp.raise_for_status()
    return resp.json()

#Dashboard
def get_dashboard_stats(start_date: str, end_date: str):
    """
    Fetch dashboard analytics from backend.
    start_date and end_date must be ISO date strings: "YYYY-MM-DD"
    """
    params = {"start_date": start_date, "end_date": end_date}

    resp = requests.get(
        f"{LOCAL_API_BASE_URL}/dashboard",
        headers=_auth_headers(),
        params=params
    )

    resp.raise_for_status()
    return resp.json()

