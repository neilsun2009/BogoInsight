import streamlit as st
from BogoInsight.configs.access import access_level


def render_unlock_form():
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
   
    with st.form('unlock_form', border=False):
        pin = st.text_input('Please enter the secret pin!', type='password', key='unlock_pin')
        submitted = st.form_submit_button('Unlock', on_click=handle_unlock)