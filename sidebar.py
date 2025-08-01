import streamlit as st
from utils import *

def run_sidebar():

    # ultimo_modulo_index = list(modulos.keys())[-1]

    with st.sidebar:

        logo_path = 'src/assets/logo_governanca.png'      
        st.image(logo_path, use_container_width=True)

        st.title('Ver se vai precisar de sidebar.')

        st.divider()