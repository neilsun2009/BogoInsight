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
CAT_HOUSE_PRICE = 'hong_kong_house_price_index'
CAT_HOUSE_RENTAL = 'hong_kong_house_rental_index'
CAT_HOUSE_VACANCY = 'hong_kong_house_vacancy'
CAT_HOUSEHOLD = 'hong_kong_household_count'
CAT_GDP = 'hong_kong_gdp_growth'
CAT_INTEREST_RATE = 'hong_kong_interest_rate'
CAT_EXCHANGE_RATE = 'hong_kong_exchange_rate'
CAT_FOREIGN_INVEST = 'hong_kong_foreign_investment'
CAT_HIBOR = 'hibor'

# styling consts
SINGLE_SUBPLOT_HEIGHT = 400
TOTAL_FACET_ROW_SPACING = 0.15

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
        'desc': 'Asian Financial Crisis & SARS outbreak'            
    },
    {
        'start': '2003-08-01',
        'end': '2008-03-01',
        'desc': 'Economic recovery & more currency in circulation'            
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
        'desc': 'Mainland capital inflow restriction'            
    },
    {
        'start': '2016-03-01',
        'end': '2018-07-01',
        'desc': 'More currency in circulation & mainland capital inflow reboom'            
    },
    {
        'start': '2018-08-01',
        'end': '2018-12-01',
        'desc': 'China-US trade war'            
    },
    {
        'start': '2018-12-01',
        'end': '2019-05-01',
        'desc': 'Impact of trade war stablized'            
    },
    {
        'start': '2021-09-01',
        'end': '2024-02-01',
        'desc': 'Post-COVID economic adjustment, currentcy in circulation dropped & major middle class outflow'            
    },
]


def write_tendency_desc(tr):
    styled_pct_chg = f":red[+{tr['pct_change']:.2f}%]" if tr['tendency'] == 'rise' else f":green[{tr['pct_change']:.2f}%]"
    st.markdown(f"""
        **Delta:** **{styled_pct_chg}**  
        **Duration:** {tr['duration']}  
        **Major events:** {tr['desc']}  
    """)
    
def draw_tendency_rects(fig, with_annotation=True):
    for idx, tr in enumerate(TENDENCY_RANGES):
        # draw rect
        fig.add_vrect(x0=tr['start'], x1=tr['end'], 
                         line_width=0, fillcolor="red" if tr['tendency'] == 'rise' else 'green', opacity=0.2,
                        #  annotation_text=f"{'+' if tr['tendency'] == 'rise' else ''}{tr['pct_change']:.2f}%" if with_annotation else '', 
                         annotation_text=f"{idx+1}." if with_annotation else '', 
                        #  annotation_position=("top left" if tr['tendency'] == 'rise' else 'top right'),)
                         annotation_position=("top left"),)
        
st.set_page_config(
    page_title='Hong Kong House Price Analysis - BogoInsight', 
    page_icon='🏠'
)

st.title('🏠Analysis on HK House Price')

# sidebar
with st.sidebar:
    st.button('Reload data', on_click=lambda: st.cache_data.clear())

