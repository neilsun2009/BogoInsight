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
        "label": "Playground",
        "icon": "🎈",
        "link": "pages/playground.py",
        "access": access_level['visitor'],
    },
    {
        "label": "Admin",
        "icon": "🔒",
        "link": "pages/admin.py",
        "access": access_level['admin'],
    },
]

def render_toc_with_expander():
    with st.expander("👻 **Meet all insights**"):
        render_toc()
            
def render_toc():
    for page in PAGES:
        if st.session_state.get('access_level', 0) < page['access']:
            continue
        st.page_link(
            label=page['label'],
            icon=page['icon'],
            page=page['link'],
        )