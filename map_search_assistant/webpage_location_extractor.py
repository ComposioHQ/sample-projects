from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from composio_crewai import ComposioToolSet, App, Action
import os

llm = ChatOpenAI(model="gpt-4o")

composio_toolset = ComposioToolSet(api_key = os.environ["COMPOSIO_API_KEY"])
tools = composio_toolset.get_tools(apps=[App.WEBTOOL])

location_extractor_agent = Agent(
    role="Web Location Extractor",
    goal="Your job is to take a specific webpage as input, crawls the html and extracts the embedded places in a specific format",
    backstory=(
        "You are an AI agent that is a specialises in scraping and crawling a web page html"
        "Extract the embedded places in a specific format and then store them in a json format"
        "The json format contains name, place, address, website, telephone number "
    )
)

webpage = input("Enter Web Page link:")
task = Task(
    description=f"Search for all the locations in the following webpage:{webpage}",
    agent=location_extractor_agent,
    tools = tools,
    expected_output="A list of all the places in JSON format from the web page",
)

my_crew = Crew(agents=[location_extractor_agent], tasks=[task])

result = my_crew.kickoff()
print(result)