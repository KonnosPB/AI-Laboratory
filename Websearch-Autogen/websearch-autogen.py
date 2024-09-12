import os
from openai import AzureOpenAI
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
import autogen
from autogen.agentchat.contrib.web_surfer import WebSurferAgent 

bing_api_key = os.environ["BING_API_KEY"]

# gpt_config = {
#                 "model": "gpt-4o", 
#                 "timeout": 600,
#                 "api_type": "azure", 
#                 "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
#                 "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
#                 "api_version": "2024-04-01-preview",
#                 "temperature":0.4
#              }



llm_config = {
    "timeout": 600,
    "cache_seed": 44,  # change the seed for different trials
    "api_type": "azure", 
    "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
    "api_version": "2024-04-01-preview",
    "temperature": 0,
}

llm_configlist = [llm_config]

summarizer_llm_config = {
    "timeout": 600,
    "cache_seed": 44,  # change the seed for different trials
    "api_type": "azure", 
    "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
    "api_version": "2024-04-01-preview",
    "temperature": 0,
}

web_surfer = WebSurferAgent(
    "web_surfer",
    llm_config=llm_config,
    summarizer_llm_config=summarizer_llm_config,
    browser_config={"viewport_size": 4096, "bing_api_key": bing_api_key},
)

user_proxy = UserProxyAgent(
    "user_proxy",
    llm_config=llm_config,
    human_input_mode="NEVER",
    code_execution_config=False,
    default_auto_reply="",
    is_termination_msg=lambda x: True,
)

task = "Search the web for information about Microsoft AutoGen"

group_chat = GroupChat(
    agents=[user_proxy, web_surfer],
    messages=[],
    allow_repeat_speaker=False,
    send_introductions=True,    
    speaker_selection_method="auto",
    max_round=12,
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,    
    llm_config={"config_list": llm_configlist},
)


chat_result = user_proxy.initiate_chat(  
    group_chat_manager, message=task)

