from agents import Agent
from models.schemas import SearchPlan

planner_agent = Agent(
    name="Research Planner",
    instructions="""
    Break the user's query into 3-5 high-quality search queries and reasons for each query selected.

    Ensure:
    - diversity (background, trends, data)
    - clarity
    - no redundancy
    """,
    output_type=SearchPlan
)