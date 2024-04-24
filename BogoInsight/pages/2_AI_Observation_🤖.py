import sys
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.utils.data_utils import (
    get_latest_data_source, load_df,
)
from BogoInsight.utils.plot_utils import (
    update_line_chart, gen_heatmap
)

# data category consts
CAT_NVIDIA_GPU = 'nvidia_gpu_specs'

st.set_page_config(
    page_title='AI Observation - BogoInsight', 
    page_icon='🤖'
)

st.title('🤖AI Observation')

# sidebar
with st.sidebar:
    st.button('Clear all cache', on_click=lambda: st.cache_data.clear())

# get data
ds_nvidia_gpu = get_latest_data_source(CAT_NVIDIA_GPU)
df_nvidia_gpu = load_df(ds_nvidia_gpu['path'])

# set index
df_nvidia_gpu.set_index('model', inplace=True)

# observe GPU specs
with st.container():
    st.header('🛢️NVIDIA GPU over the years')
    
    selectable_columns = [
        'processing power fp32 (TFLOPS)',
        'processing power fp64 (TFLOPS)',
        'processing power fp16 (TFLOPS)',
        'memory (GB)',
        'fab (nm)',
        'TDP (Watts)',
        'bandwidth (GB/s)',
        'CUDA cores',
        'base clock (MHz)',
        'boost clock (MHz)',
    ]
    y_axis_col = st.selectbox('Choose what y-axis shows', selectable_columns, index=0)
    size_col = st.selectbox('Choose what point size shows', selectable_columns, index=3)
    show_model_name = st.toggle('Show model name', value=False)
    
    fig = px.scatter(df_nvidia_gpu,
                     title='🏅NVIDIA GPU model stats',
                     x='period',
                     y=y_axis_col,
                     color='architecture',
                     size=size_col,
                     hover_name=df_nvidia_gpu.index,
                     hover_data=df_nvidia_gpu.columns,
                     text=df_nvidia_gpu.index if show_model_name else None,
                     category_orders={'architecture': ['Pascal', 'Volta', 'Turing', 'Ampere', 'Hopper', 'Ada Lovelace']},
                    )
    fig.update_traces(textposition="bottom center")
    fig.update_layout(legend_title_text=f'Architecture')
    # fig.update_layout(legend=dict(
    #     orientation="h",
    #     yanchor="bottom",
    #     y=1.02,
    #     xanchor="right",
    #     x=1
    # ))
    fig.update_xaxes(minor_ticks='inside', showgrid=True)
    if y_axis_col == 'fab (nm)':
        fig.update_yaxes(tickvals=[2, 3, 5, 7, 10, 14])
    st.plotly_chart(fig, theme="streamlit")
    st.caption(f'Point size depicts {size_col}.')
    
    # show raw data
    if st.toggle('Show raw data', value=False):
        st.dataframe(merged_df)