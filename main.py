import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel

from agents.run import RunConfig

# Load environment variables
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

# Set up the external Gemini-compatible OpenAI client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Define the model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Runner configuration
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Define language-specific agents
english_agent = Agent(
    name="english_agent",
    instructions="You are a helpful assistant who responds in English.",
    model=model
)

roman_urdu_agent = Agent(
    name="roman_urdu_agent",
    instructions="You are a helpful assistant who responds in Roman Urdu.",
    model=model
)

# Convert them into tools
english_tool = english_agent.as_tool(
    tool_name="english_agent",
    tool_description="Use this tool if the user is speaking in English."
)

roman_urdu_tool = roman_urdu_agent.as_tool(
    tool_name="roman_urdu_agent",
    tool_description="Use this tool if the user is speaking in Roman Urdu."
)

# Define the main agent that routes to the appropriate tool
main_agent = Agent(
    name="main_agent",
    instructions=(
        "You are the main assistant. Determine the language of the user input. "
        "If it is English, use the 'english_agent' tool. "
        "If it is Roman Urdu, use the 'roman_urdu_agent' tool."
    ),
    model=model,
    tools=[english_tool, roman_urdu_tool]
)

# Run synchronously
if __name__ == "__main__":
    user_input = input("Tell me your language to talk: ")
    result = Runner.run_sync(main_agent, user_input, run_config=config)
    print("\nFinal Output:", result.final_output)
