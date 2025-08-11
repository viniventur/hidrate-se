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

    df_meta = dados_analise_meta()

    # 2. Filtrar quem bateu a meta
    df_meta = df_meta[df_meta['Meta Atingida']]

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
        yaxis=dict(
            tickmode='linear',
            tickfont=dict(size=16)  # <-- aumenta o tamanho do texto do eixo Y aqui
        ),
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

    ########## gráfico de linha - consumo médio diário ##########

    df_media_diaria = df_acompanhamento.copy()

    # Garantir que Data seja datetime
    df_media_diaria['Data'] = pd.to_datetime(df_media_diaria['Data'], dayfirst=True, errors='coerce')

    # Remover registros inválidos
    df_media_diaria = df_media_diaria.dropna(subset=['Data', 'Quantidade'])

    # Considerar apenas o dia (ignorar hora/minuto)
    df_media_diaria['Data'] = df_media_diaria['Data'].dt.date

    # Calcular média de Quantidade por data
    df_media_diaria = (
        df_media_diaria
        .groupby('Data', as_index=False)
        .agg(Quantidade=('Quantidade', 'mean'))
    )

    # Formatar quantidade com 2 casas decimais e vírgula
    df_media_diaria['Quantidade_formatada'] = df_media_diaria['Quantidade'].map(lambda x: f"{x:.2f}".replace('.', ','))

    # Cria gráfico com rótulos formatados
    fig = px.line(
        df_media_diaria,
        x='Data',
        y='Quantidade',
        markers=True,
        text=df_media_diaria['Quantidade_formatada'],
        title='Consumo médio diário da equipe (litros)'
    )

    fig.update_traces(
        textposition='top center',
        textfont_size=12
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Média de consumo (litros)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


    st.markdown("##### Tabela completa de registros")

    df_meta = dados_analise_meta_diaria()

    # Formatar Data
    df_meta['Data'] = pd.to_datetime(df_meta['Data'], format='%d/%m/%Y %H:%M')
    
    # Substituir True/False por emojis
    df_meta['Meta Atingida'] = df_meta['Meta Atingida'].apply(lambda x: '✅' if x else '❌')

    df_meta = df_meta.sort_values(by='Data', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        # Filtros
        filtro_nome = st.multiselect("Nome", options=dados_nomes_select(), placeholder="Filtro por nome")

    # Filtro de intervalo de data
    data_min = df_meta['Data'].min().date()
    data_max = df_meta['Data'].max().date()
    with col2:
        filtro_data = st.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max, format='DD/MM/YYYY')

    # Aplica filtros
    df_filtrado = df_meta.copy()

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