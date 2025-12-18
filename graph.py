import streamlit as st

# tag::graph[]
from langchain_neo4j import Neo4jGraph

_graph = None


def _build_driver_config(url: str):
    """
    Build neo4j driver config from Streamlit secrets.

    Supported optional secrets:
    - `NEO4J_DRIVER_TRUST`: `SYSTEM` or `ALL` (only for `neo4j://` or `bolt://` URIs)
    - `NEO4J_DRIVER_MAX_CONNECTION_LIFETIME`: float seconds
    - `NEO4J_DRIVER_CONNECTION_TIMEOUT`: float seconds
    """
    try:
        import neo4j
    except Exception:
        return None

    driver_config = {}

    scheme = (url.split("://", 1)[0] if "://" in url else "").lower()
    # Neo4j driver forbids setting custom trust/encryption options when using `neo4j+s://` / `neo4j+ssc://`
    # because those schemes already encode the encryption behavior.
    allow_trust_settings = scheme in {"neo4j", "bolt"}

    trust = None
    try:
        trust = str(st.secrets["NEO4J_DRIVER_TRUST"]).strip().upper()
    except Exception:
        trust = None

    if allow_trust_settings:
        if trust == "ALL":
            driver_config["trusted_certificates"] = neo4j.TrustAll()
        elif trust == "SYSTEM":
            driver_config["trusted_certificates"] = neo4j.TrustSystemCAs()

    for key, dest in [
        ("NEO4J_DRIVER_MAX_CONNECTION_LIFETIME", "max_connection_lifetime"),
        ("NEO4J_DRIVER_CONNECTION_TIMEOUT", "connection_timeout"),
    ]:
        try:
            driver_config[dest] = float(st.secrets[key])
        except Exception:
            pass

    return driver_config or None


def get_graph() -> Neo4jGraph:
    """
    Lazily create and cache a Neo4jGraph connection.

    This avoids making a network connection at import time, which makes the app
    easier to run and debug when Neo4j is temporarily unavailable.
    """
    global _graph
    if _graph is not None:
        return _graph

    try:
        try:
            database = st.secrets["NEO4J_DATABASE"]
        except Exception:
            database = "neo4j"

        url = st.secrets["NEO4J_URI"]
        # Optional override to bypass routing (useful for Aura environments where
        # `neo4j+s://` routing discovery is blocked by local network/proxy settings).
        # Example: `bolt+s://p-<instance>-<region>.neo4j.io:7687`
        try:
            direct_url = st.secrets["NEO4J_DIRECT_URI"]
        except Exception:
            direct_url = None
        if direct_url:
            url = direct_url
        driver_config = _build_driver_config(url)

        # Pre-flight connectivity check so we can surface the real exception (e.g. TLS/Auth/Firewall)
        # instead of `Neo4jGraph` converting it into a generic ValueError.
        try:
            import neo4j

            username = st.secrets["NEO4J_USERNAME"]
            password = st.secrets["NEO4J_PASSWORD"]

            _driver = neo4j.GraphDatabase.driver(
                url, auth=(username, password), **(driver_config or {})
            )
            _driver.verify_connectivity()
            _driver.close()
        except Exception as connectivity_exc:
            raise connectivity_exc

        _graph = Neo4jGraph(
            url=url,
            username=st.secrets["NEO4J_USERNAME"],
            password=st.secrets["NEO4J_PASSWORD"],
            database=database,
            driver_config=driver_config,
        )
    except Exception as exc:
        raise ValueError(
            "Could not connect to Neo4j. Check `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE` "
            f"in `.streamlit/secrets.toml`. Underlying error: {type(exc).__name__}: {exc}"
        ) from exc

    return _graph
#end::graph[]
