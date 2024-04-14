import os
import pandas as pd
import streamlit as st

@st.cache_data
def get_data_sources():
    # read data from data/ folder
    data_sources = []
    for category in os.listdir('data'):
        for file in os.listdir(f'data/{category}'):
            if file.endswith('.csv'):
                data_sources.append({
                    'category': category.replace('_', ' ').title(),
                    'name': file.replace('.csv', ''),
                    'path': f'data/{category}/{file}'
                })
    return data_sources

@st.cache_data
def get_latest_data_source(category):
    data_source = None
    for file in os.listdir(f'data/{category}'):
        if file.endswith('.csv'):
            if data_source is None or file > data_source.get('name', ''):
                data_source = {
                    'category': category.replace('_', ' ').title(),
                    'name': file.replace('.csv', ''),
                    'path': f'data/{category}/{file}'
                }
    if not data_source:
        raise FileNotFoundError(f"No data source found in category: {category}")
    return data_source

@st.cache_data
def load_df(path):
    return pd.read_csv(path)