import streamlit as st
from llm import llm, embeddings
from graph import get_graph
from langchain_neo4j import Neo4jVector
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

def _secret(key: str, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return default


def _vector_config():
    """
    Vector index configuration.

    For a real-estate dataset, set these in `.streamlit/secrets.toml`:
    - `NEO4J_VECTOR_INDEX_NAME`
    - `NEO4J_VECTOR_NODE_LABEL`
    - `NEO4J_VECTOR_TEXT_PROPERTY`
    - `NEO4J_VECTOR_EMBEDDING_PROPERTY`
    - (optional) `NEO4J_VECTOR_RETRIEVAL_QUERY`

    Defaults keep the original course/movie setup working.
    """
    return {
        "index_name": _secret("NEO4J_VECTOR_INDEX_NAME", "moviePlots"),
        "node_label": _secret("NEO4J_VECTOR_NODE_LABEL", "Movie"),
        "text_node_property": _secret("NEO4J_VECTOR_TEXT_PROPERTY", "plot"),
        "embedding_node_property": _secret("NEO4J_VECTOR_EMBEDDING_PROPERTY", "plotEmbedding"),
        "retrieval_query": _secret("NEO4J_VECTOR_RETRIEVAL_QUERY", None),
    }


_plot_retriever = None


def _get_retriever_chain():
    global _plot_retriever
    if _plot_retriever is not None:
        return _plot_retriever

    cfg = _vector_config()
    neo4jvector = Neo4jVector.from_existing_index(
        embeddings,
        graph=get_graph(),
        index_name=cfg["index_name"],
        node_label=cfg["node_label"],
        text_node_property=cfg["text_node_property"],
        embedding_node_property=cfg["embedding_node_property"],
        retrieval_query=cfg["retrieval_query"],
    )

    retriever = neo4jvector.as_retriever()

    instructions = (
        "Use the given context to answer the question.\n"
        "If the answer isn't in the context, say you don't know.\n"
        "Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", instructions),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    _plot_retriever = create_retrieval_chain(
        retriever,
        question_answer_chain,
    )
    return _plot_retriever

def _format_sources(docs, max_docs: int = 3) -> str:
    if not docs:
        return ""

    lines = ["", "Top matches:"]
    for doc in docs[:max_docs]:
        meta = getattr(doc, "metadata", {}) or {}
        preferred_keys = [
            "listingId",
            "listing_id",
            "mls",
            "address",
            "city",
            "state",
            "zip",
            "price",
            "beds",
            "baths",
            "sqft",
            "url",
            "source",
            "title",
            "name",
        ]
        compact = {k: meta[k] for k in preferred_keys if k in meta}
        lines.append(f"- {compact if compact else meta}")
    return "\n".join(lines)


def semantic_search(input: str) -> str:
    """
    Semantic search over your Neo4j vector index (configured via Streamlit secrets).

    Returns an answer grounded in retrieved nodes/documents plus a short "Top matches"
    section when metadata is available.
    """
    try:
        chain = _get_retriever_chain()
    except Exception as exc:
        cfg = _vector_config()
        return (
            "Semantic search isn't configured or the Neo4j vector index couldn't be loaded. "
            "Set `NEO4J_VECTOR_INDEX_NAME`, `NEO4J_VECTOR_NODE_LABEL`, `NEO4J_VECTOR_TEXT_PROPERTY`, "
            "and `NEO4J_VECTOR_EMBEDDING_PROPERTY` in `.streamlit/secrets.toml` to match your graph.\n\n"
            f"Current config: index={cfg['index_name']}, label={cfg['node_label']}, textProp={cfg['text_node_property']}, embeddingProp={cfg['embedding_node_property']}\n"
            f"Error: {exc}"
        )

    result = chain.invoke({"input": input})

    answer = (result.get("answer") or result.get("result") or "").strip()
    docs = result.get("context") or []

    if not docs:
        return (
            "I couldn't find any semantic matches in the configured vector index.\n\n"
            "If you're trying to search listings/schools/colleges, use the structured search tools instead, "
            "or create embeddings + a vector index for those nodes."
        )

    if not answer or answer.lower() in {"i don't know", "i don't know."}:
        return f"I couldn't answer from the retrieved context.{_format_sources(docs)}"

    return f"{answer}{_format_sources(docs)}"


# Backwards-compatible alias (the course names this "movie plot search").
def get_movie_plot(input: str) -> str:
    return semantic_search(input)
