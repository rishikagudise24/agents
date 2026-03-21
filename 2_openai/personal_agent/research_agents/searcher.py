from agents import Agent, WebSearchTool, ModelSettings


search_agent = Agent(
    name="Web Researcher",
    instructions="""
    You are a web research agent.

    You are given:
    - the original user query
    - a specific search query

    Your job:
    1. Use web search to gather relevant information
    2. Focus on information that helps answer the original query
    3. Summarize clearly in 2–3 paragraphs (max 300 words)

    Be accurate, relevant, and avoid unnecessary details.
    """,
    tools=[WebSearchTool(search_context_size="low")],
    model_settings=ModelSettings(tool_choice="required")
)