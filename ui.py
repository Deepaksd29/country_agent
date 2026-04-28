import streamlit as st
from app.agent.graph import build_graph
from app.utils.logger import get_logger
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

st.title("🌍 Country Information AI Agent")
st.write("Ask me about the capital, population, currency, or other facts about any country!")

# Initialize graph
if "graph" not in st.session_state:
    logger.info("Building Streamlit graph")
    st.session_state.graph = build_graph()

user_query = st.text_input("Enter your question:", placeholder="What is the capital and population of Brazil?")

if st.button("Submit") and user_query:
 
    with st.spinner("Analyzing request and fetching data..."):
        initial_state = {"query": user_query}
        logger.info("Streamlit query submitted", extra={"query": user_query})

        try:
            result = st.session_state.graph.invoke(initial_state)
            logger.info(
                "Streamlit query completed",
                extra={
                    "query": user_query,
                    "country": result.get("country"),
                    "fields": result.get("fields"),
                    "has_error": bool(result.get("error")),
                },
            )

            st.markdown("### Answer")
            st.write(result["final_answer"])
        except Exception:
            logger.exception("Streamlit query failed", extra={"query": user_query})
            st.error("Sorry, something went wrong while processing your request.")
        
    
