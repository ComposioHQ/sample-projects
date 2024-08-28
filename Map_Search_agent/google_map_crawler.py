from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from composio_crewai import ComposioToolSet, Action, App


# add OPENAI_API_KEY to env variables.
llm = ChatOpenAI(model="gpt-4o")

# Get All the tools
composio_toolset = ComposioToolSet()
tools = composio_toolset.get_tools(apps=[App.SERPAPI])

# Define agent
google_maps_agent = Agent(
    role="Google Maps Agent",
    goal="Search for places in using Google Maps API",
    backstory=(
        "You are an AI agent specialized in using Google Maps API to find "
        "and list places in specific locations. Your current task is to search "
        "for places in world and provide a comprehensive list."
    ),
    verbose=True,
    tools=tools,
    llm=llm,
)

task = Task(
    description="Search for square pizza places in New York",
    agent=google_maps_agent,
    expected_output="A list of notable places in New York with brief descriptions",
)

my_crew = Crew(agents=[google_maps_agent], tasks=[task])

result = my_crew.kickoff()
print(result)
