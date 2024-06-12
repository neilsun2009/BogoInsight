import sys
import os
import math
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.utils.data_utils import (
    get_latest_data_source, load_df,
)
from BogoInsight.utils.plot_utils import (
    update_line_chart, gen_heatmap
)
from BogoInsight.utils.router import render_toc

# data category consts
CAT_NVIDIA_GPU = 'nvidia_gpu_specs'

# styling consts
SINGLE_SUBPLOT_HEIGHT = 300
RANGE_100_BENCHMARKS = ['MMLU', 'MATH', 'HumanEval', 'DROP', 'BFCL', 'OpenCompass avg', 'OpenCompass CN', 'OpenCompass EN', 'MMMU', 'MathVista']

st.set_page_config(
    page_title='GPU Stats | BogoInsight', 
    page_icon='🔦'
)

st.title('🔦GPU Stats')

# sidebar
with st.sidebar:
    render_toc()
    st.divider()
    
    st.button('Reload data', on_click=lambda: st.cache_data.clear())

# get data
ds_nvidia_gpu = get_latest_data_source(CAT_NVIDIA_GPU)
df_nvidia_gpu = load_df(ds_nvidia_gpu['path'])

# set index
df_nvidia_gpu.set_index('model', inplace=True)

# observe GPU specs
with st.container():
    st.header('![NVIDIA logo](https://nvidianews.nvidia.com/media/sites/219/images/favicon.ico)NVIDIA GPUs over the years')
    
    # general observation
    st.subheader('General observation', divider='grey')
    st.write('Set parameters here:')
    with st.container(height=400):
        selectable_columns = [
            'processing power fp64 (TFLOPS)',
            'processing power fp32 (TFLOPS)',
            'processing power fp16 (TFLOPS)',
            'memory (GB)',
            'fab (nm)',
            'TDP (Watts)',
            'bandwidth (GB/s)',
            'CUDA cores',
            'base clock (MHz)',
            'boost clock (MHz)',
        ]
        x_axis_col = st.selectbox('X-axis', ['period'] + selectable_columns, index=0)
        y_axis_col = st.selectbox('Y-axis', selectable_columns, index=1)
        size_col = st.selectbox('Point size', selectable_columns, index=3)
        
        # filters
        selected_df = df_nvidia_gpu.copy()
        if size_col != 'none':
            selected_df = selected_df[selected_df[size_col].notna()]
            
        focus_select = st.selectbox('Focus on...', ['Series lead', 'All'], key='focus-gpu', index=0)
        if focus_select == 'Series lead':
            selected_df = selected_df[selected_df['series lead']==True]
        
        arch_filter = st.multiselect('Filter by architecture', options=selected_df['architecture'].unique().tolist(), default=None)
        if len(arch_filter):
            selected_df = selected_df[selected_df['architecture'].isin(arch_filter)]
        
        usage_select = st.selectbox('Usage', ['All', 'Desktop', 'Data center'], index=0)
        if usage_select == 'Desktop':
            selected_df = selected_df[selected_df['usage'] == 'desktop']
        elif usage_select == 'Data center':
            selected_df = selected_df[selected_df['usage'] == 'data center']
        
        show_model_name = st.toggle('Show model name', key='show-gpu', value=True)
    
    # selected_df.fillna(-1, inplace=True)
    fig = px.scatter(selected_df,
                     title='🏅NVIDIA GPU model stats',
                     x=x_axis_col,
                     y=y_axis_col,
                     color='architecture',
                     size=size_col,
                     hover_name=selected_df.index,
                     hover_data=selected_df.columns,
                     text=selected_df.index if show_model_name else None,
                     category_orders={'architecture': ['Pascal', 'Volta', 'Turing', 'Ampere', 'Hopper', 'Ada Lovelace']},
                    )
    fig.update_traces(textposition="bottom center")
    fig.update_layout(legend_title_text=f'Architecture', margin=dict(b=0))
    # fig.update_layout(legend=dict(
    #     orientation="h",
    #     yanchor="bottom",
    #     y=1.02,
    #     xanchor="right",
    #     x=1
    # ))
    fig.update_xaxes(minor_ticks='inside', showgrid=True)
    # fab size custom tickvals
    fab_sizes = [2, 3, 5, 7, 10, 14]
    if y_axis_col == 'fab (nm)':
        fig.update_yaxes(tickvals=fab_sizes)
    if x_axis_col == 'fab (nm)':
        fig.update_xaxes(tickvals=fab_sizes)
    st.plotly_chart(fig, theme="streamlit")
    st.caption(f'Point size depicts {size_col}.')
    
    # show raw data
    st.subheader('Raw data', divider='grey')
    # if st.toggle('Show raw data', key='show-raw-llm', value=False):
    column_config = {
        "series lead": st.column_config.CheckboxColumn(
            default=False,
        ),
    }
    st.dataframe(df_nvidia_gpu, column_config=column_config)
    