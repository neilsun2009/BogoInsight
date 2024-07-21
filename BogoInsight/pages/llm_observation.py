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
CAT_LLM = 'llm_specs'

# styling consts
SINGLE_SUBPLOT_HEIGHT = 300
RANGE_100_BENCHMARKS = ['MMLU', 'MATH', 'HumanEval', 'DROP', 'BFCL', 'OpenCompass avg', 'OpenCompass CN', 'OpenCompass EN', 'MMMU', 'MathVista']

st.set_page_config(
    page_title='LLM Observation | BogoInsight', 
    page_icon='🤖'
)

st.title('🤖LLM Observation')

# sidebar
with st.sidebar:
    render_toc()
    st.divider()
    
    st.button('Reload data', on_click=lambda: st.cache_data.clear())

# get data
ds_llm = get_latest_data_source(CAT_LLM)
df_llm = load_df(ds_llm['path'])

# set index
df_llm.set_index('name', inplace=True)
   
        
# observe LLMs
with st.container():
    # st.header('📚LLMs over the years')
    
    # general observation
    st.header('📈General observation')
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
            value = (pd.to_datetime('2023-3-01'), period_range[-1]),
            format_func=lambda x: x.strftime('%Y-%m')
        )
        selected_df = selected_df[(selected_df['period'] >= start_period) & (selected_df['period'] <= end_period)]
        
        show_model_name = st.toggle('Show model name', key='show-llm-model', value=True)
    
    # selected_df.fillna(-1, inplace=True)
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
                        'Meta': 'rgb(131, 201, 255)',
                        'Google': '#ab63fa',
                        'Aliyun': '#ffa15a',
                        'Baidu': 'rgb(125, 139, 161)',
                        'Huawei': '#d62728',
                        'Mistral AI': '#eeca3b',
                        'x.AI': 'rgb(179, 179, 179)',
                        '01.AI': 'rgb(41, 176, 157)',
                        'Zhipu AI': '#3366cc',
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
    st.header('🎯Model arena')
    arena_tab_configs = [
        dict(
            name='⚔️Benchmark arena',
            dimensions=[
                'LMSYS Arena Elo', 'MMLU', 'MATH', 'HumanEval', 'DROP', 'BFCL',
                'OpenCompass avg', 'OpenCompass CN', 'OpenCompass EN',
                'MMMU', 'MathVista',
            ],
            default_dimensions = [
                'MMLU', 'MATH', 'HumanEval', 'OpenCompass CN', 'BFCL'
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
                'input image price ($/K imgs)',
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
                # df_arena.dropna(how='all', inplace=True)
                models = st.multiselect('Select models', options=df_arena.index.unique(), 
                                        default=['GPT-4o', 'Gemini 1.5 Pro 2024-05', 'Claude 3.5 Sonnet', 'Llama 3 70B', 'Qwen2 72B'], 
                                        key=f'arena-model-{idx}')
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
                        text_auto=True,
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
                        legend_title_text=f'Model',
                    )
                    for d_idx, d in enumerate(dimensions):
                        if d in RANGE_100_BENCHMARKS:
                            bar_fig.update_yaxes(range=[0, 101], row=math.ceil(len(dimensions) / 3) - math.floor(d_idx / 3), col=d_idx % 3 + 1)
                            # bar_fig.update_yaxes(range=[0, 101], row=1, col=1)
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
                                # autorange=True,
                                # showticklabels=False,
                                showline=False,
                                ticks='',
                                range=[0, 100] if idx == 0 and 'LMSYS Arena Elo' not in dimensions else None,
                            ),
                        ),
                        margin=dict(b=20),
                        showlegend=True,
                    )
                    st.plotly_chart(radar_fig, theme="streamlit")

    # benchmarks
    st.header('🏆Meet the benchmarks')
    benchmark_configs = [
        dict(
            name='🫅Subjective',
            benchmarks=[
                dict(
                    name='LMSYS Arena Elo',
                    desc='''
                    LMSYS Chatbot Arena is a crowdsourced open platform for LLM evals maintained by LMSYS (Large Model System Organization). 
                    They have collected more than 1,000,000 human pairwise comparisons, and are still doing so, to rank LLMs with the [Bradley-Terry model](https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model) and display the model ratings in [Elo-scale](https://en.wikipedia.org/wiki/Elo_rating_system). 
                    You can participate through [ChatBot Arena](https://arena.lmsys.org/).
                    
                    [Paper](https://arxiv.org/abs/2403.04132)
                    
                    [Blog](https://lmsys.org/blog/2023-05-03-arena/)
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
                    Measuring Massive Multitask Language Understanding (MMLU) is a benchmark for evaluating the capabilities of language models. 
                    It consists of about 16,000 multiple-choice questions spanning 57 academic subjects including mathematics, philosophy, law and medicine. 
                    It is one of the most commonly used benchmarks for comparing the capabilities of large language models.
                    
                    [Paper](https://arxiv.org/abs/2009.03300)

                    ''',
                ),
                dict(
                    name='MATH',
                    desc='''
                    The MATH dataset or benchmark focuses on evaluating a language model's mathematical reasoning capabilities, requiring it to solve arithmetic, algebraic, and other mathematical problems using natural language understanding. 
                    It contains 12,500 challenging competition mathematics problems. Each problem in MATH has a full step-by-step solution which can be used to teach models to generate answer derivations and explanations.
                    
                    [Paper](https://arxiv.org/abs/2103.03874)

                    ''',
                ),
                dict(
                    name='HumanEval',
                    desc='''
                    HumanEval is a benchmark that tests the capability of code generation models to produce human-level code snippets. 
                    It consists of 164 original programming problems, assessing language comprehension, algorithms, and simple mathematics, with some comparable to simple software interview questions.
                    
                    [Paper](https://arxiv.org/abs/2107.03374)

                    ''',
                ),
                dict(
                    name='DROP',
                    desc='''
                    DROP (Disambiguation and Reasoning Over Paraphrases) is a reading comprehension benchmark that requires models to understand passages and answer questions that involve numerical reasoning and the ability to resolve references and paraphrases. 
                    In this crowdsourced, adversarially-created, 96k question-answering benchmark, a system must resolve multiple references in a question, map them onto a paragraph, and perform discrete operations over them (such as addition, counting, or sorting).
                    
                    [Paper](https://arxiv.org/abs/1903.00161)

                    ''',
                ),
                dict(
                    name='BFCL',
                    desc='''
                    The Berkeley Function Calling Leaderboard (also called Berkeley Tool Calling Leaderboard) evaluates the LLM's ability to call functions (aka tools) accurately. 
                    The dataset includes 40 sub-domains of functions within its generic evaluations. This allows us to understand the model performance not just in data-abundant domains like computing, and cloud, but also in niche domains like sports, and law.
                    
                    [Paper](https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html)
                    
                    [Official website](https://gorilla.cs.berkeley.edu/leaderboard.html)

                    ''',
                ),
            ]
        ),
        dict(
            name='🧭OpenCompass',
            desc='''
                Open Compass CompassRank is dedicated to exploring the most advanced language and visual models, offering a comprehensive, objective, and neutral evaluation reference for the industry and research community.
                Using multiple closed-source datasets for evaluation, it provides multi-dimensional evaluation scores.
                
                [Official website](https://rank.opencompass.org.cn/home)
            ''',
            benchmarks=[
                dict(
                    name='OpenCompass avg',
                    desc='''
                    This is the overall average rating by OpenCompass, which is the average score of the model across all evaluation datasets in OpenCompass.
                    ''',
                ),
                dict(
                    name='OpenCompass CN',
                    desc='''
                    This is the overall Chinese language rating by OpenCompass.
                    ''',
                ),
                dict(
                    name='OpenCompass EN',
                    desc='''
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
                    MMMU includes 11.5K meticulously collected multimodal questions from college exams, quizzes, and textbooks, covering six core disciplines: Art & Design, Business, Science, Health & Medicine, Humanities & Social Science, and Tech & Engineering, spans 30 subjects and 183 subfields.
                    It focuses on advanced perception and reasoning with domain-specific knowledge, challenging models to perform tasks akin to those faced by experts. 
                    
                    [Paper](https://arxiv.org/abs/2311.16502)

                    ''',
                ),
                dict(
                    name='MathVista',
                    desc='''
                    MathVista is a benchmark designed to combine challenges from diverse mathematical and visual tasks. 
                    It consists of 6,141 examples, derived from 28 existing multimodal datasets involving mathematics and 3 newly created datasets (i.e., IQTest, FunctionQA, and PaperQA). 
                    Completing these tasks requires fine-grained, deep visual understanding and compositional reasoning, which all state-of-the-art foundation models find challenging.
                    
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
            if 'desc' in tab_cofig:
                st.markdown(tab_cofig['desc'])
            bm_config = st.selectbox('Select an indivisual benchmark', 
                                     tab_cofig['benchmarks'], 
                                     format_func=lambda x: x['name'],
                                     index=0, key=f'benchmark-bm-{idx}')
            st.markdown(bm_config['desc'])
            
            df_bm = df_llm.copy()
            is_open_source = st.selectbox('Open source or close source', 
                                          ['All', 'Open source', 'Close source'], 
                                          index=0, key=f'benchmark-source-{idx}')
            if is_open_source == 'Open source':
                df_bm = df_bm[df_bm['source access'] == 'open source']
                title = f'Top 10 open source models according to {bm_config["name"]}'
            elif is_open_source == 'Close source':
                df_bm = df_bm[df_bm['source access'] == 'close source']
                title = f'Top 10 close source models according to {bm_config["name"]}'
            else:
                title = f'Top 10 models according to {bm_config["name"]}'
            df_bm.dropna(subset=[bm_config['name']], inplace=True)
            df_bm = df_bm.sort_values(by=bm_config['name'], ascending=False)
            df_bm = df_bm.head(10)
            # df_bm.fillna(-1, inplace=True)
            # bar chart     
            bar_fig = px.bar(
                df_bm,
                x=df_bm.index,
                y=[bm_config['name']],
                title=title,
                color=df_bm.index,
                text_auto=True,
                hover_name=df_bm.index,
                hover_data=set(df_bm.columns) - set([bm_config['name']]),
                height=SINGLE_SUBPLOT_HEIGHT * 2,
            )
            bar_fig.update_yaxes(
                matches=None,
                showticklabels=True,
                title_text='value' if bm_config['name'] == 'LMSYS Arena Elo' else 'accuracy (%)',
                range=[0, 101] if bm_config['name'] in RANGE_100_BENCHMARKS else None,
            )
            bar_fig.update_xaxes(
                # matches=None,
                showticklabels=True,
                title_text='model',
            )
            bar_fig.update_layout(
                showlegend=False, 
                margin=dict(b=0),
                legend_title_text=f'Model'
            )
            bar_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            st.plotly_chart(bar_fig, theme="streamlit")
               
    
    # show raw data
    st.subheader('Raw data', divider='grey')
    # if st.toggle('Show raw data', key='show-raw-llm', value=False):
    column_config = {
        "has audio": st.column_config.CheckboxColumn(
            default=False,
        ),
        "has visual": st.column_config.CheckboxColumn(
            default=False,
        ),
        "series first": st.column_config.CheckboxColumn(
            default=False,
        ),
        "series lead": st.column_config.CheckboxColumn(
            default=False,
        ),
    }
    for col in RANGE_100_BENCHMARKS:
        column_config[col] = st.column_config.ProgressColumn(
            format="%f",
            min_value=0,
            max_value=100,
        )
    st.dataframe(df_llm, column_config=column_config)
    st.caption('\* estimated value')
        
