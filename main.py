import pandas as pd
import time
import json
import pytz 
import datetime
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils import *
from sidebar import *

import warnings
warnings.filterwarnings('ignore')


st.set_page_config(page_title=nome_pag_title(), page_icon=img_pag_icon(), layout='centered')

@st.cache_data(show_spinner=False)
def dados_nomes_select():
        
    data = obter_dados_pessoal()

    # Cria uma linha com espaço em branco para todas as colunas
    linha_em_branco = {col: "" for col in data.columns}

    # Adiciona a nova linha
    data = pd.concat([pd.DataFrame([linha_em_branco]), data], ignore_index=True)

    return data

# Config Layout (condicional de local ou online)

def main():

    logo_path= 'src/assets/logo_governanca.png'
    logo_base64 = get_image_as_base64(logo_path)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 80px;">
            <img src="data:image/png;base64,{logo_base64}" style="margin-right: 35px; width: 500px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100px; text-align: center;">
            <h1 style="font-size: 35px; margin: 0; color: #005CA8;">Hidrate-se</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("Descrição breve do programa")

    form_container = st.container(border=True)

    with form_container:
        
        if 'registro_feito' not in st.session_state:
            st.session_state.registro_feito = False


        if st.session_state.registro_feito == False:

            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; align-items: center; height: 50px; text-align: center;">
                    <h1 style="font-size: 20px; margin: 0; color: #005CA8;">Bebeu Água? Registre aqui 👇</h1>
                </div>
                """,
                unsafe_allow_html=True
            )
            

            col1, col2 = st.columns(2)

            with col1:
                nome = st.selectbox('Nome', options=dados_nomes_select())

            with col2:
                qnt_bebida = st.number_input('Quantidade bebida (litros)')

            select_qnd_bebeu = st.radio('Quando você bebeu essa quantidade?', options=[f'Hoje ({data_atual()})', 'Outro dia'], horizontal=True)

            if select_qnd_bebeu == 'Outro dia':
                data_registro = st.date_input('Em que dia você bebeu essa quantidade?', format='DD/MM/YYYY')
                data_registro = padronizar_data(data_registro)
            else:
                data_registro = data_atual()
            
            botao_enviar = st.button('Enviar', use_container_width=True)

            if botao_enviar:

                if nome == '':
                    st.error('Selecione o servidor.')
                elif qnt_bebida == 0:
                    st.error('Insira a quantidade.')
                else:
                    st.session_state.msg_registro_feito = st.success(':material/water_full: Registro enviado com sucesso!')
                    st.session_state.registro_feito = True
                    st.rerun()
        
        if st.session_state.registro_feito == True:
            st.success(':material/water_full: Registro enviado com sucesso!')
            if st.button("Clique para realizar outro registro", use_container_width=True):
                st.session_state.registro_feito = False
                st.rerun()


    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100px; text-align: center;">
            <h1 style="font-size: 35px; margin: 0; color: #005CA8;">Acompanhamento</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write('criacao da planilha base de dados, conexao da planilha de RH para obter os servidores, ideias dos graficos e ranking com imagens')


    st.write(obter_dados_pessoal())
            
if __name__ == "__main__":
    main()