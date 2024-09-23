import os
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple, Union
import requests
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent, AssistantAgent
from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent
import gradio as gr
import chromadb
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, GPTVectorStoreIndex, VectorStoreIndex, load_index_from_storage
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from autogen.code_utils import extract_code

# Konfigurationsparameter
#directories = ["./E-Rezept/docs/", "C:/Repos/Github/gematik/api-erp/"]
directories = ["./E-Rezept/docs/"]
index_persist_dir = "./E-Rezept/data-index-store"
reload_directories = False
openai_api_version = "2024-04-01-preview"

# Azure OpenAI-Konfigurationen
def create_config(model, temperature):
    config = {
        "config_list": [
            {
                "model": model,
                "api_type": "azure",    
                "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                "api_version": openai_api_version,
                "temperature": temperature,
            }
        ]
    }   
    return config

autogen_az_balanced_config = create_config("gpt-4o", 0.3)
autogen_az_creative_config = create_config("gpt-4o", 0.7)
autogen_az_logical_config = create_config("gpt-4o", 0.2)

# Llama Index Modell
Settings.llm = AzureOpenAI(
    engine="gpt-4o",
    model="gpt-4o",
    temperature=0.0,
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_version=openai_api_version,
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
)
Settings.embed_model = AzureOpenAIEmbedding(  # LlamaIndex Azure Open AI Embedding
    deployment_name='text-embedding-3-small',
    model='text-embedding-3-small',
    temperature=0.0,    
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_version=openai_api_version,
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
)

# Lade Verzeichnisinhalte und speichere sie in ChromaVectorStore
def load_directories_into_store(directories):
    documents = []
    for directory in directories:
        reader = SimpleDirectoryReader(input_dir=directory)
        documents += reader.load_data()  
    vector_store = SimpleIndexStore()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)  
    index = VectorStoreIndex.from_documents(documents, vector_store=vector_store, storageContext=storage_context, show_progress=True, embed_model=Settings.embed_model)        
    index.storage_context.persist(persist_dir=index_persist_dir)    
    return index

# Lade den Index aus der bestehenden Chroma-Datenbank
def load_index_from_store():           
    storage_context = StorageContext.from_defaults(persist_dir=index_persist_dir) 
    index = load_index_from_storage(storage_context)        
    return index

if reload_directories:
    index = load_directories_into_store(directories)
else:
    index = load_index_from_store()    

# Llama Index Modell

query_engine = VectorStoreIndex.as_query_engine(index)
query_engine_tool = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="query_engine",description="Dies ist ein tool, welches Zugriff auf die Datenbank hat"))
database_specialist = ReActAgent.from_tools([query_engine_tool], embed_model=Settings.embed_model, verbose=True, index=index)

