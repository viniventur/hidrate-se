import pandas as pd
import time
import json
import pytz 
import datetime
import plotly.express as px
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
    df_pessoal.drop(columns=["Nome"], inplace=True)
    df_pessoal.rename(columns={"nome_padronizado": "Nome"}, inplace=True)

    df_acompanhamento = obter_dados_acompanhamento()

    if len(df_acompanhamento) == 0:
        st.warning("Ainda não há registros 👀")
        st.stop()

    df_acompanhamento['Data'] = pd.to_datetime(df_acompanhamento['Data'], dayfirst=True)

    # Agrupa por pessoa e data, somando a quantidade do dia
    df_acompanhamento = df_acompanhamento.groupby(['Nome', 'Data'], as_index=False)['Quantidade'].sum()

    # Cria coluna de meta atingida com base no peso corporal
    df_acompanhamento = df_acompanhamento.merge(
        df_pessoal[['Nome', 'Foto', 'Peso']],  # seleciona só as colunas que precisa
        on='Nome',
        how='left'
    )

    df_acompanhamento['Meta'] = ml_para_litros(df_acompanhamento['Peso'] * 35)

    df_acompanhamento['Meta Atingida'] = df_acompanhamento['Quantidade'] >= df_acompanhamento['Meta']

    # Formata a data para exibição
    df_acompanhamento['Data'] = df_acompanhamento['Data'].dt.strftime('%d/%m/%Y')

    # 2. Filtrar quem bateu a meta
    df_meta = df_acompanhamento[df_acompanhamento['Meta Atingida']]

    # 3. Contar quantas vezes cada pessoa bateu a meta
    ranking = df_meta['Nome'].value_counts().reset_index()
    ranking.columns = ['Nome', 'Quantidade de Metas Batidas']
    ranking = ranking.sort_values('Quantidade de Metas Batidas', ascending=True)

    # Ordena o ranking (caso ainda não esteja)
    ranking = ranking.sort_values(by='Quantidade de Metas Batidas', ascending=False).reset_index(drop=True)

    # Adiciona os emojis nos 3 primeiros
    emojis = ['🥇', '🥈', '🥉']
    for i in range(min(3, len(ranking))):
        ranking.loc[i, 'Nome'] = f"{emojis[i]} {ranking.loc[i, 'Nome']}"

    ranking = ranking.sort_values('Quantidade de Metas Batidas', ascending=True)

    # 4. Gráfico com Plotly
    fig = px.bar(
        ranking,
        x='Quantidade de Metas Batidas',
        y='Nome',
        orientation='h',
        text='Quantidade de Metas Batidas',
        title='Ranking de quem mais bateu a meta',
        color='Quantidade de Metas Batidas'
    )

    fig.update_layout(
        xaxis_title='Quantidade de vezes que bateu a meta',
        yaxis_title='',
        yaxis=dict(tickmode='linear'),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    # Aumenta tamanho da fonte dos rótulos e ajusta cor do marcador
    fig.update_traces(
        textposition='outside',
        textfont_size=16,  # <-- aumenta aqui o tamanho dos rótulos
        marker_color='#005CA8'
    )

    st.plotly_chart(fig, use_container_width=True)

    ########## gráfico de linha ################

    df_acompanhamento['Data'] = pd.to_datetime(df_acompanhamento['Data'], dayfirst=True, errors='coerce')

    # Remove registros com datas inválidas ou quantidade faltante
    df_acompanhamento = df_acompanhamento.dropna(subset=['Data', 'Quantidade'])

    # Agrupa por Nome e Data (caso haja duplicidade no mesmo dia)
    df_agg = df_acompanhamento.groupby(['Nome', 'Data'], as_index=False)['Quantidade'].sum()

    # Cria gráfico
    fig = px.line(
        df_agg,
        x='Data',
        y='Quantidade',
        color='Nome',
        markers=True,
        title='Evolução diária de consumo por pessoa'
    )

    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Quantidade (litros)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_title='Pessoa'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Tabela completa de registros")

    # Formatar Data
    df_acompanhamento['Data'] = pd.to_datetime(df_acompanhamento['Data']).dt.strftime('%d/%m/%Y')

    # Substituir True/False por emojis
    df_acompanhamento['Meta Atingida'] = df_acompanhamento['Meta Atingida'].apply(lambda x: '✅' if x else '❌')

    df_acompanhamento = df_acompanhamento.sort_values(by='Data', ascending=False)


    filtro_nome = st.multiselect("Nome", options=dados_nomes_select(), placeholder="Filtro por nome")

    if filtro_nome:

        df_acompanhamento_filtrado = df_acompanhamento.loc[df_acompanhamento['Nome'].isin(filtro_nome)]

        # Exibir na interface
        st.dataframe(df_acompanhamento_filtrado.rename(columns={"Quantidade": "Quantidade (litros)", "Meta": "Meta (litros)"}),
                    use_container_width=True, 
                    hide_index=True,
                    row_height=80,
                    column_config={
                        'Foto': st.column_config.ImageColumn(width="small")
                    },
                    column_order=["Foto", "Nome", "Data", "Quantidade (litros)", "Meta (litros)", "Meta Atingida"])
    else:
        # Exibir na interface
        st.dataframe(df_acompanhamento.rename(columns={"Quantidade": "Quantidade (litros)", "Meta": "Meta (litros)"}),
                    use_container_width=True, 
                    hide_index=True,
                    row_height=80,
                    column_config={
                        'Foto': st.column_config.ImageColumn(width="small")
                    },
                    column_order=["Foto", "Nome", "Data", "Quantidade (litros)", "Meta (litros)", "Meta Atingida"])
