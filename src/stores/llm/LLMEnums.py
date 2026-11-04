from enum import Enum

class LLMEnums(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    AI21 = "ai21"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"

class OpenAIEnums(Enum):
    SYSTEM= "system"
    USER= "user"
    ASSISTANT= "assistant"
    
class CoHereEnums(Enum):
    SYSTEM= "SYSTEM"
    USER= "USER"
    ASSISTANT= "CHATBOT"

    DOCUMENT= "search_document"
    QUERY= "search_query"

class DocumentTypeEnums(Enum):
    DOCUMENT= "document"
    QUERY= "query"
    