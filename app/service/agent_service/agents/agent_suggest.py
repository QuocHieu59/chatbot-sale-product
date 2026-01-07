import requests
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langchain.tools import tool
from openai import OpenAI
from constants.const import model, URL, OPENAI_KEY, Model_highcost
from constants.prompts_system import SUGGEST_PROMPT, prompt_suggestion
from service.agent_service.agents.agent_product import query_phone

client = OpenAI(api_key=OPENAI_KEY)

@tool(return_direct=True)
def suggest_tool(phone_company, price_range, demand):
    """
    Hàm gợi ý sản phẩm dựa trên yêu cầu của người dùng.    
    Returns:
        str: Thông tin sản phẩm gợi ý (tên, giá cả...).
    """
    print("phone_company là", phone_company)
    print("price_range là", price_range)
    print("demand là", demand)
    list_product = []
    user_input = f" Điện thoại của hãng {phone_company} với mức giá lớn hơn {price_range - 5000000} và nhỏ hơn {price_range + 5000000}."
    data = query_phone(user_input)
    # print("data lấy từ query_phone là", data)
    for product in data.get("data", []):
        name = product.get("name")
        price = product.get("current_price")
        ram = product.get("ram")
        memory = product.get("memory")
        network_sp = product.get("network_sp")
        charge_tech = product.get("charge_tech")
        screen_size = product.get("screen_size")
        os = product.get("os")
        chip = product.get("chip")
        memory = product.get("memory")
        pin = product.get("pin")
        company = product.get("phone_company")
        product_specs = product.get("product_specs")
        color_options = product.get("color_options")
        joined_string = f"Tên điện thoại: {name}, Giá: {price}, RAM: {ram}, Bộ nhớ: {memory}, Hệ điều hành: {os}, Chip: {chip}, Pin: {pin}, Hỗ trợ mạng: {network_sp}G, kích thước màn hình: {screen_size} inch, Hãng sản xuất: {company}, Thông số kỹ thuật: {product_specs}, Màu sắc và số lượng tương ứng: {color_options}"
        if charge_tech != 0:
            joined_string += f", Sạc nhanh: {charge_tech}W"
        list_product.append(joined_string)
    print("list sản phẩm để gợi ý là", list_product)
    if len(list_product) > 0:
        response = client.chat.completions.create(
        model=Model_highcost, 
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia đánh giá độ phù hợp sản phẩm điện thoại dựa trên yêu cầu của người dùng."},
            {"role": "user", "content": prompt_suggestion(demand, list_product)}
        ],
        temperature=0 
        )
        query = response.choices[0].message.content.strip()
        print("query gợi ý là", query)
        return query.strip()
    else:
        return "ERROR: no_result"
suggest_agent = create_react_agent(
                            model=model,
                            tools=[suggest_tool],
                            name="suggest_agent",
                            prompt=SUGGEST_PROMPT,
                        )