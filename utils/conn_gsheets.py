from streamlit_gsheets import GSheetsConnection
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import streamlit as st
import pandas as pd

from utils.validacao_dados import ml_para_litros


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
    data = sheet.get_all_values()
    data = pd.DataFrame(data)
    data.columns = data.iloc[0]
    data = data.drop(data.index[0]).reset_index(drop=True)
    return data

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
            df = read_data('base_aplicativo_hidrate_se', 'base_acompanhamento')
            df['Quantidade'] = df['Quantidade'].astype(str).str.replace(',', '.').astype(float)
            return df
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
    

@st.cache_resource(show_spinner=False)
def dados_nomes_select():
        
    data = obter_dados_pessoal()

    # Cria uma linha com espaço em branco para todas as colunas
    linha_em_branco = {col: "" for col in data.columns}

    # Adiciona a nova linha
    data = pd.concat([pd.DataFrame([linha_em_branco]), data], ignore_index=True)

    data = data.sort_values(by='nome_padronizado')

    return data['nome_padronizado']


def dados_analise_meta():

    df_pessoal = obter_dados_pessoal()
    df_pessoal['Foto'] = df_pessoal['link_foto'].str.extract(r'id=([^&]+)')  # extrai só o ID
    df_pessoal['Foto'] = 'https://drive.google.com/thumbnail?id=' + df_pessoal['Foto']
    df_pessoal.drop(columns=["Nome"], inplace=True)
    df_pessoal.rename(columns={"nome_padronizado": "Nome"}, inplace=True)

    df_acompanhamento = obter_dados_acompanhamento()

    df_acompanhamento['Data'] = pd.to_datetime(df_acompanhamento['Data'], dayfirst=True)
    # Agrupa por pessoa e data, somando a quantidade do dia
    df_acompanhamento = df_acompanhamento.groupby(['Nome', 'Data'], as_index=False)['Quantidade'].sum()
        # Cria coluna de meta atingida com base no peso corporal
    df_acompanhamento = df_acompanhamento.merge(
        df_pessoal[['Nome', 'Peso', 'Foto']],  # seleciona só as colunas que precisa
        on='Nome',
        how='left'
    )

    df_acompanhamento['Peso'] = df_acompanhamento['Peso'].astype(int)

    df_acompanhamento['Meta'] = ml_para_litros(df_acompanhamento['Peso'] * 35)

    df_acompanhamento['Meta Atingida'] = df_acompanhamento['Quantidade'] >= df_acompanhamento['Meta']

    # Formata a data para exibição
    df_acompanhamento['Data'] = pd.to_datetime(df_acompanhamento['Data']).dt.strftime('%d/%m/%Y')
    #df_acompanhamento['Data'] = df_acompanhamento['Data'].dt.strftime('%d/%m/%Y %H:%M')

    return df_acompanhamento
    