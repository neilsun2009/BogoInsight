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
        
st.write('Play with data chosen from the sidebar on the left.')

# sidebar
data_sources = []
with st.sidebar:
    with st.spinner('Loading available data...'):
        data_sources = get_data_sources()
        st.toast('Data updated.', icon='✅')
    sel_data_sources = st.multiselect(
        f'🎯Select data sources (max. {MAX_DS_SELECTION})',
        data_sources,
        format_func=lambda d:f"{d['category']} ({d['name']})",
        max_selections=MAX_DS_SELECTION,
    )
    st.button('Reload data', on_click=lambda: st.cache_data.clear())

if len(sel_data_sources) == 0:
    st.warning('Please select at least 1 data source.', icon='🚨')
else:
    dfs = [load_df(ds['path']) for ds in sel_data_sources]
    # indivisual data source display
    st.header('📎Indivisual data source display')
    tabs = st.tabs([f"{d['category']} ({d['name']})" for d in sel_data_sources])
    for idx, tab in enumerate(tabs):
        with tab:
            # get df
            df = dfs[idx]
            
            if st.checkbox('Show raw data', key=f"show_raw_data_{idx}"):
                st.dataframe(df)
            
            # select columns
            y_columns = [col for col in df.columns if col not in ['period']]
            sel_columns = st.multiselect(
                '📊Select columns to display',
                y_columns,
                default=y_columns,
                key=f"sel_columns_{idx}"
            )
            
            # line chart        
            fig = px.line(df, 
                        title='📈Line chart on columns',
                        x='period', 
                        y=sel_columns, 
                        markers=False,
                        labels={"value": "value", "variable": "category"},
                        )
            update_line_chart(fig)
            
            # heatmap for correlation
            corr_matrix = df[sel_columns].corr(numeric_only=True)
            heatmap = gen_heatmap(corr_matrix, 
                                  title='🔥Heatmap for correlation',)
            
            # show charts
            st.plotly_chart(fig, theme="streamlit")
            st.plotly_chart(heatmap, theme="streamlit")
            
    # combination of multiple data sources
    st.header('🖇️Combination of multiple data sources')
    st.write('Only data sources containing column `period` will be combined.')
    # Filter dfs by containing column 'period'
    dfs_with_period = [df.set_index('period') for df in dfs if 'period' in df.columns]

    if len(dfs_with_period) < 2:
        st.warning('Please select at least 2 data sources with a column named "period".', icon='🚨')
    else:
        # Combine data sources
        merged_df = dfs_with_period[0]
        for df in dfs_with_period[1:]:
            merged_df = merged_df.join(df, on='period', how='outer', sort=True)
        if 'period' in merged_df.columns:
            merged_df.set_index('period', inplace=True)
        if st.checkbox('Show combined raw data'):
            st.write(merged_df)
            
        # select columns
        y_columns = [col for col in merged_df.columns if col not in ['period']]
        sel_columns = st.multiselect(
            '📊Select columns to display',
            y_columns,
            default=y_columns,
        )
        selected_df = merged_df[sel_columns]
        
        # select period range
        start_period, end_period = st.select_slider(
            '🗓️Select period range',
            options = selected_df.index,
            value = (selected_df.index.min(), selected_df.index.max())
        )
        selected_df = selected_df.loc[start_period:end_period]
        
        # line chart        
        fig = px.line(selected_df, 
                    title='📈Combined line chart on columns',
                    # y=sel_columns, 
                    markers=False,
                    labels={"value": "value", "variable": "category"},)
        update_line_chart(fig)
        
        # heatmap for correlation
        corr_matrix = selected_df[sel_columns].corr(numeric_only=True)
        heatmap = gen_heatmap(corr_matrix, 
                            title='🔥Heatmap for correlation',)

        st.plotly_chart(fig, theme="streamlit")
        st.plotly_chart(heatmap, theme="streamlit")