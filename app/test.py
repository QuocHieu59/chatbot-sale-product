import os
from dotenv import load_dotenv
import numpy as np
from sqlalchemy import create_engine, text
import re
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
collection = chroma_client.get_or_create_collection(name="phones")
def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a given text using OpenAI."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def rag_context(query: str, number: int = 3) -> list[dict]:
    """
    Lấy thông tin về 3 sản phẩm có độ tương đồng cao nhất đối với query.
    Returns:
        list[dict]: Mỗi dict chứa 'id' và 'information' của document
    """
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

def cut_info_before_comma(info_list) -> list[str]:
    
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
    
result = rag_context('nubia red magic 8 pr',1)

print(result)
print(cut_info_before_comma(result[0]['information']))
# --- Lấy dữ liệu từ PostgreSQL ---
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

# def format_color(color_str):
#     txt = color_str

#     # Bỏ ký tự [, ], {, }
#     txt = txt.replace("[", "").replace("]", "")
#     txt = txt.replace("{", "").replace("}", "")

#     # Bỏ dấu nháy đơn
#     txt = txt.replace("'", "")

#     # Đổi dấu :  thành " - số lượng "
#     txt = txt.replace(":", " - số lượng ")

#     # Đổi dấu phẩy phân tách dict thành dấu chấm phẩy
#     txt = txt.replace(", ", "; ")

#     return txt

# def join_string(item):
#     for i in range(len(item)):
#         name, current_price, color_options,network_sp, charge_tech, screen_size, ram, os, chip, memory, pin, sale, status, phone_company, product_specs, product_promotion= item

#         final_string = ""
#         if name:
#             final_string += f"Tên điện thoại: {name}"

#         if current_price:
#             final_string += f", có giá: {current_price}"
        
#         if ram:
#             final_string += f", RAM: {ram}"

#         if memory:
#             final_string += f", Bộ nhớ: {memory}"
        
#         if color_options:
#             try:
#                 result = format_color(color_options)
#                 final_string += ", Có màu sắc và số lượng tương ứng: " + result
#             except (ValueError, SyntaxError):
#                 # color_options không hợp lệ, bỏ qua
#                 pass

#         if network_sp:
#             final_string += f", hỗ trợ mạng: {network_sp}G"
            
#         if charge_tech != 0:
#             final_string += f", sạc nhanh: {charge_tech}W"
            
#         if screen_size:
#             final_string += f", kích thước màn hình: {screen_size} inch"
        
#         if os:
#             final_string += f", Hệ điều hành: {os}"
        
#         if chip:
#             final_string += f", chip xử lý: {chip}"

        
#         if pin:
#             final_string += f", Dung lượng Pin: {pin}mAh"
        
#         if sale:
#             final_string += f", Đang giảm giá: {sale}%"

#         if status:
#             if status.lower() != "true":
#                 final_string += f", Tình trạng: hết hàng"
        
#         if phone_company:
#             final_string += f", Hãng điện thoại: {phone_company}"

#         if product_promotion:
#             product_promotion = product_promotion.replace("<br>", " ").replace("\n", " ")
#             final_string += f" {product_promotion}"

#         if product_specs:
#             product_specs = product_specs.replace("<br>", " ").replace("\n", " ")
#             final_string += f" {product_specs}."

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
