import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. INITIAL SETUP
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("Gemini_key")

st.set_page_config(
    page_title="AI Chatbot Mentor",
    layout="wide"
)

# 2. CUSTOM CSS (Styling Labels & Removing Avatar Circles)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* General Font override */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide the circular avatar background */
    [data-testid="stChatMessageAvatarCustom"], 
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: transparent !important;
        border: none !important;
    }

    /* Custom Role Label Styling */
    .role-label {
        font-weight: 700;
        font-size: 0.75rem;
        color: #8892b0;
        margin-bottom: -10px;
        display: block;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* Message bubble adjustments */
    .stChatMessage {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #e2e8f0;
    }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SESSION STATE
if "started" not in st.session_state:
    st.session_state.started = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. SIDEBAR SETTINGS
with st.sidebar:
    st.title("Settings")
    
    MODULES = ["Python", "SQL", "Power BI", "EDA", "Machine Learning (ML)", "Deep Learning (DL)", "Generative AI (Gen AI)", "Agentic AI"]
    EXPERIENCE_LEVELS = ["1","2","3","4","5","7","9","11","14","15"]
    
    module = st.selectbox("Module", ["-- Select --"] + MODULES, disabled=st.session_state.started)
    experience = st.selectbox("Exp (Years)", ["-- Select --"] + EXPERIENCE_LEVELS, disabled=st.session_state.started)
    
    st.divider()

    if not st.session_state.started:
        if st.button("Initialize Mentor"):
            if module != "-- Select --" and experience != "-- Select --":
                st.session_state.module = module
                st.session_state.experience = experience
                st.session_state.started = True
                st.rerun()
            else:
                st.error("Please select all fields.")
    else:
        st.write(f" **Topic:** {st.session_state.module}")
        st.write(f"**Level:** Senior ({st.session_state.experience}y)")
        if st.button("Reset Session"):
            st.session_state.clear()
            st.rerun()

# 5. MAIN INTERFACE
st.title("🎓 AI Mentorship Session")

if not st.session_state.started:
    st.info("Please set your Module and Experience in the sidebar to begin.")
else:
    # Model Setup - Fixed version name
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    def get_mentor_response(user_input):
        system_prompt = f"You are a mentor in {st.session_state.module} with {st.session_state.experience} years exp. Provide industry-standard advice. Only answer topic-relevant questions."
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])
        chain = prompt | llm
        return chain.invoke({"question": user_input}).content

    # Render History with text-based operation names
    for role, msg in st.session_state.chat_history:
        avatar_char = "👤" if role == "user" else "🤖"
        label_text = "LEARNER" if role == "user" else "MENTOR"
        
        with st.chat_message(role, avatar=avatar_char):
            st.markdown(f"<span class='role-label'>{label_text}</span>", unsafe_allow_html=True)
            st.markdown(msg)

    # Chat Input
    if user_input := st.chat_input(f"Ask about {st.session_state.module}..."):
        # Learner Action
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Mentor Action
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing query..."):
                response = get_mentor_response(user_input)
                st.markdown(response)
                st.session_state.chat_history.append(("assistant", response))