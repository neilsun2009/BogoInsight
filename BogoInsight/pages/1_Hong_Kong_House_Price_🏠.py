import sys
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.utils.data_utils import (
    get_latest_data_source, load_df,
)
from BogoInsight.utils.plot_utils import (
    update_line_chart, gen_heatmap
)


# data category consts
CAT_HOUSE_PRICE = 'hong_kong_house_price_index'
CAT_HOUSE_RENTAL = 'hong_kong_house_rental_index'
CAT_HOUSE_VACANCY = 'hong_kong_house_vacancy'
CAT_HOUSEHOLD = 'hong_kong_household_count'
CAT_GDP = 'hong_kong_gdp_growth'
CAT_INTEREST_RATE = 'hong_kong_interest_rate'

# def rise & fall time ranges
TENDENCY_RANGES = [
    {
        'start': '1995-10-01',
        'end': '1997-05-01',
        'desc': 'Expectation & speculation on the Handover'            
    },
    {
        'start': '1997-10-01',
        'end': '2003-08-01',
        'desc': 'Asian Financial Crisis, major capital outflow & SARS outbreak'            
    },
    {
        'start': '2003-08-01',
        'end': '2008-03-01',
        'desc': 'Economic recovery & low interest rate'            
    },
    {
        'start': '2008-05-01',
        'end': '2008-12-01',
        'desc': 'Global Financial Crisis'            
    },
    {
        'start': '2008-12-01',
        'end': '2015-09-01',
        'desc': 'Quantitative Easing & China economic boom'            
    },
    {
        'start': '2015-09-01',
        'end': '2016-03-01',
        'desc': 'China economic slowdown ?'            
    },
    {
        'start': '2016-03-01',
        'end': '2018-07-01',
        'desc': 'Continuous low interest rate'            
    },
    {
        'start': '2018-08-01',
        'end': '2018-12-01',
        'desc': 'interest rate hike & trade war'            
    },
    {
        'start': '2018-12-01',
        'end': '2019-05-01',
        'desc': 'Interest rate go down & stablization?'            
    },
    {
        'start': '2021-09-01',
        'end': '2024-02-01',
        'desc': 'Interest rate hike & major middle class outflow'            
    },
]


def write_tendency_desc(tr):
    styled_pct_chg = f":green[+{tr['pct_change']:.2f}%]" if tr['tendency'] == 'rise' else f":red[{tr['pct_change']:.2f}%]"
    st.markdown(f"""
        **Delta:** **{styled_pct_chg}**  
        **Duration:** {tr['duration']}  
        **Major causes:** {tr['desc']}  
    """)
    
def draw_tendency_rects(fig, with_annotation=True):
    for tr in TENDENCY_RANGES:
        # draw rect
        fig.add_vrect(x0=tr['start'], x1=tr['end'], 
                         line_width=0, fillcolor="green" if tr['tendency'] == 'rise' else 'red', opacity=0.2,
                         annotation_text=f"{'+' if tr['tendency'] == 'rise' else ''}{tr['pct_change']:.2f}%" if with_annotation else '', 
                         annotation_position=("top left" if tr['tendency'] == 'rise' else 'top right'),)
        
st.set_page_config(
    page_title='Hong Kong House Price Analysis - BogoInsight', 
    page_icon='🏠'
)

st.title('🏠Analysis on HK House Price')

# sidebar
with st.sidebar:
    st.button('Clear all cache', on_click=lambda: st.cache_data.clear())

# get data
ds_house_price = get_latest_data_source(CAT_HOUSE_PRICE)
ds_house_rental = get_latest_data_source(CAT_HOUSE_RENTAL)
ds_gdp = get_latest_data_source(CAT_GDP)
ds_interest_rate = get_latest_data_source(CAT_INTEREST_RATE)
ds_vacancy = get_latest_data_source(CAT_HOUSE_VACANCY)
ds_household = get_latest_data_source(CAT_HOUSEHOLD)

