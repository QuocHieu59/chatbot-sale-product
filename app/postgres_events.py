import psycopg2
import select
import pandas as pd
import chromadb
from sqlalchemy import create_engine, text
from openai import OpenAI

from database.connection.postgresql import DATABASE_URL
from constants.const import OPENAI_KEY, COLLECTION_NAME, CHROMA_CLIENT_PATH
from utils.hash import get_text_hash
from utils.agent import join_string, get_embedding

chroma_client = chromadb.PersistentClient(CHROMA_CLIENT_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
pg_engine = create_engine(DATABASE_URL)
openai_client = OpenAI(api_key=OPENAI_KEY)

def fetch_all_from_table_sqlalchemy(table_name: str) -> pd.DataFrame:
    """Lấy toàn bộ dữ liệu từ PostgreSQL."""
    try:
        with pg_engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ {table_name}: {e}")
        return pd.DataFrame()

def listen_postgres_events():
    conn = psycopg2.connect("dbname=chatbot_db user=postgres password=ni456702 host=localhost")
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("LISTEN product_changes;")
    print("Listening for product_changes events...")
    try:
        while True:
            if select.select([conn], [], [], 5) == ([], [], []):
                continue
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                print("Có thay đổi:", notify.payload)
                sync_products_to_chroma()  # Gọi lại sync
    except Exception as e:
        print("Listener error:", e)


def sync_products_to_chroma():
    print("Đang đồng bộ dữ liệu từ PostgreSQL → Chroma...")
    print("Collection name:", collection.name)
    print("Collection count:", collection.count())

    # 1️ Lấy dữ liệu từ Postgres
    df = fetch_all_from_table_sqlalchemy("products")
    if df.empty:
        print("Không có dữ liệu trong bảng products.")
        return

    # 2️ Tạo cột information
    info_cols = [
        'name',
        'current_price',
        'color_options',
        'network_sp',
        'charge_tech',
        'screen_size',
        'ram',
        'os',
        'chip',
        'memory',
        'pin',
        'sale',
        'status',
        'phone_company',
        'product_specs',
        'product_promotion'
    ]
    df['information'] = df[info_cols].astype(str).apply(join_string, axis=1)
    df = df[df['information'].notna()]

    # 3️ Tạo hash cho từng dòng
    df["current_hash"] = df["information"].apply(get_text_hash)

    # 4️ Lấy danh sách ID trong Chroma
    chroma_data = collection.get(include=["metadatas"])
    chroma_ids = set(chroma_data["ids"])

    # 5️ Xác định phần thay đổi hoặc mới
    if "embedding_hash" not in df.columns:
        df["embedding_hash"] = None
    changed_df = df[df["current_hash"] != df["embedding_hash"]]
    postgres_ids = set(df["id"].astype(str))
    new_ids = set(changed_df["id"].astype(str))

    # 6️ Xác định bản ghi bị xóa
    deleted_ids = list(chroma_ids - postgres_ids)

    print(f"{len(changed_df)} bản ghi cần embedding lại.")
    print(f"{len(deleted_ids)} bản ghi cần xóa khỏi Chroma.")

    # 7️ Xóa bản ghi bị xóa khỏi Chroma
    if deleted_ids:
        collection.delete(ids=deleted_ids)

    # 8️ Thêm hoặc cập nhật bản ghi mới/thay đổi
    if not changed_df.empty:
        changed_df["embedding"] = changed_df["information"].apply(get_embedding)
        metadatas = [{"information": row["information"]} for _, row in changed_df.iterrows()]
        ids = [str(i) for i in changed_df["id"].tolist()]
        # print("IDs:", ids[:3])
        # print("Embeddings shape:", len(changed_df["embedding"].iloc[0]))
        # print("Metadata sample:", metadatas[0])

        collection.upsert(
            ids=ids,
            embeddings=changed_df["embedding"].tolist(),
            metadatas=metadatas
        )
        # print("✅ Đã thêm vào Chroma:", len(ids))
        # print("📊 Tổng số bản ghi:", collection.count())
        # 9️ Cập nhật hash vào Postgres
        with pg_engine.begin() as conn:
            for _, row in changed_df.iterrows():
                conn.execute(
                    text("UPDATE products SET embedding_hash = :hash WHERE id = :id"),
                    {"hash": row["current_hash"], "id": row["id"]}
                )
        # doc = collection.get(ids=["2cdeb491-0564-4542-b4e1-47162a023ef4"], include=["metadatas", "embeddings"])
        # print(doc)

    print("✅ Đồng bộ hoàn tất!")