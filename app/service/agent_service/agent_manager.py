from dataclasses import dataclass
from langgraph.pregel import Pregel
from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel import Pregel
from abc import ABC, abstractmethod

from constants.const import DEFAULT_AGENT
from service.agent_service.agents.agent_supervisor import supervisor_agent
from schema.schema import AgentInfo

# Tạo kiểu agent có khả năng khởi tạo bất đồng bộ (async),
class LazyLoadingAgent(ABC):
    """Base class for agents that require async loading."""

    def __init__(self) -> None:
        """Initialize the agent."""
        self._loaded = False
        self._graph: CompiledStateGraph | Pregel | None = None

    @abstractmethod
    async def load(self) -> None:
        """
        Perform async loading for this agent.

        This method is called during service startup and should handle:
        - Setting up external connections (MCP clients, databases, etc.)
        - Loading tools or resources
        - Any other async setup required
        - Creating the agent's graph
        """
        raise NotImplementedError  # pragma: no cover

    def get_graph(self) -> CompiledStateGraph | Pregel:
        """
        Get the agent's graph.

        Returns the graph instance that was created during load().

        Returns:
            The agent's graph (CompiledStateGraph or Pregel)
        """
        if not self._loaded:
            raise RuntimeError("Agent not loaded. Call load() first.")
        if self._graph is None:
            raise RuntimeError("Agent graph not created during load().")
        return self._graph

AgentGraph = CompiledStateGraph | Pregel
AgentGraphLike = CompiledStateGraph | Pregel | LazyLoadingAgent

@dataclass
class Agent:
    description: str
    graph: AgentGraph

async def load_agent(agent_id: str) -> None:
    """Load lazy agents if needed."""
    graph_like = agents[agent_id].graph
    if isinstance(graph_like, LazyLoadingAgent):
        await graph_like.load()

agents: dict[str, Agent] = {
    "supervisor-agent": Agent(
        description="A langgraph supervisor agent", graph=supervisor_agent
    ),
}

def get_agent(agent_id: str) -> Pregel:
    agent_graph = agents[agent_id].graph
    if isinstance(agent_graph, LazyLoadingAgent):
        if not agent_graph._loaded:
            raise RuntimeError(f"Agent {agent_id} not loaded. Call load() first.")
        return agent_graph.get_graph()

    return agent_graph

def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]
