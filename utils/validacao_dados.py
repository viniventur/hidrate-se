import os
from dotenv import load_dotenv, dotenv_values
import streamlit as st
from datetime import datetime
import pytz
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter
import base64
import re
import time
env = dotenv_values('.env')

def padronizar_data(data):
    return data.strftime("%d/%m/%Y")

def num_processo_sei(processo):
    """Filtra e padroniza números de processos SEI."""
    padrao = r"E:\d{5}\.\d{10}/\d{4}"
    processo_sei_format = re.search(padrao, processo).group()
    return processo_sei_format

def tratar_processos_input(input_text):
    """Remove espaços extras e formata os números de processo."""
    linhas = input_text.strip().splitlines()
    linhas_tratadas = [re.sub(r'\s+', '', linha) for linha in linhas if linha.strip()]
    resultado = "\n".join(linhas_tratadas)
    return resultado, len(linhas_tratadas)

def extrair_nome_sei(string):
    # Divide a string na primeira ocorrência do parêntese
    nome = string.split('(')[0]
    # Remove espaços extras no início ou fim
    return nome.strip()

def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def validacao_cpf(cpf):
    """Valida um CPF."""
    # Retira apenas os dígitos do CPF, ignorando os caracteres especiais
    numeros = [int(digito) for digito in cpf if digito.isdigit()]

    validacao1 = False
    validacao2 = False

    soma_produtos = sum(a*b for a, b in zip (numeros[0:9], range (10, 1, -1)))
    digito_esperado = (soma_produtos * 10 % 11) % 10
  
    if numeros[9] == digito_esperado:
        validacao1 = True

    soma_produtos1 = sum(a*b for a, b in zip(numeros [0:10], range (11, 1, -1)))
    digito_esperado1 = (soma_produtos1 *10 % 11) % 10

    if numeros[10] == digito_esperado1:
        validacao2 = True
        
    if  validacao1 == True and validacao2 == True:
        return True
    else:
        return False
    

