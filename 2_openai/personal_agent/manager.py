import asyncio
from typing import List

from agents import Runner
from research_agents.planner import planner_agent
from research_agents.searcher import search_agent
from research_agents.writer import writer_agent
from research_agents.notifier import send_email, send_push_notification
from models.schemas import SearchPlan, Report


class ResearchManager:
    async def _run_single_search(self, original_query: str, search_query: str) -> str:
        result = await Runner.run(
            search_agent,
            f"""
Original user query:
{original_query}

Specific search query:
{search_query}
""",
        )
        return str(result.final_output)

    async def _run_all_searches(self, original_query: str, plan: SearchPlan) -> List[str]:
        tasks = [
            asyncio.create_task(
                self._run_single_search(original_query, item.query)
            )
            for item in plan.searches
        ]

        results: List[str] = []

        for completed_task in asyncio.as_completed(tasks):
            result = await completed_task
            results.append(result)

        return results

    def _format_report_markdown(self, report: Report) -> str:
        insights_md = "\n".join(f"- {insight}" for insight in report.key_insights)
        risks_md = "\n".join(f"- {risk}" for risk in report.risks)

        return f"""# {report.title}

## Key Insights
{insights_md}

## Analysis
{report.analysis}

## Risks / Counterpoints
{risks_md}

## Conclusion
{report.conclusion}
"""

    async def run(self, query: str):
        try:
            yield "Planning research..."

            planner_result = await Runner.run(planner_agent, query)
            plan: SearchPlan = planner_result.final_output

            if not plan.searches:
                yield "No searches were generated."
                return

            yield f"Generated {len(plan.searches)} search queries."

            for i, item in enumerate(plan.searches, start=1):
                yield f"Search {i}: {item.query}"

            yield "Running web searches..."

            search_results = await self._run_all_searches(query, plan)

            yield f"Completed {len(search_results)} searches."
            yield "Writing final report..."

            writer_input = f"""
Original user query:
{query}

Web search summaries:
{chr(10).join(f"- {result}" for result in search_results)}
"""

            writer_result = await Runner.run(writer_agent, writer_input)
            report: Report = writer_result.final_output

            yield "Sending email notification..."
            send_email(report)

            yield "Sending push notification..."
            send_push_notification(report)

            yield "Research complete."

            formatted_report = self._format_report_markdown(report)
            yield formatted_report

        except Exception as e:
            yield f"An error occurred: {str(e)}"