# get data
ds_house_price = get_latest_data_source(CAT_HOUSE_PRICE)
ds_house_rental = get_latest_data_source(CAT_HOUSE_RENTAL)
ds_gdp = get_latest_data_source(CAT_GDP)
ds_interest_rate = get_latest_data_source(CAT_INTEREST_RATE)
ds_exchange_rate = get_latest_data_source(CAT_EXCHANGE_RATE)
ds_foreign_invest = get_latest_data_source(CAT_FOREIGN_INVEST)
ds_vacancy = get_latest_data_source(CAT_HOUSE_VACANCY)
ds_household = get_latest_data_source(CAT_HOUSEHOLD)
ds_hibor = get_latest_data_source(CAT_HIBOR)

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
            'households total (\'000)', 
            'households private owner-occupiers (%)',
            'households private owner-occupiers (\'000)',
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
    merged_df = merged_df.join(load_df(ds_hibor['path']).set_index('period')[[
            'HIBOR 1M (% p.a.)', 
        ]], on='period', how='outer', sort=True)
    merged_df = merged_df.join(load_df(ds_exchange_rate['path']).set_index('period')[[
            'exchange rate CNY to HKD', 
            'exchange rate USD to HKD', 
        ]], on='period', how='outer', sort=True)
    merged_df = merged_df.join(load_df(ds_foreign_invest['path']).set_index('period')[[
            'year end direct investment position all (HK$B)', 
            'year end direct investment position CN (HK$B)', 
            'year end direct investment position GB (HK$B)', 
            'year end direct investment position VG (HK$B)', 
            'year end direct investment position KY (HK$B)', 
        ]], on='period', how='outer', sort=True)
    merged_df.set_index('period', inplace=True)
    merged_df.index = pd.to_datetime(merged_df.index)
    merged_df.sort_index(inplace=True)
    # select data from 1993
    merged_df = merged_df.loc['1995-01-01':]
    # additional column calculation
    merged_df['house total supply (num)'] = (merged_df['house vacancy all (num)'] * 100 / merged_df['house vacancy all (%)']).round()
    # merged_df['house total supply growth rate (% rate YoY)'] = (merged_df['house total supply (num)'].pct_change() * 100).round(2)
    merged_df['house occupied all (num)'] = merged_df['house total supply (num)'] - merged_df['house vacancy all (num)']
    merged_df['house occupied by owners (num)'] = merged_df['households private owner-occupiers (\'000)'] * 1000
    merged_df['house occupied by owners (num)'] = merged_df['house occupied by owners (num)'].shift(1)
    merged_df['house occupied by tenants (num)'] = merged_df['house occupied all (num)'] - merged_df['house occupied by owners (num)']
    merged_df['house occupied by tenants (%)'] = (merged_df['house occupied by tenants (num)'] / merged_df['house total supply (num)'] * 100).round(1)
    merged_df['house occupied by owners (%)'] = (merged_df['house occupied by owners (num)'] / merged_df['house total supply (num)'] * 100).round(1)
    merged_df['P plan mortgage rate (% p.a.)'] = merged_df['best lending rate (% p.a.)'] - 1.75
    merged_df['H plan mortgage rate (% p.a.)'] = merged_df[['best lending rate (% p.a.)', 'HIBOR 1M (% p.a.)']].apply(
        lambda x: min(x['best lending rate (% p.a.)'] - 1.75, x['HIBOR 1M (% p.a.)'] + 1.3) if pd.notnull(x['best lending rate (% p.a.)']) and pd.notnull(x['HIBOR 1M (% p.a.)']) else np.nan, 
        axis=1)
    # rename columns
    merged_df.rename(columns={
        'GDP seasonally adjusted (% QoQ rate)': 'GDP growth rate (%)',
        'implicit price deflator (% YoY rate)': 'inflation rate (%)'
    }, inplace=True)
    # fill in details for each tendency range
    house_price_index_column = 'house price all (idx 1999=100)'
    for idx, tr in enumerate(TENDENCY_RANGES):
        start_value = merged_df.loc[tr['start'], house_price_index_column]
        end_value = merged_df.loc[tr['end'], house_price_index_column]
        tr['idx'] = idx + 1
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
    st.header('📈Overview: the rises & falls of HK house market')
    
    # house price line chart
    line_chart = px.line(merged_df[[house_price_index_column]], 
                title='💵HK avg house price index (1999=100)',
                # x='period', 
                # y=sel_columns, 
                markers=False,
                labels={"period": "time", "value": "price index"},
                )
    update_line_chart(line_chart)
    line_chart.update_layout(showlegend=False, margin=dict(b=0))
    draw_tendency_rects(line_chart)
    
    rate_chart = px.line(merged_df[['house price growth all (% rate MoM)']], 
                title='💵HK avg house price growth rate',
                # x='period', 
                # y=sel_columns, 
                markers=False,
                labels={"period": "time", "value": "%"},
                )
    update_line_chart(rate_chart)
    rate_chart.update_layout(showlegend=False, margin=dict(b=0))
    draw_tendency_rects(rate_chart)
    
    st.plotly_chart(line_chart, theme="streamlit")
    st.plotly_chart(rate_chart, theme="streamlit")
    # write desc
    rise_trs = [tr for tr in TENDENCY_RANGES if tr['tendency'] == 'rise']
    st.write(f"🔼{len(rise_trs)} major rises:")
    tabs = st.tabs([f"#{tr['idx']}. {tr['start'][:7]} ~ {tr['end'][:7]}" for tr in rise_trs])
    for idx, tab in enumerate(tabs):
        with tab:
            write_tendency_desc(rise_trs[idx])
    fall_trs = [tr for tr in TENDENCY_RANGES if tr['tendency'] == 'fall']
    st.write(f'🔽{len(fall_trs)} major falls:')
    tabs = st.tabs([f"#{tr['idx']}. {tr['start'][:7]} ~ {tr['end'][:7]}" for tr in fall_trs])
    for idx, tab in enumerate(tabs):
        with tab:
            write_tendency_desc(fall_trs[idx])

