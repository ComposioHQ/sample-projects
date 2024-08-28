from composio_crewai import ComposioToolSet, Action, App
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
import dotenv
from utils import url_to_pdf_content


dotenv.load_dotenv()  # Load env variables

llm = ChatOpenAI(model="gpt-4o")  # Initialize the language model
composio_toolset = ComposioToolSet()  # Initialize the composio toolset
tools = composio_toolset.get_tools(apps=[App.RAGTOOL])

# get the pdf URL from the user
pdf_url = str(input("Enter the PDF URL: "))
print("Extracting PDF content from URL...")

# The PDF content is extracted from the URL
pdf_content = url_to_pdf_content(pdf_url)

# Add the PDF content to RAG
rag_add_content_action = composio_toolset.execute_action(
    action=Action.RAGTOOL_ADD_CONTENT_TO_RAG_TOOL, params={"content": pdf_content}
)

# Query from the user
query = str(input("Enter the query: "))

# Initialize the query agent
query_agent = Agent(
    role="Query Agent",
    goal="""A correct, precise answer to the query from the user.""",
    backstory="""You are an AI agent responsible for answering the query from the user. 
        You will use RAGTOOL tools to query from the PDF content and then answer the query.""",
    verbose=True,
    llm=llm,
    cache=False,
    tools=tools,
)

# Task to query the PDF content
query_task = Task(
    description=f"""Query the RAG tool to answer the query from the user.
    Query: ${query}""",
    agent=query_agent,
    expected_output="Response from the RAG tool.",
    tools=tools,
)

# Task to rephrase the response got from the RAG tool
# REASON: Many times the response is not correct, wrong grammer, incorrect words & sentences, etc.
rephrase_task = Task(
    description=f"""Rephrase the response from the RAG tool to be simple, precise, correct and most importantly, answering the user's query. Don't use any formatting, it should be a plain string.
    User's Query: ${query}""",
    agent=query_agent,
    expected_output="A plain string as the response.",
    context=[query_task],
)

# Define crew
query_crew = Crew(
    agents=[query_agent],
    tasks=[query_task, rephrase_task],
    process=Process.sequential,
    verbose=True,
)


result = query_crew.kickoff()  # Execute the query crew workflow
