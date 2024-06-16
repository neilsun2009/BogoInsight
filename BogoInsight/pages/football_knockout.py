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

from BogoInsight.configs.access import access_level
from BogoInsight.utils.data_utils import (
    get_latest_data_source, load_df,
)
from BogoInsight.utils.plot_utils import (
    gen_heatmap
)
from BogoInsight.utils.router import render_toc
from BogoInsight.utils.football_utils import get_nation_flag_html
from BogoInsight.utils.router import render_toc

CAT_FOOTBALL_KNOCKOUT = 'football_knockout_matches'

DEFAULT_SEEDED_TEAMS = {
    "FIFA World Cup": [
        "Brazil", "Italy", "Germany", "Argentina", "France", 
        "Spain", "England", "Netherlands", "Portugal",
    ],
    "UEFA Euro": [
        "Germany", "Spain", "France", "Italy", "Netherlands",
        "Portugal", "England",
    ],
    "Russia 2018": ["Belgium"],
    "Euro 2020": ["Belgium"],
}

st.set_page_config(
    page_title='Football Knockout Stage Analysis | BogoInsight', 
    page_icon='⚽',
)

st.title('⚽Football Knockout Stage Analysis')

cur_access_level = st.session_state.get('access_level', access_level['visitor'])

# sidebar
with st.sidebar:
    render_toc()
    st.divider()
    
    st.button('Reload data', on_click=lambda: st.cache_data.clear())

# get data
ds_football_knockout = get_latest_data_source(CAT_FOOTBALL_KNOCKOUT)
df_football_knockout = load_df(ds_football_knockout['path'])

tournaments = df_football_knockout['tournament'].unique()

with st.container():
    st.header('📢Introduction')
    st.markdown('''
                In this page, we are going to analyze the knockout stage matches of major football tournaments.
                
                The goal is to analyze the probability of the outcome of the matches based on the relative strengths of two opponents.
                With that in mind, we will split the matches into two categories:
                
                1. `Underdog vs Seed matches`: where a significantly stronger team is pitted against a weaker one.
                2. `Balanced matches`: where the two teams are of similar strength or skill level.
                
                And for the sake of simplicity (and easier calculation with odds), we will **only consider the result after regular time** (90 minutes) and exclude extra time or penalty shootouts.
                That said, the results of a match will be one of the following: **win**, **draw**, or **loss**.
                
                Thus, for the two categories of matches described above, we will further divide and calculate the probability of the following outcomes within each category:
                
                1. `Underdog vs Seed`:
                
                    1.1. Underdog wins
                    
                    1.2. Underdog and seed draw
                    
                    1.3. Seed wins
                    
                2. `Balanced`:
                    
                    2.1. Balanced match ends with a winner
                    
                    2.2. Balanced match ends in a draw
                
                Before we dive in, let's first select the tournament we want to analyze.
                ''')
    tournament = st.selectbox('Select tournament', tournaments, label_visibility='collapsed')

df_cur_tournament = df_football_knockout[df_football_knockout['tournament'] == tournament]
game_names = df_cur_tournament['game'].unique()

