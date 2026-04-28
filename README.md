# Country Information AI Agent

An AI agent that answers factual questions about countries using the public REST Countries API and a LangGraph workflow.

Example questions:

- What is the population of Germany?
- What currency does Japan use?
- What is the capital and population of Brazil?

## Architecture

The agent is built as a small production-style service with clear stages:

1. Intent and field identification: determines whether the user is asking a supported country-facts question, extracts the country, and identifies requested fields.
2. Tool invocation: calls `https://restcountries.com/v3.1/name/{country}` to fetch grounded country data.
3. Answer synthesis: generates a concise answer using only the REST Countries API response.

The graph is defined in `app/agent/graph.py`, and the node implementations live in `app/agent/nodes.py`.

## Tech Stack

- Python 3.12+
- LangGraph
- LangChain
- Gemini via `langchain-google-genai`
- FastAPI
- Streamlit
- REST Countries API

## Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file:

```bash
GEMINI_API_KEY=your_api_key_here
```

## Run the Streamlit App

```bash
uv run streamlit run ui.py
```

Open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Run the FastAPI Service

```bash
uv run uvicorn main:app --reload
```

Test the API:

```bash
curl "http://127.0.0.1:8000/ask?query=What%20is%20the%20capital%20of%20Japan?"
```

The response format is:

```json
{
  "answer": "The capital of Japan is Tokyo."
}
```

## Deployment Notes

For a hosted demo, deploy either:

- Streamlit app: use Streamlit Community Cloud and set `GEMINI_API_KEY` in app secrets.
- FastAPI service: use Render, Railway, Fly.io, or a similar platform and set `GEMINI_API_KEY` as an environment variable.

Suggested production command for FastAPI:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Behavior

Supported:

- Country population
- Capital
- Currency
- Region/subregion
- Area
- Languages
- Other factual fields available in the REST Countries API response

Graceful handling:

- Invalid country names return a clear error.
- Unsupported questions are rejected with a short explanation.
- Greetings receive a short direct response.
- Missing API data is acknowledged instead of invented.

## Known Limitations

- The system depends on the REST Countries API being available.
- Country name matching uses the REST Countries `/name/{country}` endpoint, so ambiguous names may return the first matching result.
- The answer synthesis step uses an LLM, so prompts are constrained to use only API data for grounding.
- No authentication, database, embeddings, or RAG are used, as required by the assignment.
