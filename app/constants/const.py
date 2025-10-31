import os
from langchain_openai import ChatOpenAI
PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH")
PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
URL = os.getenv("AGENT_URL")
ALGORITHM = "RS256"
with open(PRIVATE_KEY_PATH, "r") as f:
    SECRET_KEY = f.read()  
with open(PUBLIC_KEY_PATH, "r") as f:
    PUBLIC_KEY = f.read()
OPENAI_KEY = os.getenv("OPENAI_KEY")
Model_Name = "gpt-4.1-mini"
DEFAULT_AGENT = "supervisor-agent"
model = ChatOpenAI(
    model=Model_Name,    
    api_key = OPENAI_KEY,
    streaming=True          
)