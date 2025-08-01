import os
from datetime import datetime
import pytz
from dotenv import dotenv_values
import streamlit as st
env = dotenv_values('.env')

def is_local():
    """Verifica se está rodando localmente"""
    return "IS_LOCAL" in env

def nome_pag_title():
    return 'Hidrate-se - Governança'

def img_pag_icon():
    return 'src/assets/logo_gov_favicon.png'

# modulos
@st.cache_data(show_spinner=False)
def modulos():
    '''
        Retorna um dicionário com informações sobre os módulos disponiveis no sistema.

        Estrutura:
        - Chave (int): Identificador do módulo.
        - Valor (list): [Nome do módulo (str), Caminho do arquivo (str), Emoji (str)] - .


        Exemplo de uso:
            modulos = modulos()
            print(modulos_dict[1])  # Retorna ['Início', 'pages/Inicio.py', ':material/home:']
            print(modulos[0][1]) # Retorna o endereço do primeiro modulo
    '''
    modulos = {
        0: ['Login', 'pag_login.py'],
        1: ['Início', 'pages/Inicio.py', ':material/home:'],
        2: ['Painéis Internos', 'pages/paineis_internos.py', ':material/input_circle:'],
        3: ['Painéis Externos', 'pages/paineis_externos.py', ':material/output_circle:'],
        4: ['Administração', 'pages/admin.py', ':material/admin_panel_settings:']
    }
    return modulos

modulos = modulos()

def voltar_inicio():
    with st.spinner('Redirecionando...'):
        st.switch_page(modulos[1][1])



def data_hr_atual():
    # Define o fuso horário GMT-3
    fuso_horario = pytz.timezone("America/Sao_Paulo")
    # Obtém a data e hora atual no fuso horário especificado
    now = datetime.now(fuso_horario)
    # Formata no estilo dd-mm-yyyy hh:mm
    data_hora_atual = now.strftime("%d/%m/%Y %H:%M")
    return data_hora_atual


def data_atual():
    # Define o fuso horário GMT-3
    fuso_horario = pytz.timezone("America/Sao_Paulo")
    # Obtém a data e hora atual no fuso horário especificado
    now = datetime.now(fuso_horario)
    # Formata no estilo dd-mm-yyyy hh:mm
    data_hora_atual = now.strftime("%d/%m/%Y")
    return data_hora_atual