def converter_para_excel(df_processos, nome_aba):
    """Converte DataFrame para um arquivo Excel formatado."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_processos.to_excel(writer, index=False, sheet_name=nome_aba)
        worksheet = writer.sheets[nome_aba]
        for col_idx, column in enumerate(df_processos.columns, start=1):
            max_length = max(df_processos[column].astype(str).map(len).max(), len(column)) + 2
            col_letter = get_column_letter(col_idx)
            worksheet.column_dimensions[col_letter].width = max_length
    output.seek(0)
    return output.getvalue()

# Contagem de dias entre datas do sei

def cont_dias(data_x, data_y):
    """
    Calcula a diferença em dias entre duas datas.

    Parâmetros:
        data_x (str ou datetime): Primeira data, aceita string no formato "%d/%m/%Y %H:%M" ou objeto datetime.
        data_y (str ou datetime): Segunda data, aceita string no formato "%d/%m/%Y %H:%M" ou objeto datetime.

    Retorna:
        int: Diferença em dias entre as duas datas.
    """
    # Verificar e converter data_x, se necessário
    if isinstance(data_x, str):
        data_x = datetime.strptime(data_x, "%d/%m/%Y %H:%M")
    elif not isinstance(data_x, datetime):
        raise ValueError("data_x deve ser uma string ou um objeto datetime.")

    # Verificar e converter data_y, se necessário
    if isinstance(data_y, str):
        data_y = datetime.strptime(data_y, "%d/%m/%Y %H:%M")
    elif not isinstance(data_y, datetime):
        raise ValueError("data_y deve ser uma string ou um objeto datetime.")

    # Calcular a diferença em dias
    diferenca = (data_y - data_x).days

    return diferenca

# Tratamento e verificacoes de dados de acesso
def tratamento_verif_users(add_df, df_usuarios):

    add_df = add_df[add_df["CPF"] != "Insira o CPF"]

    if len(add_df) < 1:
        st.error('Insira ao menos 1 CPF para adicionar usuários.')
        return None
    
    # Verificar se o orgao foi inserido
    orgao_teste_df = add_df[add_df["ORGAO"] != "Selecione o Orgão"]
    if len(orgao_teste_df) < 1:
        st.error('Usuários sem órgão informado:')
        st.dataframe(
            add_df.loc[add_df["ORGAO"] == "Selecione o Orgão", ['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']],
            use_container_width=True,
            hide_index=True
        )
        return None

    # Verificar se um usuario possui dois registros com 2 orgaos diferentes
    duplicados_diferentes_orgao = add_df.groupby('CPF')['ORGAO'].nunique()
    cpf_diferentes = duplicados_diferentes_orgao[duplicados_diferentes_orgao > 1].index
    if not cpf_diferentes.empty:
        st.error('CPF duplicados com órgãos diferentes:')
        st.dataframe(
            add_df[add_df['CPF'].isin(cpf_diferentes)][['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']].sort_values(by='CPF'),
            use_container_width=True,
            hide_index=True
        )
        return None


    # Verifica usuarios sem apelidos
    apelido_teste_df = add_df[(add_df["APELIDO"].str.strip() == "Insira um Apelido") | 
                                (add_df["APELIDO"].str.strip() == "") | 
                                (add_df["APELIDO"] == " ")]
    if len(apelido_teste_df) > 0 :
        st.error('Usuários sem apelidos informado:')
        st.dataframe(
            add_df.loc[(add_df["APELIDO"].str.strip() == "Insira um Apelido") | 
                        (add_df["APELIDO"].str.strip() == "") | 
                        (add_df["APELIDO"] == " "),
                        ['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']],
            use_container_width=True,
            hide_index=True
        )
        return None


    # Validação de CPF
    add_df["CPF_VALIDACAO"] = add_df["CPF"].apply(validacao_cpf)
    if any(~add_df["CPF_VALIDACAO"]):
        st.error('Os dados contêm CPFs inválidos:')
        st.dataframe(
            add_df.loc[~add_df["CPF_VALIDACAO"], ['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']],
            use_container_width=True,
            hide_index=True
        )
        return None

    # Verifica duplicados com acessos diferentes
    duplicados_diferentes_cpf = add_df.groupby('CPF')['ACESSO'].nunique()
    cpf_diferentes = duplicados_diferentes_cpf[duplicados_diferentes_cpf > 1].index
    if not cpf_diferentes.empty:
        st.error('CPF duplicados com acessos diferentes:')
        st.dataframe(
            add_df[add_df['CPF'].isin(cpf_diferentes)][['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']].sort_values(by='CPF'),
            use_container_width=True,
            hide_index=True
        )
        return None
    
    # Verifica duplicados com acessos gerais diferentes
    duplicados_diferentes_cpf_gerais = add_df.groupby('CPF')['ACESSO_GERAL'].nunique()
    cpf_diferentes_gerais = duplicados_diferentes_cpf_gerais[duplicados_diferentes_cpf_gerais > 1].index
    if not cpf_diferentes_gerais.empty:
        st.error('CPF duplicados com acessos gerais diferentes:')
        st.dataframe(
            add_df[add_df['CPF'].isin(cpf_diferentes_gerais)][['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']].sort_values(by='CPF'),
            use_container_width=True,
            hide_index=True
        )
        return None

    # Verificar duplicidade na base de dados
    if add_df["CPF"].isin(df_usuarios["CPF"]).any():
        st.error("Os CPFs abaixo já constam na base.")
        st.dataframe(
            add_df.loc[add_df["CPF"].isin(df_usuarios["CPF"])][['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']],
            use_container_width=True,
            hide_index=True
        )
        return None

    return add_df.drop_duplicates(subset=['CPF'])[['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']]



def tratamento_verif_users_alteracao(edit_df, df_selecionados_edit_users, df_usuarios):
    """
    Função para tratamento e verificação de dados de usuários alterados.
    """
    # Verificar se houve alteração nos dados
    colunas_verificacao = ['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']
    if df_selecionados_edit_users[colunas_verificacao].equals(edit_df[colunas_verificacao]):
        st.error('Não há alterações.')
        return None
    
    # Verificar se há usuários sem órgão informado
    usuarios_sem_orgao = edit_df[edit_df["ORGAO"] == "Selecione o Orgão"]
    if not usuarios_sem_orgao.empty:
        st.error('Usuários sem órgão informado:')
        st.dataframe(usuarios_sem_orgao[colunas_verificacao], use_container_width=True, hide_index=True)
        return None
    
    # Verificar CPFs duplicados com órgãos diferentes
    cpf_duplicados_orgao = edit_df.groupby('CPF')['ORGAO'].nunique()
    cpfs_com_orgaos_diferentes = cpf_duplicados_orgao[cpf_duplicados_orgao > 1].index
    if not cpfs_com_orgaos_diferentes.empty:
        st.error('CPF duplicados com órgãos diferentes:')
        st.dataframe(edit_df[edit_df['CPF'].isin(cpfs_com_orgaos_diferentes)][colunas_verificacao].sort_values(by='CPF'), 
                     use_container_width=True, hide_index=True)
        return None
    
    # Verificar usuários sem apelidos
    usuarios_sem_apelido = edit_df[edit_df["APELIDO"].str.strip().isin(["Insira um Apelido", "", " "])]
    if not usuarios_sem_apelido.empty:
        st.error('Usuários sem apelidos informados:')
        st.dataframe(usuarios_sem_apelido[colunas_verificacao], use_container_width=True, hide_index=True)
        return None
    
    # Verificar se o CPF foi alterado
    if not edit_df['CPF'].equals(df_selecionados_edit_users['CPF']):
        df_cpf_alterado = edit_df[~edit_df['CPF'].isin(df_selecionados_edit_users['CPF'])]
        
        # Validação de CPF
        df_cpf_alterado["CPF_VALIDACAO"] = df_cpf_alterado["CPF"].apply(validacao_cpf)
        if any(~df_cpf_alterado["CPF_VALIDACAO"]):
            st.error('Os dados contêm CPFs inválidos:')
            st.dataframe(
                df_cpf_alterado.loc[~df_cpf_alterado["CPF_VALIDACAO"], ['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']],
                use_container_width=True,
                hide_index=True
            )
            return None
                
        # Verificar CPFs duplicados com acessos diferentes
        cpf_duplicados_acesso = df_cpf_alterado.groupby('CPF')['ACESSO'].nunique()
        cpfs_com_acessos_diferentes = cpf_duplicados_acesso[cpf_duplicados_acesso > 1].index
        if not cpfs_com_acessos_diferentes.empty:
            st.error('CPF duplicados com acessos diferentes:')
            st.dataframe(df_cpf_alterado[df_cpf_alterado['CPF'].isin(cpfs_com_acessos_diferentes)][colunas_verificacao].sort_values(by='CPF'), 
                         use_container_width=True, hide_index=True)
            return None
        
        # Verificar CPFs duplicados com acessos gerais diferentes
        cpf_duplicados_acesso_geral = df_cpf_alterado.groupby('CPF')['ACESSO_GERAL'].nunique()
        cpfs_com_acessos_gerais_diferentes = cpf_duplicados_acesso_geral[cpf_duplicados_acesso_geral > 1].index
        if not cpfs_com_acessos_gerais_diferentes.empty:
            st.error('CPF duplicados com acessos gerais diferentes:')
            st.dataframe(df_cpf_alterado[df_cpf_alterado['CPF'].isin(cpfs_com_acessos_gerais_diferentes)][colunas_verificacao].sort_values(by='CPF'), 
                         use_container_width=True, hide_index=True)
            return None
        
        # Verificar duplicidade na base de dados
        cpfs_ja_cadastrados = df_cpf_alterado[df_cpf_alterado["CPF"].isin(df_usuarios["CPF"])]
        if not cpfs_ja_cadastrados.empty:
            st.error("Os CPFs alterados abaixo já constam na base.")
            st.dataframe(cpfs_ja_cadastrados[colunas_verificacao], use_container_width=True, hide_index=True)
            return None

            
    return edit_df.drop_duplicates(subset=['CPF'])[['CPF', 'APELIDO', 'ORGAO', 'ACESSO', 'ACESSO_GERAL']]