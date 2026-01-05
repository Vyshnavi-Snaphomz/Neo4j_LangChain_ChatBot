import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.agent_wrapper import AgentWrapper
from app.property_utils import compare_properties
from app.telemetry import setup_telemetry

from app.agent_wrapper import AgentWrapper
from app.property_utils import compare_properties
from app.telemetry import setup_telemetry
from app.history import SessionManager

# Initialize Telemetry (Cached to run once)
@st.cache_resource
def init_telemetry():
    setup_telemetry()

init_telemetry()

# Page configuration
st.set_page_config(
    page_title="Snaphomz AI Search",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS with Snaphomz brand guidelines
st.markdown("""
<style>
    /* Import Manrope font */
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');
    
    /* Global font */
    * {
        font-family: 'Manrope', sans-serif !important;
    }
    
    /* Main app styling */
    .main {
        background: #f8f9fa;
        padding-bottom: 100px;
    }
    
    /* Header styling */
    h1 {
        color: #2B2B2B;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle */
    .subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Chat messages - Enhanced */
    .stChatMessage {
        background-color: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    
    /* User message - Snaphomz Orange */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8C61 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.25);
    }
    
    .stChatMessage[data-testid="user-message"]:hover {
        box-shadow: 0 6px 16px rgba(255, 107, 53, 0.35);
    }
    
    /* Assistant message */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: white;
    }
    
    /* Chat input - Enhanced */
    .stChatInputContainer {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 2px solid #e9ecef;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stChatInputContainer:focus-within {
        border-color: #FF6B35;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.15);
    }
    
    /* Sidebar styling - Snaphomz Dark */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2B2B2B 0%, #1a1a1a 100%);
        color: white;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* Buttons - Snaphomz Orange */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8C61 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.25);
        font-size: 0.95rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 107, 53, 0.35);
        background: linear-gradient(135deg, #FF8C61 0%, #FF6B35 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: white;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e9ecef;
        padding: 0.75rem;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FF6B35;
        box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.1);
    }
    
    /* Trust indicators */
    .trust-badge {
        display: inline-block;
        background: rgba(255, 107, 53, 0.15);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.9rem;
        color: #FF6B35;
        font-weight: 600;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #FF6B35;
    }
    
    /* Metrics - Enhanced */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: #FF6B35;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6c757d;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Login form */
    .login-container {
        max-width: 500px;
        margin: 5rem auto;
        padding: 3rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Snaphomz logo styling */
    .snaphomz-logo {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8C61 100%);
        width: 80px;
        height: 80px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0 auto 1.5rem;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Links - ChatGPT style */
    .stMarkdown a {
        color: #FF6B35;
        text-decoration: none;
        font-weight: 600;
        border-bottom: 1px solid rgba(255, 107, 53, 0.3);
        transition: all 0.2s ease;
        padding-bottom: 1px;
    }
    
    .stMarkdown a:hover {
        color: #FF8C61;
        border-bottom-color: #FF6B35;
        background: rgba(255, 107, 53, 0.05);
        padding: 2px 4px;
        margin: -2px -4px;
        border-radius: 4px;
    }
    
    /* Code blocks for URLs */
    .stMarkdown code {
        background: rgba(255, 107, 53, 0.1);
        color: #FF6B35;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Manrope', monospace;
        font-size: 0.9em;
        font-weight: 600;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- USER AUTHENTICATION ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Login screen
if st.session_state.user_id is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        
        # Snaphomz logo
        st.markdown("""
        <div class='snaphomz-logo'>oc</div>
        """, unsafe_allow_html=True)
        
        st.title("🏠 Snaphomz AI Search")
        st.markdown("### Intelligent Property Search & Financial Analysis")
        
        st.markdown("""
        <div style='text-align: center; margin: 2rem 0;'>
            <span class='trust-badge'>🔒 Secure</span>
            <span class='trust-badge'>🤖 AI-Powered</span>
            <span class='trust-badge'>📊 Data-Driven</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("#### Sign In to Continue")
            username = st.text_input("Username or Email", placeholder="e.g., john.doe@example.com")
            submit = st.form_submit_button("🚀 Start Searching", use_container_width=True)
            
            if submit and username:
                st.session_state.user_id = username.strip().lower()
                st.rerun()
        
        st.info("💡 **Your Privacy Matters:** Each user gets isolated chat sessions. Your data is never shared.")
        
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem; color: #64748b; font-size: 0.9rem;'>
            <p>Powered by LangChain, LangGraph & Neo4j</p>
            <p>🏆 Part of the Snaphomz Ecosystem</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()  # Don't show the rest of the app until logged in

# Initialize Session Manager WITH user_id (after login)
session_manager = SessionManager(user_id=st.session_state.user_id)

# Initialize session state (if not already present)
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: Session History ---
with st.sidebar:
    # User profile section with premium styling
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.15); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; backdrop-filter: blur(10px);'>
        <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
            <div style='background: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-right: 1rem;'>
                👤
            </div>
            <div>
                <p style='margin: 0; font-size: 0.85rem; opacity: 0.8;'>Logged in as</p>
                <p style='margin: 0; font-weight: 600; font-size: 1.1rem;'>{st.session_state.user_id}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Chat History Section
    st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <h3 style='font-size: 1.3rem; margin-bottom: 0.5rem; display: flex; align-items: center;'>
            💬 Chat History
        </h3>
        <p style='font-size: 0.85rem; opacity: 0.8; margin: 0;'>Your conversation sessions</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_session_id = session_manager.create_session()
        st.session_state.messages = []
        st.session_state.agent = AgentWrapper(session_id=st.session_state.current_session_id, user_id=st.session_state.user_id)
        st.rerun()

    st.markdown("---")
    
    # List previous sessions
    sessions = session_manager.list_sessions()
    
    # If no session active, default to the most recent or create new
    if "current_session_id" not in st.session_state:
        if sessions:
            st.session_state.current_session_id = sessions[0]["id"]
        else:
            st.session_state.current_session_id = session_manager.create_session()
            
    # Session Selector
    for sess in sessions:
        title = sess.get("title", "New Chat") or "New Chat"
        created = sess.get("createdAt")
        label = f"{title} ({str(created).split('T')[0]})"
        
        if st.button(label, key=sess["id"], use_container_width=True):
            st.session_state.current_session_id = sess["id"]
            # Reload agent with selected session
            st.session_state.agent = AgentWrapper(session_id=sess["id"], user_id=st.session_state.user_id)
            # Load messages for UI
            history = st.session_state.agent.get_history()
            st.session_state.messages = history
            st.rerun()

# --- MAIN CHAT ---

# Initialize Agent if not present (on first load)
if "agent" not in st.session_state:
    st.session_state.agent = AgentWrapper(session_id=st.session_state.current_session_id, user_id=st.session_state.user_id)
    # Sync UI messages with agent history
    st.session_state.messages = st.session_state.agent.get_history()

if "comparison_list" not in st.session_state:
    st.session_state.comparison_list = []

if "comparison_list" not in st.session_state:
    st.session_state.comparison_list = []

# Title with professional branding
st.title("🏠 Snaphomz AI Search")
st.markdown("<p class='subtitle'>🤖 Intelligent Property Search | 💰 Financial Analysis | 📊 Market Insights</p>", unsafe_allow_html=True)

# Trust indicators
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🔒 Secure", "100%")
with col2:
    st.metric("⚡ Real-Time", "Live Data")
with col3:
    st.metric("🎯 Accurate", "AI-Powered")
with col4:
    st.metric("🌎 Coverage", "US-Wide")

st.markdown("---")

# Sidebar
with st.sidebar:
    # Features Section with premium cards
    st.markdown("---")
    st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <h3 style='font-size: 1.3rem; margin-bottom: 0.5rem;'>✨ Capabilities</h3>
        <p style='font-size: 0.85rem; opacity: 0.8; margin: 0;'>What I can help you with</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    features = [
        ("💬", "Natural Language", "Ask in plain English"),
        ("💰", "Mortgage Calculator", "Financial analysis"),
        ("📊", "Price Comparison", "Multi-tier analysis"),
        ("🏘️", "Smart Search", "AI-powered matching"),
        ("🔄", "Property Compare", "Side-by-side view"),
        ("💾", "Memory", "Context retention")
    ]
    
    for icon, title, desc in features:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; backdrop-filter: blur(5px);'>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 1.5rem; margin-right: 0.75rem;'>{icon}</span>
                <div>
                    <p style='margin: 0; font-weight: 600; font-size: 0.95rem;'>{title}</p>
                    <p style='margin: 0; font-size: 0.8rem; opacity: 0.8;'>{desc}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Memory status with premium design
    st.markdown("---")
    st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <h3 style='font-size: 1.3rem; margin-bottom: 0.5rem;'>💾 Session Status</h3>
        <p style='font-size: 0.85rem; opacity: 0.8; margin: 0;'>Current conversation state</p>
    </div>
    """, unsafe_allow_html=True)
    
    memory_summary = st.session_state.agent.get_memory_summary()
    
    # Memory card
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 10px; backdrop-filter: blur(10px);'>
        <p style='margin: 0; font-size: 0.9rem; opacity: 0.9;'>{memory_summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    if st.session_state.agent.previous_results:
        num_props = len(st.session_state.agent.previous_results)
        st.markdown(f"""
        <div style='background: rgba(34, 197, 94, 0.2); padding: 0.75rem; border-radius: 8px; border-left: 4px solid #22c55e; backdrop-filter: blur(5px);'>
            <p style='margin: 0; font-weight: 600; font-size: 0.95rem;'>📊 {num_props} Properties Loaded</p>
            <p style='margin: 0; font-size: 0.8rem; opacity: 0.9;'>Ready for comparison</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: rgba(251, 191, 36, 0.2); padding: 0.75rem; border-radius: 8px; border-left: 4px solid #fbbf24; backdrop-filter: blur(5px);'>
            <p style='margin: 0; font-weight: 600; font-size: 0.95rem;'>⚠️ No Properties</p>
            <p style='margin: 0; font-size: 0.8rem; opacity: 0.9;'>Start a search to load data</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Comparison
    if st.session_state.comparison_list:
        st.markdown("---")
        st.markdown("""
        <div style='margin-bottom: 0.75rem;'>
            <h3 style='font-size: 1.2rem; margin-bottom: 0.25rem;'>🔄 Comparison</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: rgba(59, 130, 246, 0.2); padding: 0.75rem; border-radius: 8px; border-left: 4px solid #3b82f6; backdrop-filter: blur(5px); margin-bottom: 0.75rem;'>
            <p style='margin: 0; font-weight: 600;'>{len(st.session_state.comparison_list)} properties selected</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👁️ View Comparison", use_container_width=True):
            st.session_state.show_comparison = True
        if st.button("🗑️ Clear Selection", use_container_width=True):
            st.session_state.comparison_list = []
            st.rerun()
    
    # Clear conversation with premium styling
    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.agent.clear_history()
        st.session_state.comparison_list = []
        st.rerun()
    
    # Placeholder for future ecosystem integrations
    st.markdown("---")
    st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <h3 style='font-size: 1.2rem; margin-bottom: 0.5rem;'>🌐 Snaphomz Ecosystem</h3>
        <p style='font-size: 0.85rem; opacity: 0.8; margin: 0;'>Coming Soon</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ecosystem placeholder cards
    ecosystem_tools = [
        ("📋", "Pre-Approval", "Loan qualification"),
        ("🎓", "SnapGrad", "Risk assessment"),
        ("💰", "SnapInterest", "Rate comparison"),
        ("📄", "SnapDisclosure", "Document analysis"),
        ("✅", "SnapAudit", "Compliance check"),
        ("🏠", "Rent vs Buy", "Decision calculator")
    ]
    
    for icon, name, desc in ecosystem_tools:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.05); padding: 0.6rem; border-radius: 6px; margin-bottom: 0.4rem; opacity: 0.6; cursor: not-allowed;'>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 1.2rem; margin-right: 0.6rem;'>{icon}</span>
                <div>
                    <p style='margin: 0; font-weight: 600; font-size: 0.85rem;'>{name}</p>
                    <p style='margin: 0; font-size: 0.75rem; opacity: 0.8;'>{desc}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Professional footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center;'>
        <p style='font-size: 0.9rem; margin-bottom: 0.5rem;'>🔒 <strong>Secure & Private</strong></p>
        <p style='font-size: 0.85rem; color: rgba(255,255,255,0.8);'>Powered by LangChain, LangGraph & Neo4j</p>
        <p style='font-size: 0.8rem; color: rgba(255,255,255,0.6);'>© 2026 Snaphomz</p>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about properties..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.chat(prompt)
        
        # Add comparison suggestion only if there are 2+ results AND response doesn't indicate failure
        if st.session_state.agent.previous_results and "couldn't find any properties" not in response.lower():
            num_results = len(st.session_state.agent.previous_results)
            
            # Only suggest comparison if there are at least 2 properties
            if num_results >= 2:
                if num_results == 2:
                    response += "\n\n💡 **Would you like to compare these two properties?** Just say 'compare property 1 and 2' or 'compare them'."
                elif num_results <= 5:
                    response += f"\n\n💡 **Would you like to compare any of these {num_results} properties?** For example:\n- 'Compare property 1 and 2'\n- 'Compare the first three'\n- 'Show me comparison of #1 and #{num_results}'"
                else:
                    response += f"\n\n💡 **Found {num_results} properties! Would you like to compare any?** For example:\n- 'Compare property 1 and 3'\n- 'Compare the first two'\n- 'Show me comparison of #2 and #5'"
        
        st.markdown(response)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()

# Show comparison modal at bottom if triggered
if st.session_state.get("show_comparison") and st.session_state.comparison_list:
    st.markdown("---")
    st.subheader("🔄 Property Comparison")
    
    comparison_data = compare_properties(st.session_state.comparison_list)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Price", f"${comparison_data['avg_price']:,.0f}")
    with col2:
        st.metric("Price Range", f"${comparison_data['price_range']['min']:,} - ${comparison_data['price_range']['max']:,}")
    
    # Show properties side by side
    cols = st.columns(len(st.session_state.comparison_list))
    for i, prop in enumerate(st.session_state.comparison_list):
        with cols[i]:
            st.markdown(f"### Property {i+1}")
            st.metric("Price", f"${prop.get('price', 0):,}")
            st.write(f"**State:** {prop.get('state', 'N/A')}")
            st.caption(prop.get('details', '')[:150])
    
    if st.button("Close Comparison"):
        st.session_state.show_comparison = False
        st.rerun()

