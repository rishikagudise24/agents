import gradio as gr
from dotenv import load_dotenv

from manager import InvestmentCommitteeManager
from models.schema import AnalysisRequest, AgentMemo, CommitteeDecision

load_dotenv(override=True)

manager = InvestmentCommitteeManager()


def format_memo(memo: AgentMemo) -> str:
    data_points = "\n".join(f"- {point}" for point in (memo.data_points or [])) or "- None"
    key_points = "\n".join(f"- {point}" for point in memo.key_points)
    risks = "\n".join(f"- {risk}" for risk in memo.risks)

    return f"""## {memo.agent_name}

**Agent Type:** {memo.agent_type}  
**Confidence:** {memo.confidence}/10  

### Thesis
{memo.thesis}

### Key Points
{key_points}

### Risks
{risks}

### Data Points
{data_points}
"""


def format_committee_decision(decision: CommitteeDecision) -> str:
    bull_case = "\n".join(f"- {point}" for point in decision.bull_case)
    bear_case = "\n".join(f"- {point}" for point in decision.bear_case)
    monitoring = "\n".join(f"- {point}" for point in decision.key_monitoring_points)

    return f"""# {decision.company}

## Final Recommendation
**{decision.recommendation}**  
**Confidence:** {decision.confidence}/10

## Summary
{decision.summary}

## Bull Case
{bull_case}

## Bear Case
{bear_case}

## Key Monitoring Points
{monitoring}

## Final Rationale
{decision.final_rationale}
"""


async def run_committee_analysis(ticker: str, horizon: str, risk_profile: str):
    if not ticker or not ticker.strip():
        yield (
            "Please enter a stock ticker.",
            "No recommendation yet.",
            "",
            "",
            "",
            "",
        )
        return

    request = AnalysisRequest(
        ticker=ticker.strip().upper(),
        horizon=horizon,
        risk_profile=risk_profile,
    )

    log = ""
    final_recommendation = "Running analysis..."
    fundamentals_md = ""
    bull_md = ""
    bear_md = ""
    market_risk_md = ""

    async for update in manager.run_committee(request):
        if isinstance(update, str):
            log += f"• {update}\n"
            yield (
                log,
                final_recommendation,
                fundamentals_md,
                bull_md,
                bear_md,
                market_risk_md,
            )
        elif isinstance(update, dict):
            fundamentals_md = format_memo(update["fundamentals_memo"])
            bull_md = format_memo(update["bull_memo"])
            bear_md = format_memo(update["bear_memo"])
            market_risk_md = format_memo(update["market_risk_memo"])
            final_recommendation = format_committee_decision(update["committee_decision"])

            yield (
                log,
                final_recommendation,
                fundamentals_md,
                bull_md,
                bear_md,
                market_risk_md,
            )


with gr.Blocks(title="Investment Committee Simulator", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # Investment Committee Simulator
        Enter a stock ticker and let a multi-agent investment committee debate the case from
        different perspectives before issuing a final recommendation.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            ticker_input = gr.Textbox(
                label="Ticker",
                placeholder="e.g. NVDA, AAPL, MSFT",
            )

            horizon_input = gr.Dropdown(
                label="Investment Horizon",
                choices=["3 months", "6 months", "12 months", "3 years", "5 years"],
                value="12 months",
            )

            risk_profile_input = gr.Dropdown(
                label="Risk Profile",
                choices=["conservative", "moderate", "aggressive"],
                value="moderate",
            )

            with gr.Row():
                run_button = gr.Button("Run Committee", variant="primary")
                clear_button = gr.Button("Clear")

        with gr.Column(scale=2):
            final_output = gr.Markdown(label="Final Recommendation", value="No recommendation yet.")

    with gr.Row():
        progress_output = gr.Textbox(
            label="Live Committee Log",
            lines=12,
            max_lines=20,
            show_copy_button=True,
        )

    with gr.Tabs():
        with gr.Tab("Fundamentals"):
            fundamentals_output = gr.Markdown()

        with gr.Tab("Bull Case"):
            bull_output = gr.Markdown()

        with gr.Tab("Bear Case"):
            bear_output = gr.Markdown()

        with gr.Tab("Market / Risk"):
            market_risk_output = gr.Markdown()

    run_button.click(
        fn=run_committee_analysis,
        inputs=[ticker_input, horizon_input, risk_profile_input],
        outputs=[
            progress_output,
            final_output,
            fundamentals_output,
            bull_output,
            bear_output,
            market_risk_output,
        ],
    )

    clear_button.click(
        fn=lambda: ("", "No recommendation yet.", "", "", "", ""),
        inputs=None,
        outputs=[
            progress_output,
            final_output,
            fundamentals_output,
            bull_output,
            bear_output,
            market_risk_output,
        ],
    )


if __name__ == "__main__":
    demo.launch()