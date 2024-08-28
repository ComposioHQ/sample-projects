from openai import OpenAI
from composio_openai import ComposioToolSet, App,Action
from composio.client.exceptions import NoItemsFound
import os 

# check for OPENAI_API_KEY
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set")

# collect user id from input
user_id = input("What's your name?\n")

openai_client = OpenAI()
composio_toolset = ComposioToolSet(entity_id=user_id) # Entity ID is unique to each user
entity = composio_toolset.get_entity()

# Solve authentication
def authenticate_app(app: App):
    try:
        entity.get_connection(app=app)

        print(f"User {user_id} is already authenticated with {app.name}")

    except NoItemsFound as e:

        # Create a request to initiate connection
        request = entity.initiate_connection(app, redirect_url="https://google.com")

        print(
            f"Please authenticate {app.name} in the browser and come back here. URL: {request.redirectUrl}"
        )

        # Poll until the connection is activea
        try:
            connected_account = request.wait_until_active(client=composio_toolset.client, timeout=100)
            print(f"Authenticated : {app.name}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

authenticate_app(App.GMAIL)
authenticate_app(App.GOOGLECALENDAR)


# Get GitHub tools that are pre-configured
# Retrieve actions
gmail_tools = composio_toolset.get_tools(apps=[App.GMAIL])

google_calendar_tools = composio_toolset.get_actions(actions=[Action.GOOGLECALENDAR_CREATE_EVENT,Action.GOOGLECALENDAR_UPDATE_EVENT])

# Setup openai assistant

assistant_instruction = "You are a super intelligent personal assistant\n"

# Prepare assistant

assistant = openai_client.beta.assistants.create(
    name="Personal Assistant",
    instructions=assistant_instruction,
    model="gpt-4-turbo-preview",
    tools=[*gmail_tools, *google_calendar_tools],  # type: ignore
)

thread = openai_client.beta.threads.create()

url = f"https://platform.openai.com/playground/assistants?assistant={assistant.id}&thread={thread.id}"
print("Conversation URL: ",url)

while True:
    # collect task from input
    my_task = input("\nWhat do you want to do?\n")
    if my_task == "exit":
        break

    # create a thread
    message = openai_client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=my_task
    )

    

    # Execute Agent with integrations
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )

    # Execute function calls
    response_after_tool_calls = composio_toolset.wait_and_handle_assistant_tool_calls(
        client=openai_client,
        run=run,
        thread=thread,
    )

    messages = openai_client.beta.threads.messages.list(
        thread_id=thread.id
    )
    
    print(messages.data[0].content)