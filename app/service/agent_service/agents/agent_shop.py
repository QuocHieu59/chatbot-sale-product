import requests
from langgraph.prebuilt import create_react_agent
from constants.const import model, URL
from constants.prompts_system import prompt_Test

def Get_Shop_Info_tool():
    """
    Lấy thông tin chi tiết về cửa hàng từ API theo shop_id.    
    Returns:
        dict: Thông tin chi tiết cửa hàng (tên, địa chỉ, mô tả...).
    """
    print('----Get_Shop_Info_tool')
    try:
        list_shop = []
        response = requests.get(f"{URL}/shop/inf", verify=False)
        data = response.json()       
        for shop in data.get("data", []):
            info = f"Tên shop: {shop['name_shop']} | Địa chỉ: {shop['adress']} | Giờ làm việc: {shop['wrk_hrs']} | Nhân viên tư vấn: {shop['inf_staff']}"
            list_shop.append(info)
        return list_shop

    except requests.exceptions.RequestException as e:
        return {"error": f"Không thể lấy thông tin shop: {e}"}

shop_information_agent = create_react_agent(
                            model=model,
                            tools=[Get_Shop_Info_tool],
                            name="shop_information_agent",
                            prompt=prompt_Test,
                        )