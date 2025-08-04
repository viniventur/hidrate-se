from streamlit_gsheets import GSheetsConnection
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import streamlit as st
import pandas as pd


def connect_to_gsheet(creds_json, spreadsheet_name, sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.worksheet(sheet_name)

CREDENTIALS_FILE = st.secrets['google_credentials2']

# Função para ler os dados
def read_data(planilha, aba):
    sheet = connect_to_gsheet(CREDENTIALS_FILE, planilha, aba)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Função para adicionar nova linha
def add_data(planilha, aba, linha):
    sheet = connect_to_gsheet(CREDENTIALS_FILE, planilha, aba)
    sheet.append_row(linha)

@st.cache_data(show_spinner=False)
def obter_dados_pessoal():
    with st.spinner("Carregando dados..."):
        try:
            return read_data('base_aplicativo_hidrate_se', 'base_pessoal')
        except Exception as e:
            return st.error(f"Erro ao carregar dados: {e}")


@st.cache_data(show_spinner=False)
def obter_dados_acompanhamento():
    with st.spinner("Carregando dados..."):
        try:
            return read_data('base_aplicativo_hidrate_se', 'base_acompanhamento')
        except Exception as e:
            return st.error(f"Erro ao carregar dados: {e}")
        

def novo_registro(nome, data_registro, qnt_bebida):
    with st.spinner("Enviando seu registro..."):
        try:
            dados = [nome, data_registro, qnt_bebida]
            add_data('base_aplicativo_hidrate_se', 'base_acompanhamento', dados)
        except Exception as e:
            return st.error(f"Erro ao carregar dados: {e}")


def conferir_registro_duplicado(nome, data_registro):
    try:
        df = read_data('base_aplicativo_hidrate_se', 'base_acompanhamento')
        return df.loc[(df["Nome"] == nome) & (df["Data"] == data_registro)]
    except Exception as e:
        return st.error(f"Erro ao carregar dados: {e}")