with st.container():
    st.header('📊Stats')
    
    # construct seeded teams for each game
    seeded_teams = {}
    with st.expander("✏️ Customize seeded teams", expanded=False):
        st.write("Customize the seeds selection for each knockout stage games in the selected tournament.")
        for game_name in game_names:
            df_cur_game = df_cur_tournament[df_cur_tournament['game'] == game_name]
            teams = set(df_cur_game['home_team'].unique()) | set(df_cur_game['away_team'].unique())
            teams = list(teams)
            teams.sort()
            default_seeds = DEFAULT_SEEDED_TEAMS.get(tournament, []).copy()
            default_seeds += DEFAULT_SEEDED_TEAMS.get(game_name, []).copy()
            default_seeds = list(set(teams) & set(default_seeds))
            default_seeds.sort()
            seeded_teams[game_name] = st.multiselect(f'**{game_name}**', teams, key=f'seed_{game_name}', default=default_seeds)
    
    # iterate and categorize matches
    # at the same time, construct another df to aggregate the stats
    df_agg = pd.DataFrame(columns=['game', 'match_category', 'result_category', 'count', 'percentage'])
    for game_name in game_names:
        df_cur_game = df_cur_tournament[df_cur_tournament['game'] == game_name]
        count_underdog_win, count_underdog_seed_draw, count_seed_win = 0, 0, 0
        count_balanced_no_draw, count_balanced_draw = 0, 0
        for i, row in df_cur_game.iterrows():
            home_team, away_team = row['home_team'], row['away_team']
            home_score, away_score, has_extra_time = row['home_score'], row['away_score'], row['has_extra_time']
            if home_team in seeded_teams[game_name] and away_team not in seeded_teams[game_name]:
                if has_extra_time:
                    count_underdog_seed_draw += 1
                elif home_score > away_score:
                    count_seed_win += 1
                else:
                    count_underdog_win += 1
            elif home_team not in seeded_teams[game_name] and away_team in seeded_teams[game_name]:
                if has_extra_time:
                    count_underdog_seed_draw += 1
                elif home_score > away_score:
                    count_underdog_win += 1
                else:
                    count_seed_win += 1
            else:
                if has_extra_time:
                    count_balanced_draw += 1
                else:
                    count_balanced_no_draw += 1
        df_agg = pd.concat([df_agg, pd.DataFrame([
            {'game': game_name, 'match_category': 'Underdog vs Seed', 'result_category': 'Underdog wins', 'count': count_underdog_win},
            {'game': game_name, 'match_category': 'Underdog vs Seed', 'result_category': 'Underdog/seed draw', 'count': count_underdog_seed_draw},
            {'game': game_name, 'match_category': 'Underdog vs Seed', 'result_category': 'Seed wins', 'count': count_seed_win},
            # {'game': game_name, 'match_category': 'Underdog vs Seed', 'result_category': 'All', 'count': count_underdog_win + count_underdog_seed_draw + count_seed_win},
            {'game': game_name, 'match_category': 'Balanced', 'result_category': 'Balanced no draw', 'count': count_balanced_no_draw},
            {'game': game_name, 'match_category': 'Balanced', 'result_category': 'Balanced draw', 'count': count_balanced_draw},
            # {'game': game_name, 'match_category': 'Balanced', 'result_category': 'All', 'count': count_balanced_no_draw + count_balanced_draw},
        ])], ignore_index=True)
        # st.subheader(f'🏆{game_name}')
        # st.dataframe(df_cur_game[['home_team', 'away_team', 'match_category', 'result_category', 'has_extra_time', 'home_score', 'away_score']])
    # calculate and append the sum of each result category across all games
    for category in ['Underdog vs Seed', 'Balanced']:
        if category == 'Underdog vs Seed':
            results = ['Underdog wins', 'Underdog/seed draw', 'Seed wins']
        else:
            results = ['Balanced no draw', 'Balanced draw']
        for result in results:
            df_agg = pd.concat([df_agg, pd.DataFrame([
                {'game': 'All', 'match_category': category, 'result_category': result, 'count': df_agg[(df_agg['game'] != 'All') & (df_agg['match_category'] == category) & (df_agg['result_category'] == result)]['count'].sum()},
            ])], ignore_index=True)
    # add percentage to each row
    df_agg['percentage'] = df_agg['count'] / df_agg.groupby(['game', 'match_category'])['count'].transform('sum') * 100
    
    # figures
    match_cat_tabs = st.tabs(['🛡️ Underdog vs Seed', '⚔️ Balanced'])
    for idx, tab in enumerate(match_cat_tabs):
        if idx == 0:
            match_cat = 'Underdog vs Seed'
        elif idx == 1:
            match_cat = 'Balanced'
        with tab:
            df_cur_cat = df_agg[df_agg['match_category'] == match_cat]
            show_counts = st.toggle('Show match counts', value=False, key=f'show_counts_{match_cat}')
            result_cat_fig = px.bar(
                df_cur_cat[df_cur_cat['game'] != 'All'] if show_counts else df_cur_cat, 
                title=f'📊{match_cat} result distribution',
                x='count' if show_counts else 'percentage', 
                y='game', 
                color='result_category', 
                barmode='stack',
                orientation='h', 
                text='count' if show_counts else 'percentage',
                text_auto=True if show_counts else '.2f',
                color_discrete_map={
                    'Underdog wins': 'rgb(255, 43, 43)',
                    'Underdog/seed draw': 'rgb(255, 170, 170)',
                    'Seed wins': 'rgb(255, 236, 236)',
                    'Balanced no draw': 'rgb(0, 104, 201)',
                    'Balanced draw': 'rgb(131, 201, 255)',
                },
                labels={
                    "percentage": "percentage (%)",
                },
                hover_data={
                    'percentage': ":,.2f",
                    'count': True,
                },
            )
            # match_cat_fig.update_yaxes(tickvals=[0, 4, 8, 12, 16] if tournament == 'FIFA World Cup' else [0, 5, 10, 15])
            result_cat_fig.update_layout(
                legend_title_text='',
                legend=dict(
                    orientation='h',
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(b=0),
            )
            st.plotly_chart(result_cat_fig, theme="streamlit")
    
    match_cat_fig = px.histogram(
        df_agg[df_agg['game'] != 'All'], 
        title='📊Overall match category distribution',
        x='game', 
        y='count', 
        color='match_category', 
        barmode='stack', 
        histfunc='sum',
        text_auto=True,
        color_discrete_map={
            'Underdog vs Seed': 'rgb(255, 43, 43)',
            'Balanced': 'rgb(0, 104, 201)',
        },
    )
    match_cat_fig.update_yaxes(tickvals=[0, 4, 8, 12, 16] if tournament == 'FIFA World Cup' else [0, 5, 10, 15])
    match_cat_fig.update_layout(
        # legend_title_text='Match category',
        legend_title_text='',
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )
    st.plotly_chart(match_cat_fig, theme="streamlit")
    
    # st.dataframe(df_agg)
    
    with st.expander('🎲Odds playground', expanded=True):
        if cur_access_level == access_level['visitor']:
            st.warning('🔒 This section is for verified user only.')
            go_to_user_panel = st.button('Go to user panel')
            if go_to_user_panel:
                st.switch_page('pages/user_panel.py')
        else:
            st.warning('''
                    ⚠️ This section is for mathematical purposes only and does not endorse or encourage gambling in any way. 
                    
                    The calculated results should not be taken as gambling recommendations. 
                    
                    If you were to gamble, please do so responsibly.
                    ''')
            home_input_col, draw_input_col, away_input_col = st.columns(3)
            with home_input_col:
                home_win_odds = st.number_input('Home win odds', value=2.36, min_value=1.0, step=0.1)
                home_is_seed = st.toggle('Home team is seeded', value=True)
            with draw_input_col:
                draw_odds = st.number_input('Draw odds', value=3.05, min_value=1.0, step=0.1)
            with away_input_col:
                away_win_odds = st.number_input('Away win odds', value=2.68, min_value=1.0, step=0.1)
                away_is_seed = st.toggle('Away team is seeded', value=True)
            # calculate probabilities for each scenario
            df_agg_all = df_agg[df_agg['game'] == 'All']
            underdog_win_prob = df_agg_all[(df_agg_all['match_category'] == 'Underdog vs Seed') & (df_agg_all['result_category'] == 'Underdog wins')]['percentage'].values[0] / 100
            seed_win_prob = df_agg_all[(df_agg_all['match_category'] == 'Underdog vs Seed') & (df_agg_all['result_category'] == 'Seed wins')]['percentage'].values[0] / 100
            underdog_seed_draw_prob = df_agg_all[(df_agg_all['match_category'] == 'Underdog vs Seed') & (df_agg_all['result_category'] == 'Underdog/seed draw')]['percentage'].values[0] / 100
            balanced_no_draw_prob = df_agg_all[(df_agg_all['match_category'] == 'Balanced') & (df_agg_all['result_category'] == 'Balanced no draw')]['percentage'].values[0] / 100
            balanced_draw_prob = df_agg_all[(df_agg_all['match_category'] == 'Balanced') & (df_agg_all['result_category'] == 'Balanced draw')]['percentage'].values[0] / 100
            # calculate each teams' win probability
            if (home_is_seed and away_is_seed) or (not home_is_seed and not away_is_seed):
                home_win_prob = balanced_no_draw_prob / 2
                draw_prob = balanced_draw_prob
                away_win_prob = balanced_no_draw_prob / 2
            elif home_is_seed and not away_is_seed:
                home_win_prob = seed_win_prob
                draw_prob = underdog_seed_draw_prob
                away_win_prob = underdog_win_prob
            else:
                home_win_prob = underdog_win_prob
                draw_prob = underdog_seed_draw_prob
                away_win_prob = seed_win_prob
            # print winning probabilities and expected profits
            home_result_col, draw_result_col, away_result_col = st.columns(3)
            with home_result_col:
                st.metric('Home win probability', value=f'{home_win_prob * 100:.2f}%')
                st.metric('Expected profit', value=f'{home_win_prob * home_win_odds - 1:.2f}')
            with draw_result_col:
                st.metric('Draw probability', value=f'{draw_prob * 100:.2f}%')
                st.metric('Expected profit', value=f'{draw_prob * draw_odds - 1:.2f}')
            with away_result_col:
                st.metric('Away win probability', value=f'{away_win_prob * 100:.2f}%')
                st.metric('Expected profit', value=f'{away_win_prob * away_win_odds - 1:.2f}')
        
            st.write('🔗 More on the mathematical calculation: [(Chinese) "Alternative investment" on World Cup](https://mp.weixin.qq.com/s?__biz=MzU0NTExNjE1NA==&mid=2247483871&idx=1&sn=e2cd88457dc6e8b93b21484ac6978712&chksm=fb709b4acc07125cf59fcce09d5c4304ce27bbbd8aab0ff2d2a3e258a9cbf53dd7bdf9b64c78&token=1101937543&lang=zh_CN#rd)')
    
    
with st.container():
    st.header('🤺Match details')
    game_name = st.selectbox('Select game', game_names)
    df_cur_game = df_cur_tournament[df_cur_tournament['game'] == game_name]
    rounds = df_cur_game['round'].unique()
    for round_name in rounds:
        st.subheader(f'{round_name}')
        # iterate and display each match
        for row in df_cur_game[df_cur_game['round'] == round_name].itertuples():
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; '>{row.date}</div>", unsafe_allow_html=True)
                st.markdown(f"""
                            <div style='display: flex; align-items: start; justify-content: center; margin-bottom: 10px'>
                                <div style="display: inline-block; text-align: center; width: 100px; 
                                    opacity: {'1' if row.home_score > row.away_score or row.has_extra_time else '0.5'}
                                ">
                                    {get_nation_flag_html(row.home_team)}<br/>
                                    <span style="display: inline-block;line-height: 1em">{row.home_team}</span><br/>
                                    <span style="display: inline-block;width:75px;border-radius:5px;
                                        font-size: 0.8em; text-align: center; color: white;
                                        background-color: {'#32a852' if row.home_team in seeded_teams[game_name] else '#FF2B2B'};
                                    ">
                                        {'Seed' if row.home_team in seeded_teams[game_name] else 'Underdog'}
                                    </span>
                                </div>
                                <span style='display: inline-block; text-align: center; width: 100px; align-self: center'>
                                    <span style='font-size: 2em;font-weight: bold;'>
                                        {row.home_score} - {row.away_score}
                                    </span><br/>
                                    <span>{'a.e.t.' if row.has_extra_time else '<br/>'}</span>
                                    <span style='font-weight: bold;'>{'<br/>' + str(int(row.pen_home_score)) + ' (pen.) ' + str(int(row.pen_away_score)) if row.has_penalties else ''}</span>
                                </span>
                                <div style="display: inline-block; text-align: center; width: 100px; 
                                    opacity: {'1' if row.away_score > row.home_score or row.has_extra_time else '0.5'}
                                ">
                                    {get_nation_flag_html(row.away_team)}<br/>
                                    <span style="display: inline-block;line-height: 1em">{row.away_team}</span><br/>
                                    <span style="display: inline-block;width:75px;border-radius:5px;
                                        font-size: 0.8em; text-align: center; color: white;
                                        background-color: {'#32a852' if row.away_team in seeded_teams[game_name] else '#FF2B2B'};
                                    ">
                                        {'Seed' if row.away_team in seeded_teams[game_name] else 'Underdog'}
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                st.caption(f"<p style='text-align: center;'>🔗<a href='{row.report_link}'>Match details</a></p>", unsafe_allow_html=True)
  
       