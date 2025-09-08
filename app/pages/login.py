import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"
AUTH_BASE_URL = "https://api.knoxxi.net/v1/ckyc/customer/signin"


def login():
    st.title("Uriscan Login")

    email = st.text_input("Email", "")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            #Authenticate
            payload = {
                "email": email,
                "password": password,
                "tenant": "DFS",
                "requestId": ""
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/118.0.5993.117 Safari/537.36"
            }
            resp = requests.post(
                AUTH_BASE_URL,
                json=payload,
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            #Grab bearer token and save
            token = data.get("securityToken")
            if not token:
                st.error("No token obtained")
                return
            
            #Save the token in session
            st.session_state["token"] = token

            #Obtain and resolve lab tech role
            profile_resp = requests.get(
                f"{API_BASE_URL}/labtechs/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            profile_resp.raise_for_status()
            profile = profile_resp.json()

            st.session_state["fullname"] = profile["fullname"]
            st.session_state["role"] = profile["role"]

            st.success(f"Welcome {profile['fullname']}!  Role: {profile['role']}")
            st.rerun()

        except Exception as e:
            st.error(f"Login failed: {str(e)}")