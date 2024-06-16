import os
import sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from BogoInsight.configs.access import access_level
from BogoInsight.utils.router import render_toc

st.set_page_config(
    page_title='User Panel | BogoInsight', 
    page_icon='🧐'
)

def handle_unlock():
    pin = st.session_state.get('unlock_pin', '')
    if pin == st.secrets['access_pin']['admin']:
        st.session_state.update({'access_level': access_level['admin']})
        st.balloons()
    elif pin == st.secrets['access_pin']['friend']:
        st.session_state.update({'access_level': access_level['friend']})
        st.balloons()
    else:
        st.toast('Invalid pin! Please try again.', icon='❌')
        
def handle_reset():
    st.session_state.update({'access_level': access_level['visitor']})
    st.toast('Goodbye!', icon='👋')

with st.sidebar:
    render_toc()

cur_access_level = st.session_state.get('access_level', access_level['visitor'])

if cur_access_level == access_level['visitor']:
    st.title('🎇Welcome visitor!')
    st.header('🔐Unlock more content?')
    with st.form('unlock_form', border=False):
        pin = st.text_input('Please enter the secret pin!', type='password', key='unlock_pin')
        submitted = st.form_submit_button('Unlock', on_click=handle_unlock)
            
else:
    if cur_access_level == access_level['friend']:
        st.title('🎇Hello dear friend!')
        st.write('🔓You have unlocked some extra content. Go check it out!')
    elif cur_access_level == access_level['admin']:
        st.title('🎇Welcome back Bogo!')
    logout_clicked = st.button('Reset identity', type='primary', on_click=handle_reset)