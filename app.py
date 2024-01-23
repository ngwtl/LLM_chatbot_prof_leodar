import streamlit as st
from ui import __login__
from tinydb import TinyDB
from datetime import datetime
from openai_chat import OPENAI_chat

st.set_page_config(page_title='Prof Leodar', page_icon = 'student')

__login__obj = __login__(auth_token = "courier_auth_token",
                    app_name = "LLM Assistance",
                    width = 200, height = 250,
                    logout_button_name = 'Logout', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN= __login__obj.build_login_ui()
username= __login__obj.get_username()

chatbot = OPENAI_chat("your openai api key")

if LOGGED_IN == True:
  db = TinyDB ('conversation.json')

  if 'messages' not in st.session_state:
    st.session_state.messages = []

  consent = __login__obj.get_consent()

  if consent:

    st.title("Prof. Leodar at your service")

    chat_history = str('')
    for message in st.session_state.messages:
       with st.chat_message(message['role']):
          st.markdown(message['content'])
       chat_history += str(message['role']) + ':' + message['content'] + '\n' 
    if len(chat_history.split('\n')) > 12:
      chat_history = chat_history [-12:]

    if prompt := st.chat_input('Write your message here'):
      st.chat_message('user').markdown(prompt)

      dt = datetime.now()
      db.insert({'role':username, 'content':prompt, 'time':str(dt)})

      st.session_state.messages.append({'role': 'user', 'content': prompt})

      response, context = chatbot.query_openai(query=prompt, history=chat_history)

      with st.chat_message('assistant'):
        st.markdown(response)

      dt = datetime.now()
      db.insert({'role': 'assistant', 'content': response, 'time': str(dt), 'reply_to': prompt, 'context': context})

      st.session_state.messages.append({'role': 'assistant', 'content': response})
  