st.header('🔬Analysis')

# Observe macro economy
st.subheader('Macro economy factors', divider='grey')
[gdp_tab, ] = st.tabs(['💹GDP',])

# GDP
with gdp_tab:
    st.write('**GDP growth rate is a good indicator when it\'s below zero or spikes**')
    # gdp
    fig = px.line(merged_df, 
                 y=['house price all (idx 1999=100)', 'GDP growth rate (%)'], 
                 title='HK house price 🆚 GPD growth rate',
                 facet_col="variable",
                 facet_col_wrap=1,
                 facet_row_spacing=TOTAL_FACET_ROW_SPACING / 2,
                 color=px.NO_COLOR,
                 height=SINGLE_SUBPLOT_HEIGHT * 2,)
    update_line_chart(fig)
    fig.update_yaxes(matches=None)
    fig.update_layout(showlegend=False, margin=dict(b=0))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=", maxsplit=1)[-1]))
    draw_tendency_rects(fig, with_annotation=True)
    # add vacancy as bar
    # vacancy_bar = go.Bar(name='vacancy', x=merged_df.index, y=merged_df['house vacancy all (num)'], 
    #                      marker_color='red', opacity=0.5,)
    # fig.add_trace(vacancy_bar, row=1, col=1)
    
    st.plotly_chart(fig, theme="streamlit")
    st.markdown("""
        **Note:** GDP growth rate is calculated by quarter and is seasonally adjusted. 
        
        **Observation:**
        
        + When GDP decreases (growth rate < 0), house price will most certainly to drop.  
        This accounts for period #2, #4 and #10.
        + When GDP growth rate spikes, house price will often increase, as in period #3 & #5.
        + Notice that during period #3, house price is still decreasing despite the rise of GDP.  
        This indicates that some stronger factors are at play.
    """)
    

# Observe supply
st.subheader('Supply factors', divider='grey')
[supply_tab, vacancy_tab] = st.tabs(['🏘️House supply', '🧳House vacancy'])

# house supply & vacancy
with supply_tab:
    st.write('**House supply increases steadily, making it less correlated with house price**')
    # house supply
    fig = px.line(merged_df, 
                 y=['house price all (idx 1999=100)', 'house total supply (num)'], 
                 title='HK house price 🆚 supply & vacancy',
                 facet_col="variable",
                 facet_col_wrap=1,
                 facet_row_spacing=TOTAL_FACET_ROW_SPACING / 2,
                 color=px.NO_COLOR,
                 height=SINGLE_SUBPLOT_HEIGHT * 2,)
    update_line_chart(fig)
    fig.update_yaxes(matches=None)
    fig.update_layout(showlegend=False, margin=dict(b=0))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=", maxsplit=1)[-1]))
    draw_tendency_rects(fig, with_annotation=True)
    # add vacancy as bar
    # vacancy_bar = go.Bar(name='vacancy', x=merged_df.index, y=merged_df['house vacancy all (num)'], 
    #                      marker_color='red', opacity=0.5,)
    # fig.add_trace(vacancy_bar, row=1, col=1)
    
    st.plotly_chart(fig, theme="streamlit")
    st.markdown("""
        **Note:** the sudden drop for house total supply in 2003 is due to the exclusion of village houses in the calculation. 
        
        **Observation:**
        
        + House supply has been increasing steadily, making its influence on house price not as significant as expected.
    """)
    
