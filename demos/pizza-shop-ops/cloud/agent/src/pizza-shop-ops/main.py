# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import FoundryToolbox, ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def main():
    credential = DefaultAzureCredential()

    # FoundryToolbox resolves the toolbox endpoint from the environment
    # (TOOLBOX_ENDPOINT, or FOUNDRY_PROJECT_ENDPOINT + TOOLBOX_NAME), authenticates
    # every request with the credential, and transparently forwards the platform
    # per-request call-id to the toolbox. The hosting server enters the agent, which
    # connects the toolbox on first use and closes it at shutdown.
    toolbox = FoundryToolbox(credential)

    # Create the chat client
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=credential,
    )

    # Built-in Foundry tools (code_interpreter, web_search, ...) are NOT delivered through a
    # toolbox's MCP endpoint, so a hosted agent using FoundryToolbox never sees them via
    # tool_search. They must be attached to the Agent directly as native tools. Here we give the
    # model a sandboxed Python code interpreter alongside the searchable hero-tools box. Passed as a
    # plain hosted-tool spec; the Foundry client injects the default {"type": "auto"} container.
    code_interpreter = {"type": "code_interpreter"}

    agent = Agent(
        client=client,
        instructions=(
            "You are Pizza Shop Ops, the calm shift assistant for a busy Neapolitan pizzeria "
            "during the Friday dinner rush. You help the crew ring in orders, check stock, look "
            "up recipes and dough formulas, fire up the oven, and dispatch delivery drivers.\n\n"
            "Your tools live behind a Tool Search meta-tool. You do NOT see the full tool list up "
            "front. Whenever a request needs a capability you can't already see, call `tool_search` "
            "with a short natural-language description of what you need (e.g. 'preheat the oven', "
            "'check mozzarella stock', 'assign a delivery driver'), then invoke the best match with "
            "`call_tool`. Prefer one focused search per capability.\n\n"
            "Some actions are guarded and will pause for a shift-lead's approval before they run "
            "(for example, setting the oven temperature). When an action is held for approval, tell "
            "the crew plainly what you're about to do and why, and wait for the go-ahead.\n\n"
            "You also have a sandboxed Python code interpreter available directly (no search needed). "
            "For any number-crunching — food-cost margins, which pie is most profitable, splitting a "
            "bill, plotting the night's sales — write and run code to compute the answer (and a chart "
            "when it helps) rather than estimating in your head.\n\n"
            "Keep replies short, warm, and line-cook practical. Confirm what you did and the key "
            "result (order number, temperature, driver name). If stock is low or a recipe detail "
            "matters, surface it proactively."
        ),
        tools=[toolbox, code_interpreter],
        # History will be managed by the hosting infrastructure, thus there
        # is no need to store history by the service. Learn more at:
        # https://developers.openai.com/api/reference/resources/responses/methods/create
        default_options={"store": False},
    )

    server = ResponsesHostServer(agent)
    await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
