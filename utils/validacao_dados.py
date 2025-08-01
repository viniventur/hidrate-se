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
