import streamlit as st
from app.agent_wrapper import AgentWrapper
from app.property_utils import compare_properties

# Page configuration
st.set_page_config(
    page_title="Real Estate AI Agent",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .main {
        background-color: #f5f5f5;
    }
    h1 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = AgentWrapper()

if "comparison_list" not in st.session_state:
    st.session_state.comparison_list = []

# Title
st.title("🏠 Real Estate AI Agent")
st.markdown("Ask me about properties across the United States!")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    Advanced real estate search with:
    - 💬 Conversational AI
    - 💾 Session memory
    - 🔄 Property comparison
    - 🏘️ Similar properties
    """)
    
    # Memory status
    st.markdown("---")
    st.subheader("💾 Session Memory")
    memory_summary = st.session_state.agent.get_memory_summary()
    st.info(memory_summary)
    
    if st.session_state.agent.previous_results:
        st.success(f"📊 {len(st.session_state.agent.previous_results)} properties stored")
    else:
        st.warning("No previous results")
    
    # Comparison
    if st.session_state.comparison_list:
        st.markdown("---")
        st.subheader("🔄 Comparison")
        st.info(f"{len(st.session_state.comparison_list)} properties selected")
        if st.button("View Comparison"):
            st.session_state.show_comparison = True
        if st.button("Clear Comparison"):
            st.session_state.comparison_list = []
            st.rerun()
    
    # Clear conversation
    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.agent.clear_history()
        st.session_state.comparison_list = []
        st.rerun()
    
    st.caption("Powered by LangChain, LangGraph & Neo4j")

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
        
        # Add comparison suggestion only if there are 2+ results
        if st.session_state.agent.previous_results:
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

