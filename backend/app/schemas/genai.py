from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User input prompt")
    system_prompt: str | None = Field(default=None, description="Optional system prompt")
    temperature: float = Field(default=0.7, ge=0.0, le=1.5)
    max_tokens: int = Field(default=256, ge=1, le=4096)


class ChatResponse(BaseModel):
    text: str
    provider: str


GenerateRequest = ChatRequest
GenerateResponse = ChatResponse
