import streamlit as st
import os
from datetime import datetime
from agent import AgentPipeline
from database import ChatDatabase
import uuid

# Page config
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = AgentPipeline()
    st.session_state.db = ChatDatabase()

if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = f"session_{uuid.uuid4().hex[:8]}"

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'loaded_pdf_name' not in st.session_state:
    st.session_state.loaded_pdf_name = None

if 'pdf_load_warning' not in st.session_state:
    st.session_state.pdf_load_warning = None

# Helper function to load PDF
def load_pdf_into_rag(pdf_path: str, pdf_name: str):
    """Load PDF and update tracking"""
    try:
        success = st.session_state.agent.rag_tool.load_pdf(pdf_path)
        if success:
            st.session_state.loaded_pdf_name = pdf_name
            st.session_state.pdf_load_warning = None
            return True
        return False
    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")
        return False

# Sidebar
with st.sidebar:
    st.title("🤖 AI Chat Assistant")
    st.markdown("---")
    
    # PDF Upload Section
    st.subheader("📄 Upload PDF")
    
    # Show currently loaded PDF
    if st.session_state.loaded_pdf_name:
        st.success(f"✅ Current: {st.session_state.loaded_pdf_name}")
        if st.button("Clear PDF", use_container_width=True):
            st.session_state.loaded_pdf_name = None
            st.session_state.agent.rag_tool.vectorstore = None
            st.session_state.agent.rag_tool.current_pdf_name = None
            st.rerun()
    
    uploaded_file = st.file_uploader("Upload a PDF for Q&A", type=['pdf'], key="pdf_uploader")
    
    if uploaded_file is not None:
        pdf_path =uploaded_file.name
        
        # Save uploaded file
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load PDF if different from current
        if st.session_state.loaded_pdf_name != uploaded_file.name:
            if st.button("Load PDF", use_container_width=True):
                with st.spinner("Loading PDF..."):
                    if load_pdf_into_rag(pdf_path, uploaded_file.name):
                        st.success(f"✅ Loaded: {uploaded_file.name}")
                        st.rerun()
    
    st.markdown("---")
    
    # Session Management
    st.subheader("💬 Chat Sessions")
    
    if st.button("➕ New Session", use_container_width=True):
        st.session_state.current_session_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.session_state.pdf_load_warning = None
        st.rerun()
    
    st.markdown("---")
    
    # Previous Sessions
    st.subheader("📋 Previous Sessions")
    sessions = st.session_state.db.get_all_sessions()
    
    if sessions:
        for session in sessions[:10]:
            session_id = session['session_id']
            message_count = session['message_count']
            last_message = session['last_message']
            pdf_name = session.get('pdf_name')
            
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(last_message).strftime("%m/%d %H:%M")
            except:
                timestamp = "Unknown"
            
            # Create session label
            pdf_indicator = f"📄 {pdf_name[:15]}..." if pdf_name else "🌤️ Weather"
            button_label = f"{session_id[:12]}...\n{pdf_indicator}\n({message_count} msgs) {timestamp}"
            
            if st.button(button_label, key=session_id, use_container_width=True):
                # Get session PDF
                session_pdf = st.session_state.db.get_session_pdf(session_id)
                
                if session_pdf:
                    # Try to switch to that PDF's collection
                    if st.session_state.agent.rag_tool.switch_to_pdf(session_pdf):
                        st.session_state.loaded_pdf_name = session_pdf
                        st.session_state.pdf_load_warning = None
                    else:
                        # Collection doesn't exist
                        st.session_state.pdf_load_warning = (
                            f"⚠️ This session used **{session_pdf}** but that PDF's data "
                            f"is not in the database. Please re-upload **{session_pdf}** to continue."
                        )
                        st.session_state.loaded_pdf_name = None
                else:
                    st.session_state.pdf_load_warning = None
                
                # Load session
                st.session_state.current_session_id = session_id
                history = st.session_state.db.get_session_history(session_id)
                st.session_state.messages = history
                st.rerun()
    else:
        st.info("No previous sessions")
    
    st.markdown("---")
    
    # Current Session Info
    st.subheader("ℹ️ Current Session")
    st.text(f"ID: {st.session_state.current_session_id[:16]}...")
    st.text(f"Messages: {len(st.session_state.messages)}")
    session_pdf = st.session_state.db.get_session_pdf(st.session_state.current_session_id)
    if session_pdf:
        st.text(f"PDF: {session_pdf[:20]}...")

# Main Chat Interface
st.title("💬 AI Chat Assistant")
st.caption("Ask about weather or query your uploaded PDF!")

# Display session and PDF status
col1, col2 = st.columns([2, 1])
with col1:
    st.info(f"📍 Session: **{st.session_state.current_session_id}**")
with col2:
    if st.session_state.loaded_pdf_name:
        st.success("📄 PDF Loaded")
    else:
        st.warning("⚠️ No PDF")

# Show PDF context warning
if st.session_state.pdf_load_warning:
    st.warning(st.session_state.pdf_load_warning)

# Chat Messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "human":
            with st.chat_message("user"):
                st.write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)

# Chat Input
user_query = st.chat_input("Ask me anything about weather or your PDF...")

if user_query:
    st.session_state.messages.append({"role": "human", "content": user_query})
    
    with st.chat_message("user"):
        st.write(user_query)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Set current PDF name
                if st.session_state.loaded_pdf_name:
                    st.session_state.agent.rag_tool.current_pdf_name = st.session_state.loaded_pdf_name
                
                result = st.session_state.agent.run(
                    query=user_query,
                    session_id=st.session_state.current_session_id,
                    chat_history=st.session_state.messages[:-1]
                )
                
                answer = result.get('final_answer', 'No response generated.')
                intent = result.get('intent', 'unknown')
                
                # Display intent
                if intent == "weather":
                    st.markdown("🌤️ **Intent:** Weather Query")
                elif intent == "document":
                    st.markdown("📄 **Intent:** Document Query")
                    if st.session_state.loaded_pdf_name:
                        st.caption(f"Using PDF: {st.session_state.loaded_pdf_name}")
                
                st.write(answer)
                
                # Show sources
                if intent == "document" and result.get('rag_response'):
                    sources = result['rag_response'].get('sources', [])
                    if sources:
                        with st.expander(f"📚 Sources Used ({len(sources)} documents)"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"**Source {i}:**")
                                st.code(source.get('content', 'No content'), language=None)
                                st.caption(f"Metadata: {source.get('metadata', {})}")
                                if i < len(sources):
                                    st.markdown("---")
                
                st.session_state.messages.append({"role": "ai", "content": answer})
                
                if result.get('error'):
                    st.error(f"⚠️ Error: {result['error']}")
                
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(f"❌ {error_msg}")
                st.session_state.messages.append({"role": "ai", "content": error_msg})

# Footer
st.markdown("---")
st.caption("Powered by LangChain, LangGraph & Streamlit | Built for AI Engineer Assignment")