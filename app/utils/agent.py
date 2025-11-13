from schema.schema import ChatMessage

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.messages import (
    ChatMessage as LangchainChatMessage,
)

def convert_message_content_to_string(content: str | list[str | dict]) -> str:
    if isinstance(content, str):
        return content
    text: list[str] = []
    for content_item in content:
        if isinstance(content_item, str):
            text.append(content_item)
            continue
        if content_item["type"] == "text":
            text.append(content_item["text"])
    return "".join(text)


def langchain_to_chat_message(message: BaseMessage) -> ChatMessage:
    """Create a ChatMessage from a LangChain message."""
    match message:
        case HumanMessage():
            human_message = ChatMessage(
                type="human",
                content=convert_message_content_to_string(message.content),
            )
            return human_message
        case AIMessage():
            ai_message = ChatMessage(
                type="ai",
                content=convert_message_content_to_string(message.content),
            )
            if message.tool_calls:
                ai_message.tool_calls = message.tool_calls
            if message.response_metadata:
                ai_message.response_metadata = message.response_metadata
            return ai_message
        case ToolMessage():
            tool_message = ChatMessage(
                type="tool",
                content=convert_message_content_to_string(message.content),
                tool_call_id=message.tool_call_id,
            )
            return tool_message
        case LangchainChatMessage():
            if message.role == "custom":
                custom_message = ChatMessage(
                    type="custom",
                    content="",
                    custom_data=message.content[0],
                )
                return custom_message
            else:
                raise ValueError(f"Unsupported chat message role: {message.role}")
        case _:
            raise ValueError(f"Unsupported message type: {message.__class__.__name__}")


def remove_tool_calls(content: str | list[str | dict]) -> str | list[str | dict]:
    """Remove tool calls from content."""
    if isinstance(content, str):
        return content
    # Currently only Anthropic models stream tool calls, using content item type tool_use.
    return [
        content_item
        for content_item in content
        if isinstance(content_item, str) or content_item["type"] != "tool_use"
    ]

from openai import OpenAI
from constants.const import OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)
def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a given text using OpenAI."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def cut_info_before_comma(info_list: list[str]) -> list[str]:
    result = []
    for text in info_list:
        # Tách theo dấu phẩy đầu tiên
        part = text.split(",", 1)[0].strip()
        result.append(part)
    return result

def join_string(item):
    for i in range(len(item)):
        name, current_price, color_options,network_sp, charge_tech, screen_size, ram, os, chip, memory, pin, sale, status, phone_company, product_specs, product_promotion= item

        final_string = ""
        if name:
            final_string += f"Tên điện thoại: {name}"

        if current_price:
            final_string += f", có giá: {current_price}"

        if network_sp:
            final_string += f", hỗ trợ mạng: {network_sp}G"
            
        if charge_tech != 0:
            final_string += f", sạc nhanh: {charge_tech}W"
            
        if screen_size:
            final_string += f", kích thước màn hình: {screen_size} inch"
        
        if ram:
            final_string += f", RAM: {ram}"
        
        if os:
            final_string += f", Hệ điều hành: {os}"
        
        if chip:
            final_string += f", chip xử lý: {chip}"

        if memory:
            final_string += f", Bộ nhớ: {memory}"
        
        if pin:
            final_string += f", Dung lượng Pin: {pin}mAh"
        
        if sale:
            final_string += f", Đang giảm giá: {sale}%"

        if status:
            if status.lower() == "true":
                final_string += f", Tình trạng: còn hàng"
            else :
                final_string +=  f", Tình trạng: hết hàng"
        
        if phone_company:
            final_string += f", Hãng điện thoại: {phone_company}"

        if product_promotion:
            product_promotion = product_promotion.replace("<br>", " ").replace("\n", " ")
            final_string += f" {product_promotion}"

        if product_specs:
            product_specs = product_specs.replace("<br>", " ").replace("\n", " ")
            final_string += f" {product_specs}"

        if color_options:
            try:
                color_options = color_options.replace('["', '').replace('"]', '').replace('"-"', ' - ')
                final_string += "có màu sắc: " + color_options
            except (ValueError, SyntaxError):
                # color_options không hợp lệ, bỏ qua
                pass


    return final_string