import os
from dotenv import load_dotenv
import numpy as np
from sqlalchemy import create_engine, text
import pandas as pd
import chromadb
from openai import OpenAI

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")  
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB", "chatbot_db")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

OPENAI_API_KEY = os.getenv("OPENAI_KEY")

# --- Kết nối ---
client = OpenAI(api_key=OPENAI_API_KEY)
pg_engine = create_engine(DATABASE_URL)
chroma_client = chromadb.PersistentClient("app/service/agent_service/agents/phone_db")

# --- Tạo collection ---
#collection = chroma_client.get_or_create_collection(name="phones")
def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a given text using OpenAI."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def rag_context(query: str,  number: int = 3) -> list[str]:
    """
    Lấy thông tin về 3 sản phẩm có độ tương đồng cao nhất đối với query.    
    Returns:
        str: Thông tin 3 sản phẩm điện thoại.
    """

    print('----Product', query)

    collection = chroma_client.get_collection(name="phones")
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

print(rag_context("nubia red magic 8 pro"))

# # --- Lấy dữ liệu từ PostgreSQL ---
# def fetch_all_from_table_sqlalchemy(table_name):
#     """Lấy toàn bộ dữ liệu từ một bảng trong PostgreSQL bằng SQLAlchemy"""
#     try:
#         with pg_engine.connect() as conn:
#             result = conn.execute(text(f"SELECT * FROM {table_name}"))
#             df = pd.DataFrame(result.fetchall(), columns=result.keys())
#         return df
#     except Exception as e:
#         print(f"Lỗi khi lấy dữ liệu từ {table_name}: {e}")
#         return None


# def get_embedding(text: str) -> list[float]:
#     """Generates an embedding for a given text using OpenAI."""
#     response = client.embeddings.create(
#         input=text,
#         model="text-embedding-3-large"
#     )
#     return response.data[0].embedding

# def join_string(item):
#     for i in range(len(item)):
#         name, current_price, color_options,network_sp, charge_tech, screen_size, ram, os, chip, memory, pin, sale, status, phone_company, product_specs, product_promotion= item

#         final_string = ""
#         if name:
#             final_string += f"Tên điện thoại: {name}"

#         if current_price:
#             final_string += f", có giá: {current_price}"

#         if network_sp:
#             final_string += f", hỗ trợ mạng: {network_sp}G"
            
#         if charge_tech != 0:
#             final_string += f", sạc nhanh: {charge_tech}W"
            
#         if screen_size:
#             final_string += f", kích thước màn hình: {screen_size} inch"
        
#         if ram:
#             final_string += f", RAM: {ram}"
        
#         if os:
#             final_string += f", Hệ điều hành: {os}"
        
#         if chip:
#             final_string += f", chip xử lý: {chip}"

#         if memory:
#             final_string += f", Bộ nhớ: {memory}"
        
#         if pin:
#             final_string += f", Dung lượng Pin: {pin}mAh"
        
#         if sale:
#             final_string += f", Đang giảm giá: {sale}%"

#         if status:
#             if status.lower() == "true":
#                 final_string += f", Tình trạng: còn hàng"
#             else :
#                 final_string +=  f", Tình trạng: hết hàng"
        
#         if phone_company:
#             final_string += f", Hãng điện thoại: {phone_company}"

#         if product_promotion:
#             product_promotion = product_promotion.replace("<br>", " ").replace("\n", " ")
#             final_string += f" {product_promotion}"

#         if product_specs:
#             product_specs = product_specs.replace("<br>", " ").replace("\n", " ")
#             final_string += f" {product_specs}"

#         if color_options:
#             try:
#                 color_options = color_options.replace('["', '').replace('"]', '').replace('"-"', ' - ')
#                 final_string += "có màu sắc: " + color_options
#             except (ValueError, SyntaxError):
#                 # color_options không hợp lệ, bỏ qua
#                 pass


#     return final_string

# df = fetch_all_from_table_sqlalchemy("products")

# df['information'] = df[
#     [
#      'name',
#      'current_price',
#      'color_options',
#      'network_sp',
#      'charge_tech',
#      'screen_size',
#      'ram',
#      'os',
#      'chip',
#      'memory',
#      'pin',
#      'sale',
#      'status',
#      'phone_company',
#      'product_specs',
#      'product_promotion']
#     ].astype(str).apply(join_string, axis=1)

# # --- Chuyển sang embedding bằng OpenAI ---
# # pd.set_option('display.max_colwidth', None)
# # print(df['information'].head(1))

# df = df[df['information'].notna()]
# df["embedding"] = df["information"].apply(get_embedding)

# metadatas = [{"information": row["information"]} for _, row in df.iterrows()]
# ids = [str(i) for i in df["id"].tolist()]

# collection.add(
#     ids=ids,
#     embeddings=df["embedding"].tolist(), 
#     metadatas=metadatas
# )

# print(f"Inserted {len(df)} documents into ChromaDB collection '{collection.name}'.")
