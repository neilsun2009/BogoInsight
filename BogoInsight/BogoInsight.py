import sys
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from sqlalchemy.exc import OperationalError
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BogoInsight.utils.logger import logger
from BogoInsight.utils.data_utils import (
    get_data_sources, load_df,
)
from BogoInsight.utils.plot_utils import (
    update_line_chart, gen_heatmap
)
from BogoInsight.utils.router import render_toc
# from BogoInsight.database.session import Session, engine

MAX_DS_SELECTION = 3

def check_db_connection():
    # Check connection
    try:
        session = Session()
        logger.info("Checking database connection...")
        with engine.connect() as connection:
            logger.info("Database connection established.")
            return True
    except OperationalError as e:
        logger.error(e)
        logger.error("Database connection could not be established.")
        return False
    finally:
        # Close the session
        session.close()
        
        
st.set_page_config(
    page_title='BogoInsight', 
    page_icon='👀'
)

st.title('👀Welcome to BogoInsight!')

# with st.spinner('Connecting to database...'):
#     if check_db_connection():
#         st.success('Database connection established.')
#     else:
#         st.error('Database connection could not be established.')
        
st.write('''
         A data analysis project. 
         
         Choose topic from the sidebar on the left.''')

# sidebar
with st.sidebar:
    render_toc()
    # st.divider()
    
