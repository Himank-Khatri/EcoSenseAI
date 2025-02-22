import streamlit as st
from st_pages import add_page_title, get_nav_from_toml

st.set_page_config(page_title='EcoSenseAI', layout='wide', page_icon='images/logo.png')
st.markdown("""
    <style>
        /* Reduce top padding for the main content */
        .block-container {
            padding-top: 30px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("EcoSenseAI")
st.sidebar.markdown("### What's in the air before it's there!")
st.sidebar.markdown("---") 

nav = get_nav_from_toml(".streamlit/pages.toml")
pg = st.navigation(nav) 

st.logo("images/logo.png")

add_page_title(pg)

pg.run()