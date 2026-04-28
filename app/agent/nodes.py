from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
import json
from app.tools.apicalls import fetch_country_data
from app.utils.setting import settings
from app.utils.logger import get_logger
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.schema.state import AgentState

logger = get_logger(__name__)

llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    temperature=settings.MODEL_TEMPERATURE,
    max_retries=settings.MODEL_MAX_RETRIES,
    google_api_key=settings.GEMMINE_API_KEY,
)

class IntentExtraction(BaseModel):
    is_general_chat: bool = Field(description="True if the user is just saying hi or making small talk. False if they are asking about a country.")
    is_supported_country_query: bool = Field(description="True if the user is asking specifically about country facts (population, capital, area, etc.).")
    direct_reply: str = Field(description="If is_general_chat is True, write a polite greeting here. Otherwise, leave blank.")
    rejection_message: str = Field(description="If is_supported_country_query is False, explain briefly why the request is not supported. Otherwise, leave blank.")
    country: str = Field(description="The country name, if provided.")
    fields: list[str] = Field(description="The specific information requested.")
    
def extract_intent(state):
    query = state["query"]
    logger.info("Intent extraction started", extra={"query": query})

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a specialized Country Information Agent. 
         Your ONLY job is to answer questions about sovereign nations using factual data.
         
         REJECT queries that are:
         1. Opinion-based (e.g., "Which country is the best?")
         2. Unrelated to country facts (e.g., "How do I bake a cake?", "What is the weather?")
         3. Political or sensitive debates.
         
         If the user is only greeting you or making small talk, set 'is_general_chat' to True and provide a short 'direct_reply'.
         If the query is outside these bounds, set 'is_supported_country_query' to False and provide a 'rejection_message'."""),
        ("human", "{query}")
    ])
    
    structured_llm = llm.with_structured_output(IntentExtraction)
    chain = prompt | structured_llm
    
    try:
        result = chain.invoke({"query": query})
        final_answer = None

        if result.is_general_chat:
            final_answer = result.direct_reply
        elif not result.is_supported_country_query:
            final_answer = result.rejection_message

        logger.info(
            "Intent extraction completed",
            extra={
                "is_general_chat": result.is_general_chat,
                "is_supported": result.is_supported_country_query,
                "country": result.country,
                "fields": result.fields,
            },
        )
        
        return {
            "is_general_chat": result.is_general_chat,
            "is_supported": result.is_supported_country_query,
            "final_answer": final_answer,
            "country": result.country if not result.is_general_chat else None,
            "fields": result.fields if not result.is_general_chat else []
        }
    except Exception as e:
        logger.exception("Intent extraction failed", extra={"query": query})
        return {"error": f"Failed to understand the request: {str(e)}"}
        
        

def invoke_tool(state: AgentState) -> dict:
    """Node 2: Fetches data from the REST Countries API."""
    if state.get("error") or not state.get("country"):
        logger.info(
            "Skipping country API call",
            extra={"has_error": bool(state.get("error")), "country": state.get("country")},
        )
        return {}

    logger.info("Country API call started", extra={"country": state["country"]})
    api_response = fetch_country_data(state["country"])
    
    if "error" in api_response:
        logger.warning(
            "Country API call returned error",
            extra={"country": state["country"], "error": api_response["error"]},
        )
        return {"error": api_response["error"], "api_data": None}

    logger.info("Country API call completed", extra={"country": state["country"]})
    return {"api_data": api_response["data"], "error": None}


def synthesize_answer(state: AgentState) -> dict:
    """Node 3: Generates the final natural language response."""
    query = state["query"]
    error = state.get("error")
    api_data = state.get("api_data")

    logger.info(
        "Answer synthesis started",
        extra={
            "country": state.get("country"),
            "fields": state.get("fields"),
            "has_error": bool(error),
            "has_api_data": bool(api_data),
        },
    )
    
    if error:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. The user asked a question, but we encountered an issue: {error}. Politely explain the issue to the user."),
            ("human", "{query}")
        ])
        chain = prompt | llm
        response = chain.invoke({"error": error, "query": query})
        logger.info("Answer synthesis completed for error response", extra={"country": state.get("country")})
        return {"final_answer": response.content}
        
    if not api_data:
        logger.info("Answer synthesis completed without API data", extra={"country": state.get("country")})
        return {"final_answer": """I couldn't identify a specific country in your request. 
                Please ask about a specific country's population, capital, or currency."""}

    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a factual AI assistant. 
         Answer the user's query using ONLY the provided JSON data from the REST Countries API. 
         If the data to answer the user's query is missing from the JSON, state that you do not have that specific information. 
         Keep answers concise, accurate, and conversational.\n\nAPI Data:\n{api_data}"""),
        ("human", "{query}")
    ])
    
    chain = prompt | llm
    data_str = json.dumps(api_data, indent=2)
    response = chain.invoke({"api_data": data_str, "query": query})
    content = response.content
    
    if isinstance(content, list) and len(content) > 0:
        final_text = content[0].get("text", "")
    else:
        final_text = str(content)

    logger.info("Answer synthesis completed", extra={"country": state.get("country")})
    return {"final_answer": final_text}
