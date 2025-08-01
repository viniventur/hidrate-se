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

def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")
    

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

