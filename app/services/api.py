import requests
import streamlit as st


API_BASE_URL = "http://localhost:8000/"

def _auth_headers():
    token = st.session_state.get("token")
    if not token:
        raise ValueError("No token found is session state")
    return {"Authorization": f"Bearer {token}"}



#Submissions
def get_submissions_in_review(limit: int = 10, offset: int = 0, labtech_id: str = None):
    params = {"limit": limit, "offset": offset}

    if labtech_id:
        params["lab_technician_id"] = labtech_id
    resp = requests.get(f"{API_BASE_URL}/submissions/in-review", headers=_auth_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def get_submission_details(submission_id: str):
    resp = requests.get(f"{API_BASE_URL}/tests/{submission_id}", headers=_auth_headers())
    resp.raise_for_status()
    return resp.json()


def accept_submission(submission_id: str):
    resp = requests.put(f"{API_BASE_URL}/submissions/{submission_id}/accept", headers=_auth_headers())
    resp.raise_for_status()
    return resp.json()

def reject_submission(submission_id: str):
    resp = requests.put(f"{API_BASE_URL}/submissions/{submission_id}/reject", headers=_auth_headers())
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

