from schema.schema import ChatMessage
from openai import OpenAI
import re
from constants.const import Model_embedding, OPENAI_KEY

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

client = OpenAI(api_key=OPENAI_KEY)
def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a given text using OpenAI."""
    response = client.embeddings.create(
        input=text,
        model=Model_embedding
    )
    return response.data[0].embedding

def cutinfo(info_list) -> list[str]:
    
    def process_text(text: str) -> str:
        txt = text.strip()
        lower = txt.lower()

        # pattern tìm cụm chỉ màu (hỗ trợ một vài biến thể) và bắt khối sau đó đến dấu phẩy tiếp theo (hoặc hết chuỗi)
        # giải thích ngắn: bắt mọi thứ từ đầu đến phần "có màu..." và các ký tự tiếp theo (non-greedy) trước dấu phẩy tiếp theo
        color_pattern = re.compile(
            r'^(.*?có\s*màu(?:\s*sắc)?(?:\s*và\s*số\s*lượng\s*tương\s*ứng)?\s*[:：].*?)(?:,|$)',
            flags=re.IGNORECASE | re.DOTALL
        )

        m = color_pattern.search(txt)
        if m:
            return m.group(1).strip()

        # fallback: giữ đến dấu phẩy đầu tiên (như cũ)
        return txt.split(",", 1)[0].strip()

    # xử lý input là str hoặc list
    if isinstance(info_list, str):
        return [process_text(info_list)]
    else:
        return [process_text(t) for t in info_list]

def cut_info_before_comma(info_list) -> list[str]:
    
    if isinstance(info_list, str):
        return info_list.split(",", 1)[0].strip()
    else:
        result = []
        for text in info_list:
            # Tách theo dấu phẩy đầu tiên
            part = text.split(",", 1)[0].strip()
            result.append(part)
        return result

def format_color(color_str):
    txt = color_str

    # Bỏ ký tự [, ], {, }
    txt = txt.replace("[", "").replace("]", "")
    txt = txt.replace("{", "").replace("}", "")

    # Bỏ dấu nháy đơn
    txt = txt.replace("'", "")

    # Đổi dấu :  thành " - số lượng "
    txt = txt.replace(":", " - số lượng ")

    # Đổi dấu phẩy phân tách dict thành dấu chấm phẩy
    txt = txt.replace(", ", "; ")

    return txt

def join_string(item):
    for i in range(len(item)):
        name, current_price, color_options,network_sp, charge_tech, screen_size, ram, os, chip, memory, pin, sale, status, phone_company, product_specs, product_promotion= item

        final_string = ""
        if name:
            final_string += f"Tên điện thoại: {name}"

        if current_price:
            final_string += f", có giá: {current_price}"
        
        if ram:
            final_string += f", RAM: {ram}"

        if memory:
            final_string += f", Bộ nhớ: {memory}"
        
        if color_options:
            try:
                result = format_color(color_options)
                final_string += ", Có màu sắc và số lượng tương ứng: " + result
            except (ValueError, SyntaxError):
                # color_options không hợp lệ, bỏ qua
                pass

        if network_sp:
            final_string += f", hỗ trợ mạng: {network_sp}G"
            
        if charge_tech != 0:
            final_string += f", sạc nhanh: {charge_tech}W"
            
        if screen_size:
            final_string += f", kích thước màn hình: {screen_size} inch"
        
        if os:
            final_string += f", Hệ điều hành: {os}"
        
        if chip:
            final_string += f", chip xử lý: {chip}"

        
        if pin:
            final_string += f", Dung lượng Pin: {pin}mAh"
        
        if sale:
            final_string += f", Đang giảm giá: {sale}%"

        if status:
            if status.lower() != "true":
                final_string += f", Tình trạng: hết hàng"
        
        if phone_company:
            final_string += f", Hãng điện thoại: {phone_company}"

        if product_promotion:
            product_promotion = product_promotion.replace("<br>", " ").replace("\n", " ")
            final_string += f" {product_promotion}"

        if product_specs:
            product_specs = product_specs.replace("<br>", " ").replace("\n", " ")
            final_string += f" {product_specs}."

    return final_string

def is_in_stock(product_list) -> bool:
    """
    Kiểm tra xem trong list mô tả sản phẩm có chứa trạng thái 'còn hàng' hay không.
    Trả về False nếu còn hàng, True nếu hết hàng hoặc không tìm thấy.
    """
    if not product_list:
        return False
    if isinstance(product_list, list):
        text = " ".join(product_list).lower()
    else:
        text = product_list.lower()  # Ghép lại thành 1 chuỗi & lowercase
    
    # Tìm 'tình trạng:' trước, sau đó kiểm tra nội dung sau nó
    if "tình trạng:" in text:
        # Lấy phần sau "tình trạng:"
        after_status = text.split("tình trạng:")[1].split(",")[0].strip()

        # Kiểm tra cụm sau tình trạng
        return "hết hàng" in after_status
    return False

def extract_product_info(text_list):
    # Nếu list rỗng
    if not text_list:
        return None

    # Lấy phần tử đầu tiên rồi convert thành string
    if isinstance(text_list, list):
        text = " ".join(text_list)
    else:
        text = text_list

    # Tên điện thoại
    name_match = re.search(r"Tên điện thoại:\s*([^,]+)", text, re.IGNORECASE)
    name = name_match.group(1).strip() if name_match else None

    # Giá
    price_match = re.search(r"có giá:\s*([0-9\.]+)", text, re.IGNORECASE)
    price = price_match.group(1).strip() if price_match else None

    # RAM
    ram_match = re.search(r"RAM:\s*([0-9]+gb)", text, re.IGNORECASE)
    ram = ram_match.group(1).strip() if ram_match else None

    # Bộ nhớ
    memory_match = re.search(r"Bộ nhớ:\s*([0-9]+gb)", text, re.IGNORECASE)
    memory = memory_match.group(1).strip() if memory_match else None

    return {
        "name": name,
        "price": price,
        "ram": ram,
        "memory": memory
    }