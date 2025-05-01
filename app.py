import streamlit as st
import time
from utils.llm_connect import get_llm_client
from components.widgets import render_page_header, user_login_section, file_upload_section

# Apply custom styling
render_page_header()

# Choose your LLM provider
LLM_PROVIDER = "gemini"  # or "openai"

st.title("💬 Chat with Documents using AI")

# Get user email
user_email = user_login_section()

# File upload section
uploaded_file = file_upload_section()

# Initialize LLM client
if "llm_client" not in st.session_state:
    st.session_state.llm_client = get_llm_client(provider=LLM_PROVIDER)

# Initialize chat history
if "messages" not in st.session_state:
    welcome_msg = "👋 Welcome! You can:\n* Upload a document above to chat about it\n* Or just chat with me directly!"
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ...rest of your chat logic...
# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = f"Echo: {prompt}"
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