with vacancy_tab:
    st.write('**When house vacancy is high, it negatively correlates with house price**')
    # house supply
    fig = px.line(merged_df, 
                 y=['house price all (idx 1999=100)', 'house vacancy all (%)'], 
                 title='HK house price 🆚 supply & vacancy',
                 facet_col="variable",
                 facet_col_wrap=1,
                 facet_row_spacing=TOTAL_FACET_ROW_SPACING / 2,
                 color=px.NO_COLOR,
                 height=SINGLE_SUBPLOT_HEIGHT * 2,)
    update_line_chart(fig)
    fig.update_yaxes(matches=None)
    fig.update_layout(showlegend=False, margin=dict(b=0))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=", maxsplit=1)[-1]))
    fig.add_hline(y=5, line_dash="dot", line_color="pink", row=1)
    draw_tendency_rects(fig, with_annotation=True)
    # add vacancy as bar
    # vacancy_bar = go.Bar(name='vacancy', x=merged_df.index, y=merged_df['house vacancy all (num)'], 
    #                      marker_color='red', opacity=0.5,)
    # fig.add_trace(vacancy_bar, row=1, col=1)
    
    st.plotly_chart(fig, theme="streamlit")
    st.markdown("""
        **Note:** the sudden drop for house total supply in 2004 is due to the exclusion of village houses in the calculation. 
        
        **Observation:**
        
        + Vacancy rate has a negative correlation with house price, when it fluctuates, especially above 5%.  
        This accounts for period #2 (increase) and period #3 (decrease).
        + After Jan 2018, vacancy rate has been relatively stable, making it insignificant to house price fluctuation.
    """)

with st.container():
    # bar graph
    house_vacancy_df = merged_df[~merged_df['house occupied by tenants (num)'].isnull()]
    house_vacancy_df.reset_index(drop=False, inplace=True)
    bar = px.bar(house_vacancy_df,
                    x='period',
                    y=['house vacancy all (%)', 'house occupied by tenants (%)', 'house occupied by owners (%)'],
                    title='See also: HK vacancy & occupied house percentage by year',
                    labels={
                        "variable": "category", 
                        "value": "percentage (%)",
                        "period": "year",},
                    text_auto=True,
                    hover_data={
                        'house vacancy all (num)': ':,.0f',
                        'house occupied by tenants (num)': ':,.0f',
                        'house occupied by owners (num)': ':,.0f',
                        'period': "|%Y"},
                    barmode='stack',)
    bar.update_xaxes(minor_ticks='inside', showgrid=True)
    bar.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
        margin=dict(b=0),
    )
    st.plotly_chart(bar, theme="streamlit")


# Observe demand
st.subheader('Demand factors', divider='grey')
[household_tab, interest_rate_tab, circulation_rate_tab, mainland_capital_tab] = st.tabs(['👨‍👩‍👧‍👦Household', '💳Interest rate', '💸Currency in circulation', '🌏Mainland capital'])

# Household
with household_tab:
    st.write('**Household stats doesn\'t say much, as it\'s fairly steady**')
    # household
    fig = px.line(merged_df, 
                 y=['house price all (idx 1999=100)', 'households total (\'000)', 'households private owner-occupiers (%)'], 
                 title='HK house price 🆚 household stats',
                 facet_col="variable",
                 facet_col_wrap=1,
                 facet_row_spacing=TOTAL_FACET_ROW_SPACING / 3,
                 color=px.NO_COLOR,
                 height=SINGLE_SUBPLOT_HEIGHT * 3,)
    update_line_chart(fig)
    fig.update_yaxes(matches=None)
    fig.update_layout(showlegend=False, margin=dict(b=0))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=", maxsplit=1)[-1]))
    # fig.add_hline(y=50, line_dash="dot", line_color="pink", row=1)
    draw_tendency_rects(fig, with_annotation=True)
    # add vacancy as bar
    # vacancy_bar = go.Bar(name='vacancy', x=merged_df.index, y=merged_df['house vacancy all (num)'], 
    #                      marker_color='red', opacity=0.5,)
    # fig.add_trace(vacancy_bar, row=1, col=1)
    
    st.plotly_chart(fig, theme="streamlit")
    st.markdown("""
        **Observation:**
        
        + Household number in HK has been increasing steadily in a linear manner.
        + Owner-occupier percentage for private properties has been stable around 36%.
        + These two points indicate that the demand for house is stably ever growing. The demand will increase more when investment demand is high.
    """)
    
