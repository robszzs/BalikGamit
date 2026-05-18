"""
db.py — Supabase connection manager for BalikGamit.
"""

import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection() -> Client:
    """Initialize and cache the Supabase connection."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# Call this variable anywhere in your app to talk to the database
supabase = init_connection()