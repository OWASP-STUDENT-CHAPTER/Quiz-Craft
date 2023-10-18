import streamlit as st
st.download_button(
    label="DOWNLOAD!",
    data="trees",
    file_name="string.txt",
    mime="text/plain"
)