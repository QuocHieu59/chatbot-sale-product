from fastapi import FastAPI
from threading import Thread
import time

from postgres_events import listen_postgres_events
from controller.router import auth, user, shop, agent, product, order, message
from fastapi.middleware.cors import CORSMiddleware
# origins = [
#     "http://localhost:8501",  # Streamlit port mặc định
#     "http://127.0.0.1:8501",
#     "https://localhost:8501",  # Streamlit port mặc định
#     "https://127.0.0.1:8501"
# ]
app = FastAPI(debug=True)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # URL của Streamlit hoặc client
#     allow_credentials=True,  # BẮT BUỘC để cookie được gửi
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

listener_thread = Thread(target=listen_postgres_events, daemon=True)
listener_thread.start()
print("🔊 Listener đang chạy... nhấn Ctrl + C để dừng.")
time.sleep(1)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(shop.router)
app.include_router(agent.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(message.router)