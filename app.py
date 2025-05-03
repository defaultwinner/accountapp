import streamlit as st
import time
from utils.llm_connect import get_llm_client
from components.widgets import render_page_header, user_login_section, file_upload_section

# Apply custom styling
render_page_header()

# Choose your LLM provider
LLM_PROVIDER = "grok"

st.title("💼 Accountant Busy? Ask Us Instead", anchor=False)

# Initialize LLM client
if "llm_client" not in st.session_state:
    st.session_state.llm_client = get_llm_client(provider=LLM_PROVIDER)

# Initialize chat history and show welcome message
if "messages" not in st.session_state:
    welcome_msg = """Trending Questions in Dubai:
- Time left to avoid AED 10,000 penalty?
- Key compliance tasks to avoid fines in 2025?
- How do I prep for investor due diligence?
- Optimise tax between London & Dubai?
- Ways to boost EBITDA in FY2025?
- Want a London Fintech CFO's POV on exit strategy?

Upload documents or ask accounting questions below!"""
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

    # Display welcome message
    with st.chat_message("assistant"):
        st.markdown(welcome_msg)

# File uploader below welcome message
uploaded_file = file_upload_section()
# Display file upload section
if uploaded_file:
    st.session_state.messages.append({"role": "user", "content": f"Uploaded file: {uploaded_file.name}"})
    with st.chat_message("user"):
        st.markdown(f"Uploaded file: {uploaded_file.name}")

if uploaded_file:
    st.info(f"""📄 Processing: {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)""")

# Display rest of chat history
if len(st.session_state.messages) > 1:  # Skip welcome message
    for message in st.session_state.messages[1:]:
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
                user_email=None  # Removed user_email as it's no longer used
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
