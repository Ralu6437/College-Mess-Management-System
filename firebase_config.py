
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


@st.cache_resource
def connect_firebase():
    """Connect the Streamlit app to Firebase Cloud Firestore."""
    try:
        if not firebase_admin._apps:
            service_account = dict(
                st.secrets["firebase_service_account"]
            )
            credential = credentials.Certificate(service_account)
            firebase_admin.initialize_app(credential)

        db = firestore.client()
        return db

    except Exception as error:
        st.error(
            "Firebase connection failed. Check your Streamlit Secrets "
            "and Firebase project configuration."
        )
        st.error(str(error))
        st.stop()


db = connect_firebase()
