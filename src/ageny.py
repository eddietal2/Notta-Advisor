from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from . import google_llm_init as google
from llama_index.core.agent.workflow import FunctionAgent
from . import custom_console
from .config import YEARS

def create_tools(index_set):
    # Creating Query Engines (tools) for each VectorStoreIndex
    individual_query_engine_tools = [
        QueryEngineTool(
            query_engine=index_set[year].as_query_engine(llm=google.llm),
            metadata=ToolMetadata(
                name=f"vector_index_{year}",
                description=f"Useful for queries about the {year} SEC 10-K for Uber",
            ),
        )
        for year in YEARS
    ]

    # Sub Question Query Engine
    sub_question_query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=individual_query_engine_tools,
        llm=google.llm,
    )

    # Outer tool
    query_engine_tool = QueryEngineTool(
        query_engine=sub_question_query_engine,
        metadata=ToolMetadata(
            name="sub_question_query_engine",
            description="Useful for analyzing multiple SEC 10-K documents for Uber",
        ),
    )

    tools = individual_query_engine_tools + [query_engine_tool]
    return tools

async def run_chat(agent):
    custom_console.simple_initializer_spinner(3, f"\n✅ Initial Program Loading complete!\n")
    print(google.llm.metadata)

    # User Input
    while True:
        text_input = input(f"{custom_console.COLOR_CYAN}~ ChiLLama Chat 🤖: {custom_console.RESET_COLOR}")
        if text_input.lower() == "exit":
            print("\n" + "-"*30 + " ~ Llama Chat Closing " + "-"*30)
            custom_console.process_timer_elapsed_time_success()
            break
        result = await agent.run(user_msg=text_input)
        response = result
        print(f"Type: {type(response)}, Data: {response._data}")
        print(f"{custom_console.COLOR_YELLOW}\nAgent{custom_console.RESET_COLOR}: {response}\n")

def create_agent(index_set):
    tools = create_tools(index_set)

    # system_prompt.txt to be used for Agents' System Prompt.
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        loaded_system_prompt = f.read()
        print(f"{loaded_system_prompt}\n")

    agent = FunctionAgent(
        tools=tools,
        llm=google.llm,
        system_prompt=loaded_system_prompt,
        verbose=True,
        name="uber_previous_finance_agent",
        description="AI Agent for Analyzing previous Uber financial years, from 2019 - 2022"
    )
    return agent