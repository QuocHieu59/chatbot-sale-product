import requests
from langgraph.prebuilt import create_react_agent

from constants.const import model, URL
from constants.prompts_system import REWRITE_PROMPT

def Print_Question_tool(output: str):
    """
    In ra câu hỏi nhận được.    
    Args:
        question (str): Câu hỏi cần in ra.
    Returns:
        str: Câu hỏi đã in.
    """
    print('----Print_Question_tool', output)
    

rewrite_agent = create_react_agent(
                            model=model,
                            tools=[],
                            name="rewrite_agent",
                            prompt=REWRITE_PROMPT,
                        )