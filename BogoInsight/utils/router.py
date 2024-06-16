import streamlit as st

from BogoInsight.configs.access import access_level

PAGES = [
    {
        "label": "BogoInsight",
        "icon": "👀",
        "link": "BogoInsight.py",
        "access": access_level['visitor'],
    },
    {
        "label": "HK House Price Analysis",
        "icon": "🏠",
        "link": "pages/hk_house_price.py",
        "access": access_level['visitor'],
    },
    {
        "label": "LLM Observation",
        "icon": "🤖",
        "link": "pages/llm_observation.py",
        "access": access_level['visitor'],
    },
    {
        "label": "GPU Stats",
        "icon": "🔦",
        "link": "pages/gpu_stats.py",
        "access": access_level['visitor'],
    },
    {
        "label": "Football Knockout Analysis",
        "icon": "⚽",
        "link": "pages/football_knockout.py",
        "access": access_level['visitor'],
    },
    {
        "label": "divider"
    },
    {
        "label": "Playground",
        "icon": "🎈",
        "link": "pages/playground.py",
        "access": access_level['visitor'],
    },
    {
        "label": "User Panel",
        "icon": "🧐",
        "link": "pages/user_panel.py",
        "access": access_level['visitor'],
    },
]

def render_toc_with_expander():
    with st.expander("👻 **Meet all insights**"):
        render_toc()
            
def render_toc():
    for page in PAGES:
        if page['label'] == "divider":
            st.divider()
            continue
        if st.session_state.get('access_level', 0) < page['access']:
            continue
        st.page_link(
            label=page['label'],
            icon=page['icon'],
            page=page['link'],
        )