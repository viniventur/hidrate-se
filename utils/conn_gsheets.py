from streamlit_gsheets import GSheetsConnection
import streamlit as st
import pandas as pd

st.cache_data(show_spinner=False)
def obter_dados_pessoal():
    with st.spinner("Carregando dados..."):
        # conexao com a base de usuarios no google sheets
        conn = st.connection('gsheets', type=GSheetsConnection)
        data = conn.read(
            spreadsheet='base_aplicativo_hidrate_se',
            worksheet='base_pessoal',
            folder_id='1i51kyCSMQ2E9zepQf9ywLQaWfwvOHagq'
        )                
    return data


st.cache_data(show_spinner=False)
def obter_dados_acompanhamento():
    with st.spinner("Carregando dados..."):
        # conexao com a base de usuarios no google sheets
        conn = st.connection('gsheets', type=GSheetsConnection)
        data = conn.read(
            spreadsheet='base_aplicativo_hidrate_se',
            worksheet='base_acompanhamento',
            folder_id='1i51kyCSMQ2E9zepQf9ywLQaWfwvOHagq'
        )
        
        # Retirar o cabecalho
        headers = data.iloc[0].values
        data.columns = headers
        data.drop(index=0, axis=0, inplace=True)
    return data
