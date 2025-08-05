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

    df_acompanhamento = obter_dados_acompanhamento()

    if len(df_acompanhamento) == 0:
        st.warning("Ainda não há registros 👀")
        st.stop()

    df_acompanhamento = dados_analise_meta()

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
    df_acompanhamento['Data'] = pd.to_datetime(df_acompanhamento['Data'], format='%d/%m/%Y %H:%M')
    
    # Substituir True/False por emojis
    df_acompanhamento['Meta Atingida'] = df_acompanhamento['Meta Atingida'].apply(lambda x: '✅' if x else '❌')

    df_acompanhamento = df_acompanhamento.sort_values(by='Data', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        # Filtros
        filtro_nome = st.multiselect("Nome", options=dados_nomes_select(), placeholder="Filtro por nome")

    # Filtro de intervalo de data
    data_min = df_acompanhamento['Data'].min().date()
    data_max = df_acompanhamento['Data'].max().date()
    with col2:
        filtro_data = st.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max, format='DD/MM/YYYY')

    # Aplica filtros
    df_filtrado = df_acompanhamento.copy()

    # Filtro por nome
    if filtro_nome:
        df_filtrado = df_filtrado[df_filtrado['Nome'].isin(filtro_nome)]

    # Filtro por data
    if isinstance(filtro_data, tuple) and len(filtro_data) == 2:
        data_inicio, data_fim = filtro_data
        df_filtrado = df_filtrado[(df_filtrado['Data'].dt.date >= data_inicio) & (df_filtrado['Data'].dt.date <= data_fim)]

    df_filtrado['Data'] = df_filtrado['Data'].dt.strftime('%d/%m/%Y %H:%M')

    # Exibição
    st.dataframe(
        df_filtrado.rename(columns={"Quantidade": "Quantidade (litros)", "Meta": "Meta (litros)"}),
        use_container_width=True,
        hide_index=True,
        row_height=80,
        column_config={
            'Foto': st.column_config.ImageColumn(width="small")
        },
        column_order=["Foto", "Nome", "Data", "Quantidade (litros)"]
    )