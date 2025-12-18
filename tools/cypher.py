from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

from llm import llm
from graph import get_graph

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about real estate data (properties/listings, locations, agents, transactions, amenities, etc.).
Convert the user's question based on the schema and return a Cypher query that answers it.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Prefer read-only queries. Do not use `CREATE`, `MERGE`, `SET`, `DELETE`, `DROP`, or `LOAD CSV`.
Do not return entire nodes. Return only the specific properties needed to answer the question.
Do not return embedding/vector properties.
If returning lists of entities, include a `LIMIT` (default to 20) unless the user asks otherwise.

Schema:
{schema}

Question:
{question}
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

_cypher_qa = None


def _get_cypher_qa():
    global _cypher_qa
    if _cypher_qa is not None:
        return _cypher_qa

    _cypher_qa = GraphCypherQAChain.from_llm(
        llm,
        graph=get_graph(),
        verbose=True,
        cypher_prompt=cypher_prompt,
        allow_dangerous_requests=False,
    )
    return _cypher_qa


def cypher_qa_tool(input: str) -> str:
    """
    Tool wrapper for the agent.

    GraphCypherQAChain expects a natural language question and returns a natural
    language answer grounded in Neo4j query results.
    """
    try:
        return _get_cypher_qa().run(input)
    except Exception as exc:
        return (
            "I couldn't query Neo4j right now. Verify your Neo4j connection settings in `.streamlit/secrets.toml` "
            "and that the database is reachable.\n\n"
            f"Error: {exc}"
        )
