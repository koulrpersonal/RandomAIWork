from google.adk.agents.llm_agent import Agent, LlmAgent
from google.adk.tools import google_search
from . import instructions

# --- The LLM Agent which acts as ETF advisor ---
ETF_Advisor_Agent = LlmAgent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='You are Financial adivce agent which can give advise on ETFs. Your job is to answer the questions related to ETFs',
    instruction=instructions.ETF_Agent_PROMPT,
    tools=[google_search] ,
)

# --- Assinging an agent as root agent. This agent is then instantiated using init file ---
root_agent =  ETF_Advisor_Agent


