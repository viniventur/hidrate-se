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


def conferir_meta(nome, data_registro):
    df_acompanhamento = dados_analise_meta()

    # Garantir que Data seja datetime
    df_acompanhamento['Data'] = pd.to_datetime(df_acompanhamento['Data'], errors='coerce')
    
    # Extrair só a data (ignorar hora/minuto)
    df_acompanhamento['Data'] = df_acompanhamento['Data'].dt.date
    data_registro = pd.to_datetime(data_registro).date()

    # Calcular Faltante
    df_acompanhamento['Faltante'] = df_acompanhamento['Meta'] - df_acompanhamento['Quantidade']

    # Filtrar por nome e dia
    df_filtrado = df_acompanhamento.loc[
        (df_acompanhamento['Nome'] == nome) &
        (df_acompanhamento['Data'] == data_registro)
    ]

    if df_filtrado.empty:
        return None, None

    # Padronizar para 2 casas decimais e trocar . por ,
    faltante = f"{df_filtrado['Faltante'].iloc[0]:.2f}".replace('.', ',')
    quantidade = f"{df_filtrado['Quantidade'].iloc[0]:.2f}".replace('.', ',')

    return faltante, quantidade

def main():

    if 'aviso_duplicata' not in st.session_state:
        st.session_state.aviso_duplicata = False

    if 'faltante_meta' not in st.session_state:
        st.session_state.faltante_meta = False

    if 'quantidade' not in st.session_state:
        st.session_state.quantidade = False

    if 'pergunta_confirmacao' not in st.session_state:
        st.session_state.pergunta_confirmacao = False

    if 'confirmacao' not in st.session_state:
        st.session_state.confirmacao = False

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

    with st.expander('Quantos litros de água diária preciso beber para manter esse corpinho bem hidratado? 😂💦', expanded=False):
        st.write("Métrica: 35 ml por quilo de peso.")

        peso = st.number_input('Qual o seu peso? (kg)', step=1.00, min_value=00.00)

        if st.button("Calcular :material/calculate:"):
            st.success(f'Você precisa beber {ml_para_litros(peso*35):.2f}'.replace('.', ',') + ' litros (de água... 😏) por dia! :material/water_full:')

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
                qnt_bebida = st.number_input('Quantidade bebida (LITROS)', step=0.25, min_value=0.00)

            select_qnd_bebeu = st.radio('Quando você bebeu essa quantidade?', options=[f'Hoje ({data_atual()})', 'Outro dia'], horizontal=True)

            if select_qnd_bebeu == 'Outro dia':
                data_registro = st.date_input('Em que dia você bebeu essa quantidade?', format='DD/MM/YYYY', max_value=datetime.now(pytz.timezone("America/Sao_Paulo")))
                #data_registro = padronizar_data(data_registro)
                hora_registro = st.time_input('Que horas?')

                # Junta os dois em um datetime completo
                data_hora_registro = datetime.combine(data_registro, hora_registro)

                # Formata no padrão desejado: dd/mm/yyyy HH:MM
                data_hora_registro = data_hora_registro.strftime('%d/%m/%Y %H:%M')
            else:
                data_hora_registro = data_hr_atual()

            if st.session_state.pergunta_confirmacao == True:

                st.warning('Esta quantidade é muito alta, tem certeza que deseja registrar? (ou esqueceu de converter para litros? 👀)')

                if st.button('Confirmar! Bebi muito!'):
                    st.session_state.confirmacao = True
                    st.rerun()

            if st.session_state.confirmacao == True:
                novo_registro(nome, data_hora_registro, qnt_bebida)
                st.session_state.registro_feito = True
                st.session_state.confirmacao = False
                st.session_state.pergunta_confirmacao = False
                st.cache_data.clear()
                st.session_state.faltante_meta, st.session_state.quantidade = conferir_meta(nome, data_hora_registro)
                st.rerun()   
            
            botao_enviar = st.button('Enviar :material/check_box:', use_container_width=True)

            if botao_enviar:

                if nome == '':
                    st.error('Selecione o servidor.')
                elif qnt_bebida == 0:
                    st.error('Insira a quantidade.')
                elif qnt_bebida > 6:
                    st.session_state.pergunta_confirmacao = True         
                else:
                    novo_registro(nome, data_hora_registro, qnt_bebida)
                    st.session_state.registro_feito = True
                    st.cache_data.clear()
                    st.session_state.faltante_meta, st.session_state.quantidade = conferir_meta(nome, data_hora_registro)
                    st.rerun()
        
        if st.session_state.registro_feito == True:
            st.success(':material/water_full: Registro enviado com sucesso!')
            if float(st.session_state.faltante_meta.replace(',', '.')) <= 0:
                st.success("Parabéns! Você bateu a meta diária!")
                st.write(f"Quantidade bebida hoje: {st.session_state.quantidade} litros")
                st.balloons()
            else:
                st.warning(f"Quase lá! Faltam {st.session_state.faltante_meta} litros para bater a meta! 🏃‍♂️‍➡️")

            if st.button("Clique para realizar outro registro :material/replay:", use_container_width=True):
                st.session_state.registro_feito = False
                st.rerun()

    with st.expander('Não sabe quanto bebeu em litros? Calcule aqui ➗', expanded=False):
        qnt_ml = st.number_input('Quantidade em mililitros (ml):', step=50.00, min_value=00.00)

        if qnt_ml != 0:
            st.success(f'Essa quantidade equivale a {ml_para_litros(qnt_ml):.2f} litros!'.replace('.', ','))

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100px; text-align: center;">
            <h1 style="font-size: 35px; margin: 0; color: #005CA8;">Ranking</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    analise_ranking()


            
if __name__ == "__main__":
    main()