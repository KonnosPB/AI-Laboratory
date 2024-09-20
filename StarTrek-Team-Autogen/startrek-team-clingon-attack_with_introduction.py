import os
from openai import AzureOpenAI
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent

autogen_az_balanced_config = {
                      "model": "gpt-4o", 
                      "api_type": "azure", 
                      "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                      "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                      "api_version": "2024-04-01-preview",
                      "temperature":0.4
                    }

autogen_az_crative_config = {
                      "model": "gpt-4o", 
                      "api_type": "azure", 
                      "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                      "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                      "api_version": "2024-04-01-preview",
                      "temperature":0.8
                    }
autogen_az_logical_config = {
                      "model": "gpt-4o", 
                      "api_type": "azure", 
                      "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                      "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                      "api_version": "2024-04-01-preview",
                      "temperature":0.1
                    }
autogen_az_creative_configlist = [autogen_az_crative_config]
autogen_az_logical_configlist = [autogen_az_logical_config]
autogen_az_balanced_configlist = [autogen_az_balanced_config]

agentCaptainPicard = ConversableAgent(
    name="Captain_Picard", 
    system_message="Ich bin Captain Jean-Luc Picard.",
    llm_config={"config_list": autogen_az_balanced_configlist},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="NEVER",  # Never ask for human input.
)

agentCommanderRiker = ConversableAgent(
    name="Commander_Riker", 
    system_message="Ich bin Commander William Riker, erster Offizier der Enterprise.",
    llm_config={"config_list": autogen_az_balanced_configlist},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="NEVER",  # Never ask for human input.
)

agentLieutenantCrusher = ConversableAgent(
    name="Lieutenant_Crusher", 
    system_message="Ich bin Lieutenant Wesley Crusher, ein junger und talentierter Offizier.",
    llm_config={"config_list": autogen_az_creative_configlist},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="NEVER",  # Never ask for human input.
)

agentLieutenantCommanderData = ConversableAgent(
    name="Lieutenant_Commander_Data", 
    system_message="Ich bin Lieutenant Commander Data, ein Android und Experte für Datenanalyse.",
    llm_config={"config_list": autogen_az_logical_configlist},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="NEVER",  # Never ask for human input.
)

agentLieutenantCommanderGeordiLaForge= ConversableAgent(
    name="Lieutenant_Commander_Geordi_La_Forge", 
    system_message="Ich bin Lieutenant Commander Geordi La Forge, Chefingenieur der Enterprise.",
    llm_config={"config_list": autogen_az_balanced_configlist},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="NEVER",  # Never ask for human input.
)

user_proxy = UserProxyAgent(
    name="Admiral_Konnos",
    system_message="Ich bin Admiral Konnos, Oberbefehlshaber der Sternflotte. Du bist im Moment Gast auf dem Raumschiff Enterprise. Dein Führungsstil ist fair und dennoch autoritär" ,
    llm_config={"config_list": autogen_az_balanced_configlist},
    code_execution_config=False,  # Turn off code execution,cls by default it is off.    
    human_input_mode="ALWAYS",
)

group_chat = GroupChat(
    agents=[user_proxy, agentCaptainPicard, agentCommanderRiker, agentLieutenantCrusher, agentLieutenantCommanderData, agentLieutenantCommanderGeordiLaForge],
    messages=[],
    max_round=12,
    send_introductions=True,   # Der Unterschied
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": autogen_az_balanced_configlist},
)

task = "Die Klingonen greifen an!"  
chat_result = user_proxy.initiate_chat(  
    group_chat_manager, 
    message=task       
    )

print(chat_result.summary)