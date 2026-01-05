from langgraph.graph import StateGraph, END
from app.state import AgentState

# Import nodes
from app.nodes.intent import intent_classifier
from app.nodes.extractor import entity_extractor
from app.nodes.planner import query_planner
from app.nodes.generator import cypher_generator
from app.nodes.search import neo4j_search
from app.nodes.rerank import vector_rerank
from app.nodes.guardrails import policy_guardrails
from app.nodes.softener import response_softener
from app.nodes.final_response import final_response
from app.nodes.reference import reference_handler
from app.nodes.comparison import comparison_handler
from app.nodes.census_data import census_data_enrichment
from app.nodes.financial_analysis import financial_analysis_handler

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("Intent_Classifier", intent_classifier)
workflow.add_node("Reference_Handler", reference_handler)
workflow.add_node("Comparison_Handler", comparison_handler)
workflow.add_node("Financial_Analysis_Handler", financial_analysis_handler)
workflow.add_node("Entity_Extractor", entity_extractor)
workflow.add_node("Query_Planner", query_planner)
workflow.add_node("Cypher_Generator", cypher_generator)
workflow.add_node("Neo4j_Search", neo4j_search)
workflow.add_node("Census_Data_Enrichment", census_data_enrichment)
workflow.add_node("Vector_ReRank", vector_rerank)
workflow.add_node("Policy_and_Guardrails", policy_guardrails)
workflow.add_node("Response_Softener", response_softener)
workflow.add_node("Final_Response", final_response)

# Set entry point
workflow.set_entry_point("Intent_Classifier")

# Conditional routing based on intent
def route_after_intent(state):
    intent = state.get("intent", "search")
    if intent == "reference":
        return "Reference_Handler"
    elif intent == "comparison":
        return "Comparison_Handler"
    elif intent == "financial_analysis":
        return "Financial_Analysis_Handler"
    else:
        return "Entity_Extractor"

workflow.add_conditional_edges(
    "Intent_Classifier",
    route_after_intent,
    {
        "Reference_Handler": "Reference_Handler",
        "Comparison_Handler": "Comparison_Handler",
        "Financial_Analysis_Handler": "Financial_Analysis_Handler",
        "Entity_Extractor": "Entity_Extractor"
    }
)

# Reference, comparison, and financial analysis handlers go directly to final response
workflow.add_edge("Reference_Handler", "Final_Response")
workflow.add_edge("Comparison_Handler", "Final_Response")
workflow.add_edge("Financial_Analysis_Handler", "Final_Response")

# Normal search flow with Census Data enrichment
workflow.add_edge("Entity_Extractor", "Query_Planner")
workflow.add_edge("Query_Planner", "Cypher_Generator")
workflow.add_edge("Cypher_Generator", "Neo4j_Search")
workflow.add_edge("Neo4j_Search", "Census_Data_Enrichment")  # Add Census enrichment after search
workflow.add_edge("Census_Data_Enrichment", "Vector_ReRank")
workflow.add_edge("Vector_ReRank", "Policy_and_Guardrails")
workflow.add_edge("Policy_and_Guardrails", "Response_Softener")
workflow.add_edge("Response_Softener", "Final_Response")
workflow.add_edge("Final_Response", END)

graph = workflow.compile()

