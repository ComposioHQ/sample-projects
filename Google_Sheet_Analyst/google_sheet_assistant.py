from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from composio_crewai import ComposioToolSet, Action, App


# add OPENAI_API_KEY to env variables.
llm = ChatOpenAI(model="gpt-4o")

# Get All the tools
composio_toolset = ComposioToolSet()
tools = composio_toolset.get_tools(apps=[App.GOOGLESHEETS])

sheet_id = input("Enter sheet id (it is found in the shared url):")

# Define agent
google_sheets_agent = Agent(
    role="Google Sheets Roadmap Analyzer",
    goal=f"Summarize the project roadmap progress from the sheetid: {sheet_id}",
    backstory=(
        "You are an AI agent specialized in analyzing Google Sheets data. "
        f"Your current task is to review the {sheet_id} sheet and provide "
        "a summary of the roadmap progress so far, highlighting completed milestones "
        "and upcoming tasks."
    ),
    verbose=True,
    tools=tools,
    llm=llm,
)

task = Task(
    description=f"Analyze the 'project_roadmap' sheet with sheet id {sheet_id} and summarize the roadmap progress so far",
    agent=google_sheets_agent,
    expected_output="A concise summary of the project roadmap progress, including completed milestones, current status, and upcoming key tasks",
)


my_crew = Crew(agents=[google_sheets_agent], tasks=[task])

result = my_crew.kickoff()
print(result)