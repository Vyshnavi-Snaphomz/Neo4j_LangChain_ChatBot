from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

from llm import llm
from graph import get_graph

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about real estate listings.
Convert the user's question based on the schema and return a Cypher query that answers it.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Prefer read-only queries. Do not use `CREATE`, `MERGE`, `SET`, `DELETE`, `DROP`, or `LOAD CSV`.
Do not return entire nodes. Return only the specific properties needed to answer the question.
Do not return embedding/vector properties.
If returning lists of entities, include a `LIMIT` (default to 20) unless the user asks otherwise.

Example Cypher Statements:

1. To find listings in a specific state with a minimum number of bedrooms:
```
MATCH (l:Listing)
WHERE l.state = 'CA' AND l.bedrooms >= 3
RETURN l.streetAddress, l.city, l.state, l.zipcode, l.price, l.bedrooms, l.bathrooms, l.listingUrl
```

2. To find listings in a specific zip code with a maximum price:
```
MATCH (l:Listing)
WHERE l.zipcode = '90210' AND l.price <= 2000000
RETURN l.streetAddress, l.city, l.state, l.zipcode, l.price, l.bedrooms, l.bathrooms, l.listingUrl
```

3. To find listings with a certain number of bathrooms and half-bathrooms:
```
MATCH (l:Listing)
WHERE l.bathrooms = 3.5
RETURN l.streetAddress, l.city, l.state, l.zipcode, l.price, l.bedrooms, l.bathrooms, l.listingUrl
```

Schema:
{schema}

Notes (Listing nodes):
- `Listing` node properties include: `address`, `bathrooms`, `bedrooms`, `city`, `price`, `state`, `streetAddress`, `zipcode`, `listingUrl`, `yearBuilt`, `livingArea`, `homeType`, `lotSize`

Question:
{question}
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

_cypher_qa = None


def _get_cypher_qa():
    global _cypher_qa
    if _cypher_qa is not None:
        return _cypher_qa

    graph = get_graph()
    graph.refresh_schema()
    _cypher_qa = GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        verbose=True,
        cypher_prompt=cypher_prompt,
        allow_dangerous_requests=True,
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
