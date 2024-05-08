import sys
import os
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

# data category consts
CAT_NVIDIA_GPU = 'nvidia_gpu_specs'
CAT_LLM = 'llm_specs'

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
ds_llm = get_latest_data_source(CAT_LLM)
df_nvidia_gpu = load_df(ds_nvidia_gpu['path'])
df_llm = load_df(ds_llm['path'])

# set index
df_nvidia_gpu.set_index('model', inplace=True)
df_llm.set_index('name', inplace=True)

# observe GPU specs
with st.container():
    st.header('![NVIDIA logo](https://nvidianews.nvidia.com/media/sites/219/images/favicon.ico)NVIDIA GPU over the years')
    
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
    x_axis_col = st.selectbox('X-axis', ['period'] + selectable_columns, index=0)
    y_axis_col = st.selectbox('Y-axis', selectable_columns, index=0)
    size_col = st.selectbox('Choose what point size shows', selectable_columns, index=3)
    
    # filters
    selected_df = df_nvidia_gpu.copy()
    focus_select = st.selectbox('Focus on...', ['Series lead', 'All'], key='focus-gpu', index=0)
    if focus_select == 'Series lead':
        selected_df = selected_df[selected_df['series lead']==True]
    
    usage_select = st.selectbox('Usage', ['All', 'Desktop', 'Data center'], index=0)
    if usage_select == 'Desktop':
        selected_df = selected_df[selected_df['usage'] == 'desktop']
    elif usage_select == 'Data center':
        selected_df = selected_df[selected_df['usage'] == 'data center']
    
    show_model_name = st.toggle('Show model name', key='show-gpu', value=True)
    
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
    if st.toggle('Show raw data', key='show-raw-gpu', value=False):
        st.dataframe(df_nvidia_gpu)
        
# observe LLMs
with st.container():
    st.header('📚LLMs over the years')
    
    selectable_columns = [
        'parameters (B)',
        'input context window (K tkns)',
        'max output tokens (K tkns)',
        'input token price ($/M tkns)',
        'output token price ($/M tkns)',
        'input image price ($/K imgs)',
        'corpus size (B tokens)',
        'training cost (PFLOPS-day)',
    ]
    x_axis_col = st.selectbox('X-axis', ['period'] + selectable_columns + ['source access',], index=0)
    y_axis_col = st.selectbox('Y-axis', selectable_columns + ['source access',], index=0)
    size_col = st.selectbox('Point size', ['none'] + selectable_columns, index=1)
    
    selected_df = df_llm.copy()
    selected_df['period'] = pd.to_datetime(selected_df['period'])
    if size_col != 'none':
        selected_df = selected_df[selected_df[size_col].notna()]
    
    # filters
    focus_select = st.selectbox('Focus on...', ['Series premiere + lead', 'Series premiere', 'Series lead', 'All'], key='focus-llm-model', index=0)
    st.caption('When multiple models in a series are premiered, only the most powerful one is labeled "premiere".')
    if focus_select == 'Series premiere + lead':
        selected_df = selected_df[(selected_df['series first']==True) | selected_df['series lead']==True]
    elif focus_select == 'Series premiere':
        selected_df = selected_df[selected_df['series first']==True]    
    elif focus_select == 'Series lead':
        selected_df = selected_df[selected_df['series lead']==True]
    
    is_open_source = st.selectbox('Open source or close source', ['All', 'Open source', 'Close source'], index=0)
    if is_open_source == 'Open source':
        selected_df = selected_df[selected_df['source access'] == 'open source']
    elif is_open_source == 'Close source':
        selected_df = selected_df[selected_df['source access'] == 'close source']
    
    company_filter = st.multiselect('Filter by developer', options=selected_df['developer'].unique().tolist(), default=None)
    if len(company_filter):
        selected_df = selected_df[selected_df['developer'].isin(company_filter)]
    # select period range
    period_range = pd.date_range(df_llm['period'].min(), pd.to_datetime(datetime.now()), freq='MS')
    start_period, end_period = st.select_slider(
        'Select period range',
        options = period_range,
        value = (pd.to_datetime('2022-11-01'), period_range[-1]),
        format_func=lambda x: x.strftime('%Y-%m')
    )
    selected_df = selected_df[(selected_df['period'] >= start_period) & (selected_df['period'] <= end_period)]
    
    show_model_name = st.toggle('Show model name', key='show-llm-model', value=True)
    
    
    fig = px.scatter(selected_df,
                     title='🏅Large language model stats',
                     x=x_axis_col,
                     y=y_axis_col,
                     log_y=(y_axis_col in ['input context window (K tkns)', 'max output tokens (K tkns)']),
                     color='developer',
                     size=size_col if size_col != 'none' else None,
                     hover_name=selected_df.index,
                     hover_data=selected_df.columns,
                     text=selected_df.index if show_model_name else None,
                     category_orders={
                         'developer': ['OpenAI', 'Anthropic', 'Meta', 'Google', 'Aliyun']
                     },
                     color_discrete_map={
                        'OpenAI': 'rgb(153, 153, 153)',
                        'Anthropic': '#9d755d',
                        'Meta': '#3366cc',
                        'Google': '#ab63fa',
                        'Aliyun': '#ffa15a',
                        'Baidu': '#00cc96',
                        'Huawei': '#d62728',
                        'Mistral AI': '#eeca3b',
                        'x.AI': 'rgb(179, 179, 179)',
                        'Moonshot': '#ff9da6',
                     }
                    )
    fig.update_traces(textposition="bottom center")
    fig.update_layout(legend_title_text=f'Developer', margin=dict(b=0))
    # fig.update_layout(legend=dict(
    #     orientation="h",
    #     yanchor="bottom",
    #     y=1.02,
    #     xanchor="right",
    #     x=1
    # ))
    fig.update_xaxes(minor_ticks='inside', showgrid=True)
    # if y_axis_col == 'fab (nm)':
    #     fig.update_yaxes(tickvals=[2, 3, 5, 7, 10, 14])
    st.plotly_chart(fig, theme="streamlit")
    if size_col != 'none':
        st.caption(f'Point size depicts {size_col}.')
    
    # show raw data
    if st.toggle('Show raw data', key='show-raw-llm', value=False):
        st.dataframe(df_llm)
        
