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


def conferir_meta(nome, data_registro, quantidade_atual):
    # Base de acompanhamentos
    df = dados_analise_meta()
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    dia = pd.to_datetime(data_registro, dayfirst=True, errors='coerce').date()
    df['Dia'] = df['Data'].dt.date

    # Meta oficial da pessoa
    df_pessoal = obter_dados_pessoal()
    df_pessoal['Peso'] = df_pessoal['Peso'].astype(int)
    df_pessoal['Meta'] = ml_para_litros(df_pessoal['Peso'] * 35)

    pessoa = df_pessoal.loc[df_pessoal['nome_padronizado'] == nome]
    if pessoa.empty:
        # Se por algum motivo o nome não existir na base oficial, evita crash
        meta_oficial = 0.0
    else:
        meta_oficial = float(pessoa['Meta'].iloc[0])

    # Soma do dia (se houver)
    df_user_day = df[(df['Nome'] == nome) & (df['Dia'] == dia)]

    if df_user_day.empty:
        # Fallback: usa somente o que acabou de ser registrado
        qtd_total = float(quantidade_atual)
        faltante = round(meta_oficial - qtd_total, 2)
        return faltante, round(qtd_total, 2)

    # Caso haja registros no dia, usa o agregado do dia
    qtd_total = float(df_user_day['Quantidade'].sum())
    faltante = round(meta_oficial - qtd_total, 2)
    return faltante, round(qtd_total, 2)

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

    if 'nome' not in st.session_state:
        st.session_state.nome = ''

    if 'data_hora_registro' not in st.session_state:
        st.session_state.data_hora_registro = '15/09/2025'

    if 'qnt_bebida_registrada' not in st.session_state:
        st.session_state.qnt_bebida_registrada = 0

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
                st.session_state.nome = nome
                st.session_state.data_hora_registro = data_hora_registro
                st.session_state.qnt_bebida_registrada = qnt_bebida
                st.session_state.registro_feito = True
                st.session_state.confirmacao = False
                st.session_state.pergunta_confirmacao = False
                st.cache_data.clear()
                st.rerun()   
            
            botao_enviar = st.button('Enviar :material/check_box:', use_container_width=True)

            if botao_enviar:

                if nome == '':
                    st.error('Selecione o servidor.')
                elif qnt_bebida == 0:
                    st.error('Insira a quantidade.')
                elif qnt_bebida > 6:
                    st.session_state.pergunta_confirmacao = True
                    st.rerun()         
                else:
                    novo_registro(nome, data_hora_registro, qnt_bebida)
                    st.session_state.nome = nome
                    st.session_state.data_hora_registro = data_hora_registro
                    st.session_state.qnt_bebida_registrada = qnt_bebida
                    st.session_state.registro_feito = True
                    st.cache_data.clear()
                    st.rerun()
        
        if st.session_state.registro_feito == True:
            st.session_state.faltante_meta, st.session_state.quantidade = conferir_meta(
                st.session_state.nome,
                st.session_state.data_hora_registro,
                st.session_state.qnt_bebida_registrada
            )

            st.success(':material/water_full: Registro enviado com sucesso!')

            fmt = lambda x: f"{x:.2f}".replace('.', ',')
            if st.session_state.faltante_meta <= 0:
                st.success("Parabéns! Você bateu a meta diária!")
                st.write(f"Quantidade bebida no dia: {fmt(st.session_state.quantidade)} litros")
                st.balloons()
            else:
                st.warning(f"Quase lá! Faltam {fmt(st.session_state.faltante_meta)} litros para bater a meta! 🏃‍♂️‍➡️")
                st.write(f"Quantidade bebida no dia: {fmt(st.session_state.quantidade)} litros")

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