# Interest rate
with interest_rate_tab:
    st.write('**Interest rate gives contradictory signals, therefore is a weak indicator**')
    if st.toggle('Show house price chart', value=False):
        # house price index
        price_chart = px.line(merged_df[[house_price_index_column]], 
                    title='💵HK avg house price index (1999=100)',
                    # x='period', 
                    # y=sel_columns, 
                    markers=False,
                    labels={"period": "time", "value": "price index"},
                    )
        update_line_chart(price_chart)
        price_chart.update_layout(showlegend=False, margin=dict(b=0))
        draw_tendency_rects(price_chart)
        st.plotly_chart(price_chart, theme="streamlit")
    # interest rate
    ir_df = merged_df[~merged_df['HIBOR 1M (% p.a.)'].isnull()]
    ir_df.reset_index(drop=False, inplace=True)
    interest_chart = px.line(ir_df, 
                title='🏦Various interest rates in HK',
                x='period', 
                y=['H plan mortgage rate (% p.a.)', 'P plan mortgage rate (% p.a.)',
                                        'HIBOR 1M (% p.a.)', 'best lending rate (% p.a.)'], 
                markers=False,
                labels={"period": "time", "value": "% p.a."},
                hover_data={
                    'period': False,
                },)
    update_line_chart(interest_chart)
    interest_chart.update_layout(
        showlegend=True, 
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="right",
            x=1
        ), 
        margin=dict(b=0))
    draw_tendency_rects(interest_chart)
    interest_chart.for_each_annotation(lambda a: a.update(text=a.text.replace(" (% p.a.)", "")))
    st.plotly_chart(interest_chart, theme="streamlit")
   
    st.markdown("""
        **Note:**
        + H plan & P plan mortage rate are calculated using current standard, i.e.  
        P plan mortgage rate = best lending rate - 1.75%  
        H plan mortgage rate = min(P plan mortgage rate - 1.75%, HIBOR (1 month) + 1.3%)
        + Obviously, H plan is generally preferred by borrowers.
        
        **Observation:**
        
        + Interest rate gives contradictory signals to house price.
        + This is due to the fact that interest rate is set as a policy tool to influence market, instead of indicating current market status.
    """)

# Currency in circulation
with circulation_rate_tab:
    st.write('**Currency in circulation greatly affects house price when in extreme**')
    # exchange rate
    fig = px.line(merged_df, 
                 y=['house price all (idx 1999=100)', 'exchange rate USD to HKD'], 
                 title='HK house price 🆚 exchange rate of USD to HKD',
                 facet_col="variable",
                 facet_col_wrap=1,
                 facet_row_spacing=TOTAL_FACET_ROW_SPACING / 2,
                 color=px.NO_COLOR,
                 height=SINGLE_SUBPLOT_HEIGHT * 2,)
    update_line_chart(fig)
    fig.update_yaxes(matches=None)
    fig.update_layout(showlegend=False, margin=dict(b=0))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=", maxsplit=1)[-1]))
    fig.add_hline(y=7.8, line_dash="dot", line_color="pink", row=1, annotation_text="baseline rate", annotation_position="bottom right")
    draw_tendency_rects(fig, with_annotation=True)
    # add vacancy as bar
    # vacancy_bar = go.Bar(name='vacancy', x=merged_df.index, y=merged_df['house vacancy all (num)'], 
    #                      marker_color='red', opacity=0.5,)
    # fig.add_trace(vacancy_bar, row=1, col=1)
    
    st.plotly_chart(fig, theme="streamlit")
    st.markdown("""
        **Observation:**
        
        + Exchange rate between USD and HKD can be seen as a indicator of currency in circulation, especially when in extreme, i.e. when it reaches 7.75 or 7.85.
        + This is because that under such situations, the monetary policy of HK is affected as a result of the linked exchange rate system.
        + When USD to HKD exchange rate reaches 7.75 (strong side band), HKMA will have to increase the money supply and house market will bloom.  
        Conversely, when it reaches 7.85 (weak side band), HKMA will have to decrease the money supply, which will threathen the house market.
        + This is a stronger indicator than plaini interest rate, because interest rate can be influenced by other factors, e.g. the profit pressure of the banks.
        By contrast, the exchange rate is a direct result of the monetary policy of the region, and has a substantial impact on the house market.
        + This trait can be clearly seen in period #5, #7 (increase) and #10 (decrease).
    """)