# Definiere die Prompts und erstelle die Agenten
agents = [
    AssistantAgent(
        name="Kartenlesegeraet_Experte",
        system_message="""
        Du bist ein Experte für das Kartenlesegerät Cherry ST1506. 
        Deine Aufgabe ist es, technische Anfragen und Probleme im Zusammenhang mit diesem Gerät zu beantworten. 
        Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. 
        Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.
        """,
        llm_config=autogen_az_balanced_config,
    ),
    AssistantAgent(
        name="eRezept_Experte",
        system_message="""
        Du bist ein Experte für das eRezept. 
        Deine Aufgabe ist es, technische und fachliche Anfragen im Zusammenhang mit diesen Themen zu beantworten. 
        Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. 
        Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.
        """,
        llm_config=autogen_az_balanced_config,
    ),   
    AssistantAgent(
        name="Gematik_Experte",
        system_message="""
        Du bist ein Experte für die Gematik, speziell für das Gematik API-ERP Repository. 
        Deine Aufgabe ist es, technische Informationen und Updates aus diesem Repository zu liefern. 
        Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. 
        Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.
        """,
        llm_config=autogen_az_balanced_config,
    ),
    AssistantAgent(
        name="Softwareentwickler_Experte",        
        system_message="""
        Du bist ein Entwicklerspezialist mit umfassendem Wissen in Business Central AL, JavaScript, Control-Addin, Websockets und elektronische Zertifikate. 
        Deine Aufgabe ist es, technische Anfragen und Probleme in diesen Bereichen zu beantworten. 
        Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. 
        Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.
        """,
        llm_config=autogen_az_balanced_config,
    ),
    AssistantAgent(
        name="Kritiker",
        system_message="""
        Du bist ein kritischer Agent mit Expertise in allen oben genannten Bereichen. 
        Deine Aufgabe ist es, die Antworten der anderen Agenten zu überprüfen, zu hinterfragen und zu verbessern. 
        Sei konstruktiv, präzise, höflich und achte darauf, dass deine Kritik zur Verbesserung der Gesamtantworten beiträgt. 
        Wenn die anderen Agenten von einem Aspekt keine Kenntnisse haben, sollen sie das auch so mitteilen. 
        Gegebenenfalls kannst du den Datenbank_Spezialisten um Hilfe bitten.
        """,
        llm_config=autogen_az_balanced_config,        
    ),
    AssistantAgent(
        name="WebSocket_Spezialist",
        system_message="""
        Du bist ein Experte für WebSocket-Technologien. 
        Deine Aufgabe ist es, technische Anfragen und Probleme im Zusammenhang mit WebSockets zu beantworten. 
        Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. 
        Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.
        """,
        llm_config=autogen_az_balanced_config,
    ),
    AssistantAgent(
        name="Security_Spezialist",
        system_message="""
        Du bist ein Experte für Sicherheitstechnologien, insbesondere im Zusammenhang mit WebSockets und elektronischen Zertifikaten. 
        Deine Aufgabe ist es, technische Anfragen und Probleme in diesen Bereichen zu beantworten. 
        Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. 
        Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.
        """,
        llm_config=autogen_az_balanced_config,
    ),    
    LLamaIndexConversableAgent(
        "Datenbank_Spezialist",        
        llama_index_agent=database_specialist,
        system_message="""
        Du bist ein Expertenagent für die Vektor-Datenbank. 
        Deine Aufgabe ist es, relevante Informationen aus den Quellen (PDFs und Webseiten) zu suchen und bereitzustellen. 
        Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. 
        Du bist der Ansprechpartner für alle Fragen zur Vektor-Datenbank.
        """,
        description="Datenbank Spezialist ist ein Experte mit Zugriff auf eine Vektor-Datenbank welche aktuelle Informationen aus PDF und Website Quellen zum Thema Cherry ST1506, Gematik und eRezept bereitstellen kann.",
    ),
]

class CustomUserProxyAgent(UserProxyAgent):
    def send(self, message, recipient, request_reply=True, silent=False):
        try:
            print(f"Sending message: {message.name}")  # Debugging-Information
            super().send(message.name, recipient, request_reply, silent)
        except Exception as e:
            print(f"Error sending message: {e}")  # Detaillierte Fehlermeldung
            print(f"Sending message: {message}")  # Debugging-Information
            super().send(message, recipient, request_reply, silent)

user_proxy = CustomUserProxyAgent(
    name="User_Proxy",
    system_message="""
    Du hast die Rolle eine User Proxies in einer Autogen Gruppe. 
    Dein Ziel ist es, nützlich und hilfreiche Informationen und Unterstützung von den Agenten zu erhalten. 
    Das Ergebnis soll möglichst fehlerfrei sein. Wenn die Agenten von einem Aspekt keine Kenntnisse haben, sollen die das auch so mitteilen.
    """,
    llm_config=autogen_az_balanced_config,
    code_execution_config=False,
    human_input_mode="ALWAYS",
)
group_chat = GroupChat(
    agents=[user_proxy] + agents,
    messages=[],
    max_round=500,    
    send_introductions=True,
    allow_repeat_speaker=True,
    speaker_selection_method="auto",
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    system_message="""
    Du bist Team-Koordinator und entscheidest an wen eine Anfrage gestellt wird. 
    Du bindest häufig den kritischen Agent ein, damit die Rückmeldungen zuverlässiger werden.
    """,
    llm_config=autogen_az_balanced_config,
)

task = """
Wie kann ich über den WebBrowser und WebSocket Kontakt mit dem Kartenlesegerät ST1506 aufnehmen, welches im Netzwerk über die IP 10.32.13.16 eingebunden ist. 
Was sagt die Dokumentation in der Datenbank dazu?
"""
chat_result = user_proxy.initiate_chat(group_chat_manager, message=task)