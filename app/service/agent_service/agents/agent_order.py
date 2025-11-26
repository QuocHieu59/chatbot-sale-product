from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from typing import Any
import requests as request
from service.agent_service.agents.agent_product import rag_context_ids
from utils.agent import cutinfo, is_in_stock, extract_product_info
from constants.const import model, URL
from dto.order import current_user_id

from constants.prompts_system import ORDER_PROMPT, product_prompt_verify
from constants.const import OPENAI_KEY, Model_Name, Model_highcost
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=OPENAI_KEY)

class OrderState(BaseModel):
    product_name: str | None = None
    id_product: str | None = None
    color: str | None = None
    customer_phone: str | None = None
    customer_address: str | None = None

def verify_product(name_product, ram, memory, color):
    
    """
    Kiểm tra xem có tồn tại tên sản phẩm trong cửa hàng
    Returns:
    str: thông tin để trả lời
    """
    if not name_product or not ram or not memory or not color:
        return "Vui lòng cung cấp đầy đủ thông tin tên sản phẩm, RAM, bộ nhớ và màu sắc để tôi có thể giúp bạn kiểm tra."
    try:
        product_info = f"{name_product}, RAM: {ram}, Bộ nhớ: {memory}, Màu sắc: {color}"
        info1 = rag_context_ids(product_info, 1)
        # print("info1 là", info1[0]['id'])
        # print("state.user_id là", state.user_id)
        # print("product_info là", product_info)
        #print("info1 là", info1[0]['information'])
        info1_process = cutinfo(info1[0]['information'])
        #print("info1_process là", info1_process)
    except Exception:
        info1 = None
    print(is_in_stock(info1[0]['information']))
    if is_in_stock(info1[0]['information']):
        return f" Hiện tại điện thoại bạn chọn đã hết hàng"
    else:
        response = client.chat.completions.create(
            model=Model_highcost, 
            messages=[
                {"role": "system", "content": "Bạn là một chuyên gia so khớp sản phẩm điện thoại."},
                {"role": "user", "content": product_prompt_verify(product_info, info1_process)}
            ],
            temperature=0 
            )
        result = response.choices[0].message.content.strip()
        print(result)
        
        if "yes" not in result.lower():
            return f"Rất tiếc, cửa hàng chúng tôi không có sản phẩm điện thoại với thông tin bạn cung cấp. do {result}"
        else:
            product = extract_product_info(info1[0]['information'])
            print(product_info)
            return f"Sản phẩm bạn muốn đặt là {product['name']} với giá {product['price']}, RAM {product['ram']}, bộ nhớ {product['memory']}, và màu {color}. Bạn có muốn đặt mua sản phẩm này không?"
  
def order_product(name_product, ram, memory, color, phone_number, address, state: OrderState):
    """
    Hàm đặt hàng điện thoại gồm các biến product_information thông tin điện thoại, phone_number: số điện thoại, address: địa chỉ nhận hàng.
    return:
    dict chứa thông tin đơn hàng
    """
    # info1 = rag_context(product_information, 1)
    # product = extract_product_info(info1)
    product_info = f"{name_product}, RAM: {ram}, Bộ nhớ: {memory}, Màu sắc: {color}"
    info1 = rag_context_ids(product_info, 1)
    state.product_name = product_info
    state.id_product = info1[0]['id']
    state.color = color.lower()
    state.customer_phone = phone_number
    state.customer_address = address
    if state.product_name and state.customer_phone and state.customer_address and state.id_product and state.color:
        print("chạy vào hàm này chưa")
        user_id = current_user_id.get()
        print("user_id trong verify_product là", user_id)
        print(state.product_name)
        orders_endpoint = f"{URL}/orders"
        order_data = {
            "id_phone": state.id_product,
            "customer_phone": state.customer_phone,
            "customer_address": state.customer_address,
            "id_user": user_id,
            "info": state.product_name,
            "color": state.color
        }
        print("Dữ liệu đơn hàng gửi đi:", order_data)
        # return {
        #     "message": "Đơn hàng của bạn đang được xử lý."
        # }
        # Gửi yêu cầu đặt hàng đến dịch vụ bên ngoài
        response = request.post(orders_endpoint, json=order_data, verify=False)
        if response.status_code == 200:
            order_response = response.json()
            print("Phản hồi từ dịch vụ đặt hàng:", order_response)
            if order_response.get("success"):
                return order_response.get("data")
            else:
                return {
                    "error": "Đặt hàng thất bại. Vui lòng thử lại sau."
                }
        else:
            return {
                "error": "Đặt hàng thất bại. Vui lòng thử lại sau."
            }
        
order_agent = create_react_agent(
                            model=model,
                            tools=[verify_product, order_product],
                            name="order_agent",
                            prompt=ORDER_PROMPT,
                        )