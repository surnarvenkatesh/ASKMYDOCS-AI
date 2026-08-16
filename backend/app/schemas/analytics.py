"""
Analytics-facing Pydantic schemas.
"""
from pydantic import BaseModel


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int


class DailyQueryCount(BaseModel):
    date: str
    count: int


class AnalyticsSummary(BaseModel):
    documents_count: int
    embeddings_count: int
    total_queries: int
    avg_response_time_ms: float | None
    avg_retrieval_time_ms: float | None
    retrieval_accuracy: float | None
    token_usage: TokenUsage
    estimated_cost_usd: float
    daily_queries: list[DailyQueryCount]
