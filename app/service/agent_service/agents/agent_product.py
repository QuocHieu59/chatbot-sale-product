import numpy as np
from typing import Dict
import requests
from langchain.tools import tool
import chromadb
from langgraph.prebuilt import create_react_agent

from openai import OpenAI
from constants.prompts_system import PRODUCT_PROMPT, product_prompt_classify, prompt_query_PostgreSQL
from constants.const import model, Model_Name, URL, OPENAI_KEY, COLLECTION_NAME, CHROMA_CLIENT_PATH 
from utils.agent import cut_info_before_comma, get_embedding

client = OpenAI(api_key=OPENAI_KEY)
chroma_client = chromadb.PersistentClient("service/agent_service/agents/phone_db")
collection_name= COLLECTION_NAME

@tool
def query_products(user_input: str) -> str:
    """
    Use this function when users want to **find, filter or browse product lists**.
    Args:
        user_input (str): User's input for filtering or searching products.
    Returns:
        str: A formatted list of products matching the user's criteria, if successful
            An error message explaining why no products were found or the request is invalid
    """
    try:
        list_product = []
        data = query_phone(user_input)
        for product in data.get("data", []):
            name = product.get("name")
            price = product.get("current_price")
            ram = product.get("ram")
            memory = product.get("memory")
            list_product.append({
                "name": name,
                "price": price,
                "memory": memory,
                "ram": ram
            })
        print("list sản phẩm là", list_product)
        if len(list_product) > 0:
                return f"List Product: {list_product}"
        else: 
                return "Hiện tại hệ thống không có sản phẩm phù hợp"
    except requests.exceptions.RequestException as e:
        return {"Hiện tại hệ thống đang bị lỗi, vui lòng thử lại sau"}
    
@tool
def rag_context(query: str,  number: int = 3) -> Dict[str, any]:
    """
    Use this function when a user requests **information related to a product** or when a user is asking about ONE specific product.
    Retrieve information about the 3 products with the highest similarity to the user's question in a single function call.
    
    Args:
    query(str): User's question.
    number(int): Number of products to retrieve (default is 3).
    
    Returns:
    Dict[str, any]: Information on 3 phone products.
    """
    # print('----Product', query)
    # print("Số lượng kết quả tool:", number)
    print("Chạy vào rag_context với query:", query)
    search_result = []
    k = 1
    result = rag_context_ids(query, number)
    for i in result:
        search_result.append(f"{k}): {i['information']}") 
        k += 1
        # print("-----")
        # print(i['information'])
    # print("Kết quả tìm kiếm:", search_result)
    return {
        "information relevant": search_result
    }

@tool
def compare_products(prod_1: str, prod_2: str) -> str:
    """
    This function is used when a user needs to compare two phone products. 
    This function checks and retrieves the corresponding information about the two phone products the user wants to compare in a single function call.
    Args:
        prod_1 (str): Name of the first product to compare.
        prod_2 (str): Name of the second product to compare.
    Returns:
        str: Information comparing two phone products,
        or error messages for the user.
    """
    info1_process = ""
    info2_process = ""
    print(f"Tên sản phẩm: {prod_1} vs {prod_2}")
    try:
        info1 = rag_context_tool(prod_1, 1)
        info1_process = cut_info_before_comma(info1)
    except Exception:
        info1 = None
    try:
        info2 = rag_context_tool(prod_2, 1)
        info2_process = cut_info_before_comma(info2)
    except Exception:
        info2 = None
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia kiểm tra so khớp tên sản phẩm điện thoại."},
            {"role": "user", "content": product_prompt_classify(prod_1, info1_process, prod_2, info2_process)}
        ],
        temperature=0 
        )
    result = response.choices[0].message.content.strip()
    print("So sánh giữa 2 sản phẩm:", info1_process, "và", info2_process)
    print("Kết quả phản hồi:", result)
    if result != "YES":
        return f" Hiện tại cửa hàng không bán điện thoại {result}"
    else:
        return f"{prod_1}: {info1}\n\n{prod_2}: {info2}"
    
def query_phone(user_input: str):
    """
    Gọi model để sinh câu SQL query dựa trên input của người dùng và thực thi trên database.
    """
    response = client.chat.completions.create(
        model=Model_Name, 
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia SQL, nhiệm vụ của bạn là sinh câu lệnh truy vấn PostgreSQL hợp lệ."},
            {"role": "user", "content": prompt_query_PostgreSQL(user_input)}
        ],
        temperature=0 
        )
    query = response.choices[0].message.content.strip()
    print("query là", query)
    try:
        response = requests.get(f"{URL}/product/", params={"query": query}, verify=False)
        data = response.json()
        return data    
        # for product in data.get("data", []):
        #     name = product.get("name")
        #     price = product.get("current_price")
        #     ram = product.get("ram")
        #     memory = product.get("memory")
        #     list_product.append({
        #         "name": name,
        #         "price": price,
        #         "memory": memory,
        #         "ram": ram
        #     })
        # print("list sản phẩm là", list_product)
        # return list_product

    except requests.exceptions.RequestException as e:
        return {"Hiện tại hệ thống đang bị lỗi, vui lòng thử lại sau"}    

def rag_context_tool(query: str,  number: int = 1) -> list[str]:
    """
    Lấy thông tin về 3 sản phẩm có độ tương đồng cao nhất đối với query.    
    Returns:
        str: Thông tin 3 sản phẩm điện thoại.
    """
    # print('----Product', query)
    # print("Số lượng kết quả tool:", number)
    
    search_result = []
    k = 1
    result = rag_context_ids(query, number)
    for i in result:
        search_result.append(f"{k}): {i['information']}") 
        k += 1
        # print("-----")
        # print(i['information'])
    return search_result

#print(rag_context('iPhone 14'))

def rag_context_ids(query: str, number: int = 3) -> list[dict]:
    """
    Lấy thông tin về 3 sản phẩm có độ tương đồng cao nhất đối với query.
    Returns:
        list[dict]: Mỗi dict chứa 'id' và 'information' của document
    """
    collection = chroma_client.get_collection(name=collection_name)
    query_embedding = get_embedding(query)
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    search_results = collection.query(
        query_embeddings=query_embedding,
        n_results=number
    )

    ids = search_results.get('ids', [])
    metadatas = search_results.get('metadatas', [])

    search_result = []

    for i, metadata_list in enumerate(metadatas):
        if isinstance(metadata_list, list):
            for j, metadata in enumerate(metadata_list):
                if isinstance(metadata, dict):
                    doc_id = ids[i][j] if ids else None
                    combined_text = metadata.get('information', 'No text available').strip()
                    search_result.append({
                        "id": doc_id,
                        "information": combined_text
                    })
    return search_result

product_agent = create_react_agent(
    model=model,
    tools=[rag_context, compare_products, query_products],
    name="product_agent",
    prompt=PRODUCT_PROMPT,
).with_config(tags=["skip_stream"])
# query = "thế bây giờ giá của sản phẩm nubia red magic 8 pro là bao nhiêu"

# # Gọi agent
# response = product_agent.run(query)

# # In kết quả
# print(response)