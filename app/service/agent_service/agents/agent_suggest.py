import requests
from langgraph.prebuilt import create_react_agent
from constants.const import model, URL
from constants.prompts_system import SUGGEST_PROMPT

def suggest_tool(phone_company, price_range, features):
    """
    Hàm gợi ý sản phẩm dựa trên yêu cầu của người dùng.    
    Returns:
        dict: Thông tin sản phẩm gợi ý (tên, giá cả...).
    """
    
suggest_agent = create_react_agent(
                            model=model,
                            tools=[suggest_tool],
                            name="suggest_agent",
                            prompt=SUGGEST_PROMPT,
                        )