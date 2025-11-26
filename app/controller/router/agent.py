from fastapi import APIRouter, Depends, HTTPException, status
from constants.const import DEFAULT_AGENT
from typing import Any
from fastapi.responses import StreamingResponse
from service.agent_service.agent_service import _sse_response_example, message_generator, _handle_input
from schema.schema import StreamInput, UserInput, ChatMessage, ServiceMetadata
from dto.order import current_user_id
from langchain_core.messages import AIMessage
from service.agent_service.agent_manager import get_agent, Pregel
from utils.agent import langchain_to_chat_message
from service.agent_service.agent_manager import get_all_agent_info
from schema.schema import AllModelEnum

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post(
    "/{agent_id}/stream",
    response_class=StreamingResponse,
    responses=_sse_response_example(),
    operation_id="stream_with_agent_id",
)
@router.post("/stream", response_class=StreamingResponse, responses=_sse_response_example())
async def stream(user_input: StreamInput, agent_id: str = DEFAULT_AGENT) -> StreamingResponse:
    """
    Stream an agent's response to a user input, including intermediate messages and tokens.

    If agent_id is not provided, the default agent will be used.
    Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
    is also attached to all messages for recording feedback.
    Use user_id to persist and continue a conversation across multiple threads.

    Set `stream_tokens=false` to return intermediate messages but not token-by-token.
    """
    return StreamingResponse(
        message_generator(user_input, agent_id),
        media_type="text/event-stream",
    )

@router.post("/{agent_id}/invoke")
@router.post("/invoke")
async def invoke(user_input: UserInput, agent_id: str = DEFAULT_AGENT) -> ChatMessage:
    """
    Invoke an agent with user input to retrieve a final response.

    If agent_id is not provided, the default agent will be used.
    Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
    is also attached to messages for recording feedback.
    Use user_id to persist and continue a conversation across multiple threads.
    """
    # NOTE: Currently this only returns the last message or interrupt.
    # In the case of an agent outputting multiple AIMessages (such as the background step
    # in interrupt-agent, or a tool step in research-assistant), it's omitted. Arguably,
    # you'd want to include it. You could update the API to return a list of ChatMessages
    # in that case.
    agent: Pregel = get_agent(agent_id)
    kwargs, run_id = await _handle_input(user_input, agent)
    #print("kwargs là", kwargs)
    current_user_id.set(user_input.user_id)
    #print("user_input.user_id là", user_input.user_id)
    try:
        response_events: list[tuple[str, Any]] = await agent.ainvoke(**kwargs, stream_mode=["updates", "values"])  # type: ignore # fmt: skip
        response_type, response = response_events[-1]
        if response_type == "values":
            # Normal response, the agent completed successfully
            output = langchain_to_chat_message(response["messages"][-1])
            # print("kwargs mới là", kwargs)
            #print("output là", output)
        elif response_type == "updates" and "__interrupt__" in response:
            # The last thing to occur was an interrupt
            # Return the value of the first interrupt as an AIMessage
            output = langchain_to_chat_message(
                AIMessage(content=response["__interrupt__"][0].value)
            )
        else:
            raise ValueError(f"Unexpected response type: {response_type}")

        output.run_id = str(run_id)
        return output
    except Exception as e:
        #logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")
    

@router.get("/info")
async def info() -> ServiceMetadata:
    """Get service metadata."""
    return ServiceMetadata(
        agents=get_all_agent_info(),
        models=[AllModelEnum.GPT_4O_MINI, AllModelEnum.GPT_4O],
        default_agent=DEFAULT_AGENT,
        default_model=AllModelEnum.GPT_4O_MINI,
    )