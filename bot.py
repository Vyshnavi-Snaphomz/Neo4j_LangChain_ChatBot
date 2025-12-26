import streamlit as st
from utils import write_message
# tag::import_agent[]
from agent import generate_response
# end::import_agent[]
from graph import get_graph

# tag::setup[]
# Page Config
st.set_page_config("Real Estate Assistant", page_icon=":house:")
# end::setup[]

# tag::db_status[]
# Print Neo4j connectivity status to the terminal once per session (Streamlit reruns on every interaction).
if "neo4j_connectivity_checked" not in st.session_state:
    try:
        get_graph()
        st.session_state.neo4j_connectivity_checked = True
        st.session_state.neo4j_connectivity_ok = True
        print("Neo4j connectivity: OK")
    except Exception as exc:
        st.session_state.neo4j_connectivity_checked = True
        st.session_state.neo4j_connectivity_ok = False
        st.session_state.neo4j_connectivity_error = str(exc)
        print(f"Neo4j connectivity: FAILED - {exc}")

# Optional UI indicator (doesn't block the app)
with st.sidebar:
    if st.session_state.get("neo4j_connectivity_ok"):
        st.success("Neo4j connected")
    elif st.session_state.get("neo4j_connectivity_checked"):
        st.error("Neo4j connection failed")
        err = st.session_state.get("neo4j_connectivity_error")
        if err:
            st.caption(err)
# end::db_status[]

# tag::session[]
# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your real estate assistant. What would you like to know about the properties in your database?"},
    ]
# end::session[]

# tag::submit[]
# Submit handler
def handle_submit(message):
    """
    Submit handler:

    You will modify this method to talk with an LLM and provide
    context using data from Neo4j.
    """

    # Handle the response
    with st.spinner('Thinking...'):
        # Call the agent
        response = generate_response(message)
        write_message('assistant', response)
        
# end::submit[]


# tag::chat[]
# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if prompt := st.chat_input("Ask about listings, neighborhoods, prices, amenities…"):
    # Display user message in chat message container
    write_message('user', prompt)

    # Generate a response
    handle_submit(prompt)
# end::chat[]
