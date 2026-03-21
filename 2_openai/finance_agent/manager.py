import asyncio

from agents import Runner
from models.schema import AnalysisRequest, AgentMemo, CommitteeDecision

from finance_agents.fundamentals import fundamentals_agent
from finance_agents.bull import bull_agent
from finance_agents.bear import bear_agent
from finance_agents.market_risk import market_risk_agent
from finance_agents.committee_chair import committee_chair_agent
from services.market_data import get_market_summary


class InvestmentCommitteeManager:
    def _build_agent_input(self, request: AnalysisRequest, market_data: dict) -> str:
        return f"""
            Ticker: {request.ticker}
            Investment Horizon: {request.horizon}
            Risk Profile: {request.risk_profile}

            Market Data:
            - Current Price: {market_data["recent_price"]}
            - 1-Year Return: {market_data["annual_return_pct"]}%
            - Annualized Volatility: {market_data["volatility_pct"]}%
            """

    def _build_committee_input(
        self,
        request: AnalysisRequest,
        fundamentals_memo: AgentMemo,
        bull_memo: AgentMemo,
        bear_memo: AgentMemo,
        market_risk_memo: AgentMemo,
    ) -> str:
        return f"""
Ticker: {request.ticker}
Investment Horizon: {request.horizon}
Risk Profile: {request.risk_profile}

Fundamentals Memo:
Agent Name: {fundamentals_memo.agent_name}
Agent Type: {fundamentals_memo.agent_type}
Thesis: {fundamentals_memo.thesis}
Key Points:
- {"\n- ".join(fundamentals_memo.key_points)}
Risks:
- {"\n- ".join(fundamentals_memo.risks)}
Confidence: {fundamentals_memo.confidence}
Data Points:
- {"\n- ".join(fundamentals_memo.data_points) if fundamentals_memo.data_points else "None"}

Bull Memo:
Agent Name: {bull_memo.agent_name}
Agent Type: {bull_memo.agent_type}
Thesis: {bull_memo.thesis}
Key Points:
- {"\n- ".join(bull_memo.key_points)}
Risks:
- {"\n- ".join(bull_memo.risks)}
Confidence: {bull_memo.confidence}
Data Points:
- {"\n- ".join(bull_memo.data_points) if bull_memo.data_points else "None"}

Bear Memo:
Agent Name: {bear_memo.agent_name}
Agent Type: {bear_memo.agent_type}
Thesis: {bear_memo.thesis}
Key Points:
- {"\n- ".join(bear_memo.key_points)}
Risks:
- {"\n- ".join(bear_memo.risks)}
Confidence: {bear_memo.confidence}
Data Points:
- {"\n- ".join(bear_memo.data_points) if bear_memo.data_points else "None"}

Market / Risk Memo:
Agent Name: {market_risk_memo.agent_name}
Agent Type: {market_risk_memo.agent_type}
Thesis: {market_risk_memo.thesis}
Key Points:
- {"\n- ".join(market_risk_memo.key_points)}
Risks:
- {"\n- ".join(market_risk_memo.risks)}
Confidence: {market_risk_memo.confidence}
Data Points:
- {"\n- ".join(market_risk_memo.data_points) if market_risk_memo.data_points else "None"}
"""

    async def _run_fundamentals_agent(self, request: AnalysisRequest, market_data: dict) -> AgentMemo:
        result = await Runner.run(
            fundamentals_agent,
            self._build_agent_input(request, market_data),
        )
        return result.final_output

    async def _run_bull_agent(self, request: AnalysisRequest,  market_data: dict) -> AgentMemo:
        result = await Runner.run(
            bull_agent,
            self._build_agent_input(request, market_data),
        )
        return result.final_output

    async def _run_bear_agent(self, request: AnalysisRequest,  market_data: dict) -> AgentMemo:
        result = await Runner.run(
            bear_agent,
            self._build_agent_input(request, market_data),
        )
        return result.final_output

    async def _run_market_risk_agent(self, request: AnalysisRequest,  market_data: dict) -> AgentMemo:
        result = await Runner.run(
            market_risk_agent,
            self._build_agent_input(request, market_data),
        )
        return result.final_output

    async def run_committee(self, request: AnalysisRequest):
        try:
            yield f"Starting investment committee analysis for {request.ticker}..."
            yield "Fetching market data..."
            try:
                market_data = get_market_summary(request.ticker)
            except ValueError as e:
                yield f"Market data error: {str(e)}"
                return
            yield "Running analyst agents in parallel..."

            tasks = [
                asyncio.create_task(self._run_fundamentals_agent(request, market_data)),
                asyncio.create_task(self._run_bull_agent(request, market_data)),
                asyncio.create_task(self._run_bear_agent(request, market_data)),
                asyncio.create_task(self._run_market_risk_agent(request, market_data)),
            ]

            fundamentals_memo, bull_memo, bear_memo, market_risk_memo = await asyncio.gather(*tasks)

            yield "Fundamentals memo complete."
            yield "Bull memo complete."
            yield "Bear memo complete."
            yield "Market / risk memo complete."
            yield "Committee chair is synthesizing the final decision..."

            committee_input = self._build_committee_input(
                request,
                fundamentals_memo,
                bull_memo,
                bear_memo,
                market_risk_memo,
            )

            committee_result = await Runner.run(
                committee_chair_agent,
                committee_input,
            )

            final_decision: CommitteeDecision = committee_result.final_output

            yield "Final committee decision complete."

            yield {
                "fundamentals_memo": fundamentals_memo,
                "bull_memo": bull_memo,
                "bear_memo": bear_memo,
                "market_risk_memo": market_risk_memo,
                "committee_decision": final_decision,
            }

        except Exception as e:
            yield f"An error occurred: {str(e)}"