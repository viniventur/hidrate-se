import pandas as pd
import time
import json
import pytz 
import plotly
import datetime
import streamlit as st
from dotenv import load_dotenv, dotenv_values
env = dotenv_values('.env')

from utils import *
from sidebar import *

import warnings
warnings.filterwarnings('ignore')


def analise_ranking():

    col1, col2 = st.columns(2)

    with col1:

        st.write(obter_dados_acompanhamento())
        st.write('analise')
