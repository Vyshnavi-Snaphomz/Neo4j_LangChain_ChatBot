from llm import llm
from graph import get_graph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain_neo4j import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from utils import get_session_id

from tools.vector import semantic_search
from tools.cypher import cypher_qa_tool
from tools.listings import search_listings, search_schools, search_colleges

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful real estate assistant."),
        ("human", "{input}"),
    ]
)

general_chat = chat_prompt | llm | StrOutputParser()

tools = [
    Tool.from_function(
        name="General Chat",
        description="General real estate chat and guidance not requiring database lookup",
        func=general_chat.invoke,
    ),
    Tool(
        name="Listings Search",
        description="Filter and list properties/homes from the `Listing` dataset (state/zip/price/beds/baths). Use for queries like 'homes in California' or 'listings in 90001'.",
        func=search_listings,
        return_direct=True,
    ),
    Tool(
        name="Schools Search",
        description="Find schools by state or zip code from the `School` dataset. Use for queries like 'schools in TX' or 'schools near 94016'.",
        func=search_schools,
        return_direct=True,
    ),
    Tool(
        name="Colleges Search",
        description="Find colleges by state or zip code from the `College` dataset. Use for queries like 'colleges in CA' or 'colleges near 92037'.",
        func=search_colleges,
        return_direct=True,
    ),
    Tool(
        name="Document Semantic Search",
        description="Semantic search over embedded nodes (requires a Neo4j vector index + embeddings). Use when keyword/state filters aren't enough.",
        func=semantic_search,
        return_direct=True,
    ),
    Tool(
        name="Property Information (Cypher)",
        description="Answer questions using Cypher against the Neo4j real estate graph",
        func=cypher_qa_tool,
        return_direct=True,
    ),
]

_fallback_histories = {}


def get_memory(session_id):
    try:
        return Neo4jChatMessageHistory(session_id=session_id, graph=get_graph())
    except Exception:
        history = _fallback_histories.get(session_id)
        if history is None:
            history = InMemoryChatMessageHistory()
            _fallback_histories[session_id] = history
        return history

agent_prompt = PromptTemplate.from_template("""
You are a real estate assistant for a Neo4j-backed knowledge base.
Be as helpful as possible and return as much relevant information as possible.
If the user asks for specific facts about listings/properties/locations/agents in the database, use a tool.

For general real-estate process questions (e.g., definitions, how-to guidance), you may answer without tools.
For database-backed questions, do not guess: use tools and ground answers in their output.
If a tool returns that it can't find the answer or can't access the database, stop and explain that limitation in your final answer. Do not repeatedly call the same tool with the same input.
Prefer `Listings Search` / `Schools Search` / `Colleges Search` for structured lookup by location, then use `Property Information (Cypher)` for more complex graph questions, and `Document Semantic Search` only if embeddings are configured for the target data.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=6,
    handle_parsing_errors=True,
    )

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """

    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}},)

    return response['output']
