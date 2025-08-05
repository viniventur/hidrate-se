import pandas as pd
import time
import json
import pytz 
import plotly
import datetime
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils import *
from sidebar import *

import warnings
warnings.filterwarnings('ignore')


def analise_ranking():

    df_pessoal = obter_dados_pessoal()

    df_pessoal['Foto'] = df_pessoal['link_foto'].str.extract(r'id=([^&]+)')  # extrai só o ID
    df_pessoal['Foto'] = 'https://drive.google.com/thumbnail?id=' + df_pessoal['Foto']

    st.dataframe(df_pessoal[["Foto", "nome_padronizado"]],
                    column_config={
                        'Foto': st.column_config.ImageColumn(width='medium')
                    },
                    column_order=['Foto', 'Nome', 'nome_padronizado', 'link_foto'],
                    hide_index=True,
                    use_container_width=True
                    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(obter_dados_acompanhamento())
        st.write('analise')
