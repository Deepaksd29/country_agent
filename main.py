from fastapi import FastAPI
from app.agent.graph import build_graph
from app.utils.logger import get_logger

app = FastAPI()
graph = build_graph()
logger = get_logger(__name__)

@app.get("/ask")
def ask(query: str):
    logger.info("API request received", extra={"query": query})

    try:
        result = graph.invoke({"query": query})
    except Exception:
        logger.exception("API request failed", extra={"query": query})
        return {"error": "Failed to process the request."}

    if result.get("error"):
        logger.warning("API request completed with error", extra={"query": query, "error": result["error"]})
        return {"error": result["error"]}

    logger.info("API request completed", extra={"query": query})
    return {"answer": result["final_answer"]}
