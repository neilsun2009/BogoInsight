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

# data category consts
CAT_NVIDIA_GPU = 'nvidia_gpu_specs'
CAT_LLM = 'llm_specs'

# styling consts
SINGLE_SUBPLOT_HEIGHT = 300

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
    st.header('![NVIDIA logo](https://nvidianews.nvidia.com/media/sites/219/images/favicon.ico)NVIDIA GPUs over the years')
    
    # general observation
    st.subheader('General observation')
    st.write('Set parameters here:')
    with st.container(height=400):
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
    
    # general observation
    st.subheader('General observation')
    st.write('Set parameters here:')
    with st.container(height=400):
        selectable_columns = [
            'parameters (B)',
            'LMSYS Arena Elo',
            'MMLU',
            'MATH',
            'HumanEval',
            'DROP',
            'BFCL',
            'OpenCompass avg',
            'OpenCompass CN',
            'OpenCompass EN',
            'MMMU',
            'MathVista',
            'input context window (K tkns)',
            'max output tokens (K tkns)',
            'input token price ($/M tkns)',
            'output token price ($/M tkns)',
            'input image price ($/K imgs)',
            'function call cost ($/K calls)',
            'function call avg latency (s)',
            'corpus size (B tokens)',
            'training cost (PFLOPS-day)',
        ]
        x_axis_col = st.selectbox('X-axis', ['period'] + selectable_columns + ['source access',], index=0)
        y_axis_col = st.selectbox('Y-axis', selectable_columns + ['source access',], index=1)
        size_col = st.selectbox('Point size', ['none'] + selectable_columns, index=1)
        
        selected_df = df_llm.copy()
        # convert approximate values to float
        selected_df['parameters (B)'] = selected_df['parameters (B)'].str.replace('\*$', '', regex=True).astype(float)

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
        period_range = pd.date_range(df_llm['period'].min(), pd.to_datetime(datetime.now()) + pd.DateOffset(months=1), freq='MS')
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
        st.caption('Parameter values for proprietary models are mostly estimated.')
    
    # model arena
    st.subheader('Model arena')
    arena_tab_configs = [
        dict(
            name='⚔️Benchmark arena',
            dimensions=[
                'LMSYS Arena Elo', 'MMLU', 'MATH', 'HumanEval', 'DROP', 'BFCL',
                'OpenCompass avg', 'OpenCompass CN', 'OpenCompass EN',
                'MMMU', 'MathVista',
            ],
            default_dimensions = [
                'LMSYS Arena Elo', 'MMLU', 'MATH', 'HumanEval'
            ]
        ),
        dict(
            name='💸Price arena',
            dimensions=[
                'input token price ($/M tkns)', 'output token price ($/M tkns)',
                'input image price ($/K imgs)',
                'function call cost ($/K calls)',
            ],
            default_dimensions = [
                'input token price ($/M tkns)', 'output token price ($/M tkns)',
            ]
        ),
        dict(
            name='🛠️Function calling arena',
            dimensions=[
                'BFCL',
                'function call cost ($/K calls)', 
                'function call avg latency (s)',
            ],
            default_dimensions=[
                'BFCL',
                'function call cost ($/K calls)', 
                'function call avg latency (s)',
            ],    
        ),
        dict(
            name='❓Customized arena',
            dimensions=[
                'parameters (B)',
                'input context window (K tkns)', 'max output tokens (K tkns)',
                'LMSYS Arena Elo', 'MMLU', 'MATH', 'HumanEval', 'DROP', 'BFCL',
                'OpenCompass avg', 'OpenCompass CN', 'OpenCompass EN',
                'MMMU', 'MathVista',
                'BFCL',
                'function call cost ($/K calls)', 'function call avg latency (s)',
                'input token price ($/M tkns)', 'output token price ($/M tkns)',
                'input image price ($/K imgs)',
                'corpus size (B tokens)',
            ],
            default_dimensions=[
                'parameters (B)',
                'LMSYS Arena Elo',
                'input context window (K tkns)',
            ],    
        ),
    ]
    tabs = st.tabs([tab['name'] for tab in arena_tab_configs])
    for idx, tab in enumerate(tabs):
        with tab:
            tab_cofig = arena_tab_configs[idx]
            dimensions = st.multiselect('Select dimensions', options=tab_cofig['dimensions'], 
                                        default=tab_cofig['default_dimensions'], key=f'arena-dimension-{idx}')
            if len(dimensions) < 1:
                st.warning('Please select at least 1 dimension.')
            else:
                df_arena = df_llm.copy()
                df_arena['parameters (B)'] = df_arena['parameters (B)'].str.replace('\*$', '', regex=True).astype(float)
                df_arena = df_arena[dimensions]
                df_arena.dropna(how='all', inplace=True)
                models = st.multiselect('Select models', options=df_arena.index.unique(), 
                                        default=None, key=f'arena-model-{idx}')
                if len(models) < 1:
                    st.warning('Please select at least 1 model.')
                else:
                    df_arena_sel = df_arena.loc[models]
                    # bar chart     
                    bar_fig = px.bar(
                        df_arena_sel,
                        x=df_arena_sel.index,
                        y=dimensions,
                        title='Bar chart',
                        color=df_arena_sel.index,
                        facet_col="variable",
                        facet_col_wrap=3,
                        facet_row_spacing=0.1,
                        facet_col_spacing=0.1,
                        height=SINGLE_SUBPLOT_HEIGHT * math.ceil(len(dimensions) / 3),
                    )
                    bar_fig.update_yaxes(
                        matches=None,
                        showticklabels=True,
                    )
                    bar_fig.update_xaxes(
                        # matches=None,
                        showticklabels=False,
                        title_text='',
                    )
                    bar_fig.update_layout(
                        showlegend=True, 
                        margin=dict(b=0),
                        legend_title_text=f'Model'
                    )
                    bar_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                    st.plotly_chart(bar_fig, theme="streamlit")
                    # radar chart
                    radar_fig = go.Figure()
                    for model in models:
                        radar_fig.add_trace(go.Scatterpolar(
                            r=df_arena_sel.loc[model].values,
                            theta=dimensions,
                            fill='toself',
                            name=model,
                        ))
                    radar_fig.update_layout(
                        title='Radar chart',
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                autorange=True,
                                # showticklabels=False,
                                showline=False,
                                ticks='',
                                # range=[0, 5]
                            ),
                        ),
                        margin=dict(b=0),
                        showlegend=True,
                    )
                    st.plotly_chart(radar_fig, theme="streamlit")

    # benchmarks
    st.subheader('Meet the benchmarks')
    benchmark_configs = [
        dict(
            name='🫅Subjective',
            benchmarks=[
                dict(
                    name='LMSYS Arena Elo',
                    desc='''
                    LMSYS Chatbot Arena is a crowdsourced open platform for LLM evals maintained by LMSYS (Large Model System Organization).
                    They've collected over 1,000,000 human pairwise comparisons to rank LLMs with the Bradley-Terry model and display the model ratings in Elo-scale.
                    
                    [Official website](https://arena.lmsys.org/)

                    ''',
                ),
            ]
        ),
        dict(
            name='🎯Objective',
            benchmarks=[
                dict(
                    name='MMLU',
                    desc='''
                    Measuring Massive Multitask Language Understanding (MMLU) is a benchmark for evaluating the capabilities of language models. It consists of about 16,000 multiple-choice questions spanning 57 academic subjects including mathematics, philosophy, law and medicine. It is one of the most commonly used benchmarks for comparing the capabilities of large language models.
                    
                    [Paper](https://arxiv.org/abs/2009.03300)

                    ''',
                ),
                dict(
                    name='MATH',
                    desc='''
                    The MATH dataset or benchmark focuses on evaluating a language model's mathematical reasoning capabilities, requiring it to solve arithmetic, algebraic, and other mathematical problems using natural language understanding.
                    
                    [Paper](https://arxiv.org/abs/2103.03874)

                    ''',
                ),
                dict(
                    name='HumanEval',
                    desc='''
                    HumanEval is a benchmark that tests the capability of code generation models to produce human-level code snippets. It consists of real-world programming problems solved by humans and serves as a standard to evaluate the functional correctness of generated code.
                    
                    [Paper](https://arxiv.org/abs/2107.03374)

                    ''',
                ),
                dict(
                    name='DROP',
                    desc='''
                    DROP (Disambiguation and Reasoning Over Paraphrases) is a reading comprehension benchmark that requires models to understand passages and answer questions that involve numerical reasoning and the ability to resolve references and paraphrases.
                    
                    [Paper](https://arxiv.org/abs/1903.00161)

                    ''',
                ),
                dict(
                    name='BFCL',
                    desc='''
                    The Berkeley Function Calling Leaderboard (also called Berkeley Tool Calling Leaderboard) evaluates the LLM's ability to call functions (aka tools) accurately. This leaderboard consists of real-world data and will be updated periodically.
                    
                    [Paper](https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html)
                    
                    [Official website](https://gorilla.cs.berkeley.edu/leaderboard.html)

                    ''',
                ),
            ]
        ),
        dict(
            name='🧭OpenCompass',
            benchmarks=[
                dict(
                    name='OpenCompass avg',
                    desc='''
                    Open Compass CompassRank is dedicated to exploring the most advanced language and visual models, offering a comprehensive, objective, and neutral evaluation reference for the industry and research community.
                    It is updated on a monthly basis.
                    
                    [Official website](https://rank.opencompass.org.cn/home)
                    
                    This is the overall average rating by OpenCompass.
                    ''',
                ),
                dict(
                    name='OpenCompass CN',
                    desc='''
                    Open Compass CompassRank is dedicated to exploring the most advanced language and visual models, offering a comprehensive, objective, and neutral evaluation reference for the industry and research community.
                    It is updated on a monthly basis.
                    
                    [Official website](https://rank.opencompass.org.cn/home)
                    
                    This is the overall Chinese language rating by OpenCompass.
                    ''',
                ),
                dict(
                    name='OpenCompass EN',
                    desc='''
                    Open Compass CompassRank is dedicated to exploring the most advanced language and visual models, offering a comprehensive, objective, and neutral evaluation reference for the industry and research community.
                    It is updated on a monthly basis.
                    
                    [Official website](https://rank.opencompass.org.cn/home)
                    
                    This is the overall English language rating by OpenCompass.
                    ''',
                ),
            ]
        ),
        dict(
            name='👓Vision',
            benchmarks=[
                dict(
                    name='MMMU',
                    desc='''
                    MMMU (Massive Multi-discipline Multimodal Understanding) is a new benchmark designed to evaluate multimodal models on massive multi-discipline tasks demanding college-level subject knowledge and deliberate reasoning.
                    
                    [Paper](https://arxiv.org/abs/2311.16502)

                    ''',
                ),
                dict(
                    name='MathVista',
                    desc='''
                    MathVista is a benchmark designed to combine challenges from diverse mathematical and visual tasks. It consists of 6,141 examples, derived from 28 existing multimodal datasets involving mathematics and 3 newly created datasets (i.e., IQTest, FunctionQA, and PaperQA). Completing these tasks requires fine-grained, deep visual understanding and compositional reasoning, which all state-of-the-art foundation models find challenging.
                    
                    [Paper](https://arxiv.org/abs/2310.02255)

                    ''',
                ),
            ],
        ),
    ]
    tabs = st.tabs([tab['name'] for tab in benchmark_configs])
    for idx, tab in enumerate(tabs):
        with tab:
            tab_cofig = benchmark_configs[idx]
            bm_config = st.selectbox('Select an indivisual benchmark', 
                                     tab_cofig['benchmarks'], 
                                     format_func=lambda x: x['name'],
                                     index=0, key=f'benchmark-bm-{idx}')
            st.markdown(bm_config['desc'])
            df_bm = df_llm.copy()[[bm_config['name']]]
            df_bm.dropna(how='all', inplace=True)
            df_bm = df_bm.sort_values(by=bm_config['name'], ascending=False)
            df_bm = df_bm.head(10)
            # bar chart     
            bar_fig = px.bar(
                df_bm,
                x=df_bm.index,
                y=[bm_config['name']],
                title=f'Top 10 models according to {bm_config["name"]}',
                color=df_bm.index,
                # facet_col="variable",
                # facet_col_wrap=1,
                # facet_row_spacing=0.1,
                # facet_col_spacing=0.1,
                # height=SINGLE_SUBPLOT_HEIGHT * math.ceil(len(dimensions) / 3),
            )
            bar_fig.update_yaxes(
                matches=None,
                showticklabels=True,
            )
            bar_fig.update_xaxes(
                # matches=None,
                showticklabels=True,
                title_text='models',
            )
            bar_fig.update_layout(
                showlegend=False, 
                margin=dict(b=0),
                legend_title_text=f'Model'
            )
            bar_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            st.plotly_chart(bar_fig, theme="streamlit")
               
    
    # show raw data
    if st.toggle('Show raw data', key='show-raw-llm', value=False):
        st.dataframe(df_llm)
        st.caption('\* estimated value')
        
