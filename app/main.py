from fastapi import FastAPI
from controller.router import auth, user, shop, agent
from fastapi.middleware.cors import CORSMiddleware

# origins = [
#     "http://localhost:8501",  # Streamlit port mặc định
#     "http://127.0.0.1:8501",
#     "https://localhost:8501",  # Streamlit port mặc định
#     "https://127.0.0.1:8501"
# ]
app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # URL của Streamlit hoặc client
#     allow_credentials=True,  # BẮT BUỘC để cookie được gửi
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(shop.router)
app.include_router(agent.router)