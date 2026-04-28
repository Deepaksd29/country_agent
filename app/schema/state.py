from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    query: str
    country: Optional[str]
    fields: Optional[List[str]]
    api_data: Optional[Dict[str, Any]]
    error: Optional[str]
    final_answer: Optional[str]
    is_general_chat: bool
    is_supported: bool