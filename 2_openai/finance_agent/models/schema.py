from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class AnalysisRequest(BaseModel):
    ticker: str = Field(description="Stock ticker symbol, e.g. NVDA")
    horizon: str = Field(description="Investment horizon, e.g. 6 months or 12 months")
    risk_profile: str = Field(description="Risk tolerance, e.g. conservative, moderate, aggressive")


class AgentMemo(BaseModel): # will be used by all the agents (they each will have different perspectives!)
    agent_name: str = Field(description="Name of the agent producing the memo")
    agent_type: Literal["fundamentals", "bull", "bear", "market_risk"] 
    thesis: str = Field(description="Core viewpoint of the agent in 2-4 sentences")
    key_points: List[str] = Field(description="3-5 most important supporting points")
    risks: List[str] = Field(description="Main risks or uncertainties from this agent's perspective")
    confidence: int = Field(description="Confidence score from 1 to 10")
    data_points: Optional[List[str]] = Field(
        default=None,
        description="Optional supporting quantitative metrics or data points"
    )


class CommitteeDecision(BaseModel):
    company: str = Field(description="Company name or ticker under review")
    recommendation: Literal["Buy", "Hold", "Avoid"] = Field(description="Final committee recommendation")
    confidence: int = Field(description="Overall confidence score from 1 to 10")
    summary: str = Field(description="High-level summary of the final decision")
    bull_case: List[str] = Field(description="Strongest arguments in favor")
    bear_case: List[str] = Field(description="Strongest arguments against")
    key_monitoring_points: List[str] = Field(description="Signals or developments to watch going forward")
    final_rationale: str = Field(description="Detailed explanation of the final committee decision")