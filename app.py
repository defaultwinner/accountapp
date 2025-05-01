import streamlit as st
import time
from utils.llm_connect import get_llm_client
from components.widgets import render_page_header, user_login_section, file_upload_section

# Apply custom styling
render_page_header()

# Choose your LLM provider
LLM_PROVIDER = "gemini"

st.title("💬 Your AI Accountant")

# Get user email
user_email = user_login_section()

# File upload section
uploaded_file = file_upload_section()

# Initialize LLM client
if "llm_client" not in st.session_state:
    st.session_state.llm_client = get_llm_client(provider=LLM_PROVIDER)

# Initialize chat history
if "messages" not in st.session_state:
    welcome_msg = """👋 Welcome! I'm your AI Accountant. I can help you with:
* Accounting principles and concepts
* Financial statements analysis
* Bookkeeping questions
* Tax-related queries
* Business financial planning
* Audit-related topics

Please upload relevant documents or ask your accounting questions!"""
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask your accounting question..."):
    # Add context to ensure accounting-focused responses
    accounting_context = """You are an AI Accountant. Only answer questions related to accounting, 
    finance, taxation, auditing, or business financial matters. If the question is not related to 
    these topics, politely decline to answer and remind the user of your accounting focus."""
    
    formatted_prompt = f"{accounting_context}\n\nUser question: {prompt}"
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response with spinner
    with st.spinner("Thinking..."):
        try:
            response = st.session_state.llm_client.generate_response(
                messages=[{"role": "user", "content": formatted_prompt}],
                uploaded_file=uploaded_file,
                user_email=user_email
            )
            
            # Check if response indicates non-accounting question
            if "not related to accounting" in response.lower():
                response = """I can only assist with accounting and finance related questions. 
                Please ask me about:
                • Accounting principles
                • Financial statements
                • Bookkeeping
                • Taxation
                • Business finances
                • Auditing"""
                
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
