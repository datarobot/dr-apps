import os
import streamlit as st

def run():
    st.set_page_config(
        page_title="Example Custom App",
    )

    st.markdown(f"""
    This is an example streamlit App 
    """)


if __name__ == "__main__":
    run()