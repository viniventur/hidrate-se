import pandas as pd
import time
import json
import pytz 
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils import *
from sidebar import *

import warnings
warnings.filterwarnings('ignore')


st.set_page_config(page_title=nome_pag_title(), page_icon=img_pag_icon(), layout='centered')

def main():

    if 'aviso_duplicata' not in st.session_state:
        st.session_state.aviso_duplicata = False

    logo_path= 'src/assets/logo_hidratese.png'
    logo_base64 = get_image_as_base64(logo_path)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 130px;">
            <img src="data:image/png;base64,{logo_base64}" style="margin-right: 35px; width: 350px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander('Quantos litros preciso beber para bater a meta? (de água... 😏)', expanded=False):
        st.write("Métrica: 35 ml por quilo de peso.")

        peso = st.number_input('Qual o seu peso? (kg)', step=1.00, min_value=00.00)

        if st.button("Calcular :material/calculate:"):
            st.success(f'Você precisa beber {ml_para_litros(peso*35):.2f} litros de água por dia! :material/water_full:'.replace('.', ','))

    with st.expander('Calculadora de litros', expanded=False):
        qnt_ml = st.number_input('Quantidade em mililitros (ml):', step=50.00, min_value=00.00)

        if qnt_ml != 0:
            st.success(f'Essa quantidade equivale a {ml_para_litros(qnt_ml):.2f} litros!'.replace('.', ','))

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
                qnt_bebida = st.number_input('Quantidade bebida (litros)', step=0.25, min_value=0.00)

            select_qnd_bebeu = st.radio('Quando você bebeu essa quantidade?', options=[f'Hoje ({data_atual()})', 'Outro dia'], horizontal=True)

            if select_qnd_bebeu == 'Outro dia':
                data_registro = st.date_input('Em que dia você bebeu essa quantidade?', format='DD/MM/YYYY', max_value=datetime.now(pytz.timezone("America/Sao_Paulo")))
                data_registro = padronizar_data(data_registro)
            else:
                data_registro = data_atual()
            
            botao_enviar = st.button('Enviar :material/check_box:', use_container_width=True)

            if botao_enviar:

                if nome == '':
                    st.error('Selecione o servidor.')
                elif qnt_bebida == 0:
                    st.error('Insira a quantidade.')
                elif (len(conferir_registro_duplicado(nome, data_registro)) > 0) & (st.session_state.aviso_duplicata == False):
                    st.warning("Você já realizou um registro nesta data 👇")
                    st.dataframe(conferir_registro_duplicado(nome, data_registro), use_container_width=True, hide_index=True)
                    st.warning("Se deseja realizar outro registro, clique enviar novamente para confirmar.")
                    st.session_state.aviso_duplicata = True

                    botao_cancelar = st.button('Cancelar :material/cancel:', use_container_width=True, key="botao_cancelar_registro")

                    if botao_cancelar:
                        st.rerun()
                else:
                    novo_registro(nome, data_registro, qnt_bebida)
                    st.session_state.msg_registro_feito = st.success(':material/water_full: Registro enviado com sucesso!')
                    st.session_state.registro_feito = True
                    st.session_state.aviso_duplicata = False
                    st.cache_data.clear()
                    st.rerun()
        
        if st.session_state.registro_feito == True:
            st.success(':material/water_full: Registro enviado com sucesso!')
            if st.button("Clique para realizar outro registro :material/replay:", use_container_width=True):
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

    analise_ranking()


            
if __name__ == "__main__":
    main()