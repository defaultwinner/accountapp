import streamlit as st

def render_page_header():
    st.markdown("""
    <style>
        /* Main background and text colors */
        .stApp {
            background-color: #BDDBEF;
            color: #262730;
        }
        
        /* Header styling */
        header {
            color: #FFFFFF !important;
        }
        
        .stApp h1 {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #FFFFFF !important;
        }
        
        /* Make regular Markdown text black */
        .stMarkdown p {
            color: #000000 !important;
        }
        .stMarkdown h3 {
            color: #000000 !important;
        }
        
        
        /* Chat message containers */
        .stChatMessage {
            background-color: #F8F9FA;
            border-radius: 10px;
            margin: 10px 0;
        }
        .stChatMessage li {
                color: #000000 !important;
        }
        
        .stFileUploader section {
            background-color: #F8F9FA !important;
            border-radius: 8px;
                color: #000000 !important;
        }
        .stFileUploader section small {
                color: #000000 !important;
        }
        .stFileUploader section button {
            # background-color: #F8F9FA !important;
            # border-radius: 8px;
            color: #FFFFFF !important;
        }
        
        /* User input box */
        .stTextInput input {
            border: 1px solid #E0E3E7;
            background-color: white;
            border-radius: 8px;
        }
        
        /* File uploader */
        .stUploadedFile {
            background-color: #F8F9FA;
            border-radius: 8px;
        }
        
        /* Button colors */
        .stButton>button {
            background-color: #1E88E5;
            color: white;
            border-radius: 20px;
        }
        
        /* Info boxes */
        .stAlert {
            background-color: #E3F2FD;
            color: #1E88E5;
            border-radius: 8px;
        }

        .stBottom .st-emotion-cache-hzygls {
            background-color: #BDDBEF !important;
        }
                
        }
    </style>
    """, unsafe_allow_html=True)

def user_login_section():
    """Render user login section"""
    col1, col2 = st.columns([2, 1])
    with col1:
        user_email = st.text_input(
            "📧 Enter your email to save chat history",
            key="user_email",
            placeholder="your.email@example.com"
        )
    if user_email and not "@" in user_email:
        st.warning("⚠️ Please enter a valid email address")
    return user_email

def file_upload_section():
    """Render file upload section"""
    uploaded_file = st.file_uploader(
        "Upload your accounting documents (optional)", 
        type=["pdf", "txt", "doc", "docx"],
        help=None,
        label_visibility="collapsed",
    )
    
    if uploaded_file:
        st.info(f"""
        **Current Document:**  
        📄 Name: {uploaded_file.name}  
        📝 Type: {uploaded_file.type}  
        📊 Size: {uploaded_file.size/1024:.1f} KB
        """)
    
    return uploaded_file