# data preprocessing
with st.spinner('Data preprocessing...'):
    # merge useful columns
    merged_df = load_df(ds_house_price['path']).set_index('period')[
        [
            'house price all (idx 1999=100)', 
            'house price growth all (% rate MoM)'
        ]]
    merged_df = merged_df.join(load_df(ds_house_rental['path']).set_index('period')[[
            'house rental all (idx 1999=100)', 
            'house rental growth all (% rate MoM)'
        ]], on='period', how='outer', sort=True)
    merged_df = merged_df.join(load_df(ds_vacancy['path']).set_index('period')[[
            'house vacancy all (num)', 
            'house vacancy all (%)',
            'house vacancy growth all (% rate YoY)'
        ]], on='period', how='outer', sort=True)
    merged_df = merged_df.join(load_df(ds_household['path']).set_index('period')[[
            'households (\'000)', 
            'owner-occupier percentage (%)',
            'household growth rate (%)'
        ]], on='period', how='outer', sort=True)
    merged_df = merged_df.join(load_df(ds_gdp['path']).set_index('period')[[
            'GDP chained (2021) (HK$M)', 
            'GDP seasonally adjusted (% QoQ rate)', 
            'implicit price deflator (% YoY rate)',
        ]], on='period', how='outer', sort=True)
    merged_df = merged_df.join(load_df(ds_interest_rate['path']).set_index('period')[[
            'best lending rate (% p.a.)', 
        ]], on='period', how='outer', sort=True)
    merged_df.set_index('period', inplace=True)
    # select data from 1993
    merged_df = merged_df.loc['1993-01-01':]
    # additional column calculation
    merged_df['house total supply (num)'] = (merged_df['house vacancy all (num)'] * 100 / merged_df['house vacancy all (%)']).round()
    # fill in details for each tendency range
    house_price_index_column = 'house price all (idx 1999=100)'
    for tr in TENDENCY_RANGES:
        start_value = merged_df.loc[tr['start'], house_price_index_column]
        end_value = merged_df.loc[tr['end'], house_price_index_column]
        tr['tendency'] = 'rise' if end_value > start_value else 'fall'
        tr['pct_change'] = (end_value - start_value) / start_value * 100
        # Calculate the duration in years and months
        start_date = pd.to_datetime(tr['start'])
        end_date = pd.to_datetime(tr['end'])
        years = end_date.year - start_date.year
        months = end_date.month - start_date.month
        # Adjust if end month is less than start month
        if months < 0:
            years -= 1
            months += 12
        tr['duration'] = f'{years} years {months} months' if years > 0 else f'{months} months'

# Observe the rises and falls
with st.container():
    st.header('📈The rises & falls of HK house market')
    
    # house price line chart
    line_chart = px.line(merged_df[[house_price_index_column]], 
                title='💵HK average house price index (1999=100)',
                # x='period', 
                # y=sel_columns, 
                markers=False,
                labels={"period": "time", "value": "price index"},
                )
    update_line_chart(line_chart)
    line_chart.update_layout(showlegend=False)
    draw_tendency_rects(line_chart)
    
    st.plotly_chart(line_chart, theme="streamlit")
    # write desc
    rise_trs = [tr for tr in TENDENCY_RANGES if tr['tendency'] == 'rise']
    st.write(f"🔼{len(rise_trs)} major rises:")
    tabs = st.tabs([f"{tr['start'][:7]} ~ {tr['end'][:7]}" for tr in rise_trs])
    for idx, tab in enumerate(tabs):
        with tab:
            write_tendency_desc(rise_trs[idx])
    fall_trs = [tr for tr in TENDENCY_RANGES if tr['tendency'] == 'fall']
    st.write(f'🔽{len(fall_trs)} major falls:')
    tabs = st.tabs([f"{tr['start'][:7]} ~ {tr['end'][:7]}" for tr in fall_trs])
    for idx, tab in enumerate(tabs):
        with tab:
            write_tendency_desc(fall_trs[idx])

# Observe supply
st.header('Supply side factors')

# house supply & vacancy
with st.container():
    st.subheader('🏠House supply & vacancy')
    # house supply
    fig = px.line(merged_df, 
                 y=['house price all (idx 1999=100)', 'house total supply (num)'], 
                 facet_col="variable",
                 facet_col_wrap=1,
                 facet_row_spacing=0.15,
                 color=px.NO_COLOR,)
    update_line_chart(fig)
    fig.update_yaxes(matches=None)
    fig.update_layout(showlegend=False)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=", maxsplit=1)[-1]))
    draw_tendency_rects(fig, with_annotation=False)
    st.plotly_chart(fig, theme="streamlit")

# show raw data
if st.checkbox('Show raw data'):
    st.dataframe(merged_df)