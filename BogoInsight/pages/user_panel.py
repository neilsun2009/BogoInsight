import os
import sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from BogoInsight.configs.access import access_level
from BogoInsight.utils.router import render_toc
from BogoInsight.utils.streamlit_utils import render_unlock_form

st.set_page_config(
    page_title='User Panel | BogoInsight', 
    page_icon='🧐'
)
    
def handle_reset():
    st.session_state.update({'access_level': access_level['visitor']})
    st.toast('Goodbye!', icon='👋')

with st.sidebar:
    render_toc()

cur_access_level = st.session_state.get('access_level', access_level['visitor'])

if cur_access_level == access_level['visitor']:
    st.title('🎇Welcome visitor!')
    st.header('🔐Unlock more content?')
    render_unlock_form()
            
else:
    if cur_access_level == access_level['friend']:
        st.title('🎇Hello dear friend!')
        st.write('🔓You have unlocked some extra content. Go check it out!')
    elif cur_access_level == access_level['admin']:
        st.title('🎇Welcome back Bogo!')
    logout_clicked = st.button('Reset identity', type='primary', on_click=handle_reset)