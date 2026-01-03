# 🏡 Real Estate AI Agent

An advanced, graph-native AI assistant designed to help users find their dream homes using natural language. Built with **LangGraph**, **Neo4j**, and **OpenAI**, this agent understands complex queries, filters by rich property criteria, and provides detailed, context-aware responses.

## ✨ Features

- **Natural Language Search**: Ask for "luxury homes in Texas", "affordable apartments in New York", or "hill top houses in California".
- **Rich Property Details**: Retrieves full descriptions, specifications (beds, baths, sqft), year built, and direct Zillow URLs.
- **Smart Entity Extraction**:
  - Auto-corrects typos (e.g., "San Fransisco" → "San Francisco").
  - Maps full state names to codes (e.g., "Texas" → "TX").
  - Understands price keywords: "Luxury" (>$1M), "Cheap" (<$400k).
- **Contextual Memory**: Remembers previous results allowing for follow-up questions like "tell me more about the second one".
- **Hybrid Search**: Combines keyword filtering with vector-ready architecture (ready for semantic search).
- **Interactive UI**: Clean, responsive interface built with Streamlit.

## 🛠️ Tech Stack

- **Framework**: LangChain & LangGraph
- **Database**: Neo4j (Graph Database)
- **LLM**: OpenAI GPT-4o-mini
- **Frontend**: Streamlit
- **Language**: Python

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A running Neo4j Database populated with the Zillow dataset.
- An OpenAI API Key.

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Create a `.env` file in the root directory with your credentials:
   ```env
   OPENAI_API_KEY=sk-...
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   NEO4J_DATABASE=neo4j
   ```

### Running the Agent

Start the application using Streamlit:

```bash
streamlit run streamlit_app.py
```

The app will open in your default browser at `http://localhost:8501`.

## 📂 Project Structure

- `app/`: Core application logic (nodes, state, graph definition).
  - `nodes/`: Individual graph nodes for search, extraction, generation, etc.
- `streamlit_app.py`: Main entry point for the frontend.
- `requirements.txt`: Python package dependencies.

## 📝 Usage Examples

Try asking the agent:
- *"Show me luxury houses in Los Vegas"*
- *"Find affordable homes in Texas under 300k"*
- *"Tell me more about property #1"*
- *"Compare the first two houses"* (Coming soon)
