# pydantic models below...
from pydantic import BaseModel, Field
from typing import List

class SearchItem(BaseModel):
    query: str = Field(description="The web search query to run.")
    reason: str = Field(description="Why this search is important to the overall query.")

class SearchPlan(BaseModel):
    searches: List[SearchItem]

class Report(BaseModel):
    title: str
    key_insights: List[str]
    analysis: str
    risks: List[str]
    conclusion: str