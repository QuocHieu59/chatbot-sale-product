import os
from langchain_openai import ChatOpenAI
from  dotenv import load_dotenv
load_dotenv()
PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH")
PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH")
CHROMA_CLIENT_PATH = os.getenv("CHROMA_CLIENT_PATH")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
URL = os.getenv("AGENT_URL")
ALGORITHM = "RS256"
with open(PRIVATE_KEY_PATH, "r") as f:
    SECRET_KEY = f.read()  
with open(PUBLIC_KEY_PATH, "r") as f:
    PUBLIC_KEY = f.read()
OPENAI_KEY = os.getenv("OPENAI_KEY")
Model_Name = "gpt-4o-mini"
Model_highcost = "gpt-4o"
Model_SQL = "gpt-4o"
Model_embedding = "text-embedding-3-large"
DEFAULT_AGENT = "supervisor-agent"
model = ChatOpenAI(
    model=Model_Name,    
    api_key = OPENAI_KEY,
)