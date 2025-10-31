import os
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from constants.prompts_system import SUPERVISOR_PROMPT
from constants.const import model
from service.agent_service.agents.agent_shop import shop_information_agent

# Create supervisor agent
workflow = create_supervisor(
    agents=[shop_information_agent],
    model=model,
    prompt=SUPERVISOR_PROMPT,
    add_handoff_back_messages=False,
)

supervisor_agent = workflow.compile(checkpointer=MemorySaver(), store=InMemoryStore())