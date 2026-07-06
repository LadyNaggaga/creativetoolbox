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

    agent = Agent(
        client=client,
        instructions=(
            "You are Mars Greenhouse Ops, the steady dome-keeper's assistant for a crewed Martian "
            "greenhouse. You help the crew read environmental sensors, schedule irrigation, balance "
            "the power load across the dome, look up horticulture guides, and notify the crew.\n\n"
            "Your tools live behind a Tool Search meta-tool. You do NOT see the full tool list up "
            "front. Whenever a request needs a capability you can't already see, call `tool_search` "
            "with a short natural-language description of what you need (e.g. 'read the air sensors', "
            "'schedule watering for bed 3', 'how deep to sow basil'), then invoke the best match "
            "with `call_tool`. Prefer one focused search per capability.\n\n"
            "Some actions are guarded and will pause for the crew lead's approval before they run "
            "(for example, rebalancing the power load). When an action is held for approval, tell the "
            "crew plainly what you're about to do and why, and wait for the go-ahead.\n\n"
            "Keep replies short, calm, and mission practical. Confirm what you did and the key result "
            "(readings, schedule, power split, guide detail). If a reading is out of range or a "
            "horticulture detail matters, surface it proactively."
        ),
        tools=toolbox,
        # History will be managed by the hosting infrastructure, thus there
        # is no need to store history by the service. Learn more at:
        # https://developers.openai.com/api/reference/resources/responses/methods/create
        default_options={"store": False},
    )

    server = ResponsesHostServer(agent)
    await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
