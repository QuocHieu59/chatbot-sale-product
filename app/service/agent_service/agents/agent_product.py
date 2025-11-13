import numpy as np
import requests
import chromadb
from langgraph.prebuilt import create_react_agent
from sqlalchemy.orm import Session
from openai import OpenAI
from constants.prompts_system import PRODUCT_PROMPT, product_prompt_classify, prompt_query_PostgreSQL
from constants.const import model, Model_Name, URL, OPENAI_KEY, COLLECTION_NAME, CHROMA_CLIENT_PATH 
from utils.agent import cut_info_before_comma, get_embedding
import os

client = OpenAI(api_key=OPENAI_KEY)
chroma_client = chromadb.PersistentClient("service/agent_service/agents/phone_db")
collection_name= COLLECTION_NAME

def query_products(user_input: str):
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
        list_product = []
        response = requests.get(f"{URL}/product/", params={"query": query}, verify=False)
        data = response.json()       
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
            return f"Có {len(list_product)} sản phẩm phù hợp, bao gồm: {list_product}"
        else: 
            return "Hiện tại hệ thống không có sản phẩm phù hợp"

    except requests.exceptions.RequestException as e:
        return {"Hiện tại hệ thống đang bị lỗi, vui lòng thử lại sau"}

def compare_products(prod_1: str, prod_2: str):
    """Lấy thông tin tương ứng về 2 sản phẩm điện thoại.
    Returns:
        list[dict]: Thông tin tương ứng về 2 sản phẩm điện thoại.
    """
    print(f"Tên sản phẩm: {prod_1} vs {prod_2}")
    try:
        info1 = rag_context(prod_1, 1)
        info1_process = cut_info_before_comma(info1)
    except Exception:
        info1 = None
    try:
        info2 = rag_context(prod_2, 1)
        info2_process = cut_info_before_comma(info2)
    except Exception:
        info2 = None
    response = client.chat.completions.create(
        model=Model_Name, 
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia so khớp tên sản phẩm điện thoại."},
            {"role": "user", "content": product_prompt_classify(prod_1, info1_process, prod_2, info2_process)}
        ],
        temperature=0 
        )
    result = response.choices[0].message.content.strip()
    #print("Kết quả phản hồi:", result)
    if result != "YES":
        return f" Hiện tại cửa hàng không bán điện thoại {result}"
    else:
        return [{prod_1: info1}, {prod_2: info2}]

def rag_context(query: str,  number: int = 3) -> list[str]:
    """
    Lấy thông tin về 3 sản phẩm có độ tương đồng cao nhất đối với query.    
    Returns:
        str: Thông tin 3 sản phẩm điện thoại.
    """

    print('----Product', query)

    collection = chroma_client.get_collection(name=collection_name)
    query_embedding = get_embedding(query)
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    # Perform vector search
    search_results = collection.query(
        query_embeddings=query_embedding, 
        n_results=number
    )

    metadatas = search_results.get('metadatas', [])

    search_result = []
    i = 0

    for i, metadata_list in enumerate(metadatas):
        if isinstance(metadata_list, list):  # Ensure it's a list
            for metadata in metadata_list:  # Iterate through all dicts in the list
                if isinstance(metadata, dict):
                    combined_text = metadata.get('information', 'No text available').strip()

                    search_result.append(f"{i}): {combined_text}") 
                    i += 1
    print('----result', search_result[0])
    return search_result

#print(rag_context('iPhone 14'))

product_agent = create_react_agent(
                            model=model,
                            tools=[rag_context, compare_products, query_products],
                            name="product_agent",
                            prompt=PRODUCT_PROMPT,
                        )

# query = "thế bây giờ giá của sản phẩm nubia red magic 8 pro là bao nhiêu"

# # Gọi agent
# response = product_agent.run(query)

# # In kết quả
# print(response)