# Mainland capital
with mainland_capital_tab:
    st.write('**Mainland capital largely influences HK house market**')
    fig = px.line(merged_df, 
                 y=['house price all (idx 1999=100)', 'exchange rate CNY to HKD'], 
                 title='HK house price 🆚 exchange rate of CNY to HKD',
                 facet_col="variable",
                 facet_col_wrap=1,
                 facet_row_spacing=TOTAL_FACET_ROW_SPACING / 2,
                 color=px.NO_COLOR,
                 height=SINGLE_SUBPLOT_HEIGHT * 2,)
    update_line_chart(fig)
    fig.update_yaxes(matches=None)
    fig.update_layout(showlegend=False, margin=dict(b=0))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=", maxsplit=1)[-1]))
    fig.add_hline(y=1, line_dash="dot", line_color="pink", row=1, annotation_text="CNY:HKD=1:1", annotation_position="top right")
    draw_tendency_rects(fig, with_annotation=True)
    # add vacancy as bar
    # vacancy_bar = go.Bar(name='vacancy', x=merged_df.index, y=merged_df['house vacancy all (num)'], 
    #                      marker_color='red', opacity=0.5,)
    # fig.add_trace(vacancy_bar, row=1, col=1)
    
    st.plotly_chart(fig, theme="streamlit")
    st.markdown("""
        **Observation:**
        
        + Capital from mainland China has been a significant buyer in the HK house market due to geopolitical reasons.  
        Every major rise & fall in house price has a corresponding change in the exchange rate of CNY to HKD since 2003.
        + The change of exchange rate between CNY and HKD can be seen as the change of cost for mainland buyers to purchase HK properties.
        Therefore a good indicator of mainland capital inflow.
        + This can be explained in that when CNY is stronger, mainland buyers will have more purchasing power in HK. And vice versa.
    """)
 
st.header('📑Conclusion')
st.markdown("""
Four indicators are showing strong correlation with HK house price:
1. **GDP growth rate**: when it's below zero or spikes, house price will drop or hike.
2. **House vacancy rate**: when it fluctulates greatly, house price will be affected, especially when it's above 5%.
3. **Exchange rate of USD to HKD**: when it reaches 7.75 or 7.85, house price will bloom or threathen.
4. **Exchange rate of CNY to HKD**: when it changes, mainland capital will follow, which will greatly influence HK house market.   

However, there are also two principles to bear in mind:
1. **Correlation doesn't mean causation.** The indicators are not necissarily the cause of house price fluctuation.   
2. **These indicators are also correlated with each other.** Therefore, it's important to consider them as a whole, instead of individually.

With these in mind, when we are trying to depict the current and foreseeable house market, we should not only collect the data, but also gather the policy and the social-psychological trends towards this topic.  
""")

st.header('🔗Reference')
st.markdown("""
1. [Hong Kong Official Statistics by Subject - Census and Statistics Department, HKSAR](https://www.censtatd.gov.hk/en/page_8000.html)
2. [Property Market Statistics - Rating and Valuation Department, HKSAR](https://www.rvd.gov.hk/en/publications/property_market_statistics.html)
2. [(Chinese) 香港房价：解析汇率、利率和房价的勾稽关系 - 雪球](https://xueqiu.com/7462290789/117244366)            
""")
    
# show raw data
if st.toggle('Show raw data', value=False):
    st.dataframe(merged_df)