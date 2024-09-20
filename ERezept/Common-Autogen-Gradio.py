import os
import hashlib
import json
import requests
from bs4 import BeautifulSoup
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent
import gradio as gr
import chromadb
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, ServiceContext
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core.agent import ReActAgent
from git import Repo

# Konfigurationsparameter
directories = ["./pdfs/", "C:/Repos/Github/gematik/api-erp/"]
hash_file = "./hashes.json"
chroma_db_file = "./erezept.chromadb"

# Azure OpenAI-Konfigurationen
autogen_az_balanced_config = {
    "model": "gpt-4o",
    "api_type": "azure",
    "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
    "api_version": "2024-04-01-preview",
    "temperature": 0.4
}

autogen_az_creative_config = {
    "model": "gpt-4o",
    "api_type": "azure",
    "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
    "api_version": "2024-04-01-preview",
    "temperature": 0.8
}

autogen_az_logical_config = {
    "model": "gpt-4o",
    "api_type": "azure",
    "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
    "api_version": "2024-04-01-preview",
    "temperature": 0.1
}

# create client and a new collection
chroma_client = chromadb.PersistentClient(path=chroma_db_file)
chroma_collection = chroma_client.get_or_create_collection("erezept")

autogen_az_creative_configlist = [autogen_az_creative_config]
autogen_az_logical_configlist = [autogen_az_logical_config]
autogen_az_balanced_configlist = [autogen_az_balanced_config]

# Llama Index Modell
Settings.llm = AzureOpenAI(
    engine="gpt-4o",
    model="gpt-4o",
    temperature=0.0,
    api_key=os.environ.get("OPENAPI_API_KEY", ""),
)
Settings.embed_model = AzureOpenAIEmbedding(  # LlamaIndex Azure Open AI Embedding
    model='text-embedding-3-large',
    temperature=0.0,
    api_key=os.environ.get("OPENAPI_API_KEY", ""),
)
database_specialist = ReActAgent.from_tools(llm=Settings.llm, max_iterations=10, verbose=True)


# Funktion zur Berechnung des Hashwertes einer Datei
def calculate_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


# Lade Hashwerte aus Datei
def load_hashes():
    if os.path.exists(hash_file):
        with open(hash_file, 'r') as f:
            return json.load(f)
    return {}


# Speichere Hashwerte in Datei
def save_hashes(hashes):
    with open(hash_file, 'w') as f:
        json.dump(hashes, f)


# Lade Verzeichnisinhalte in LlamaIndex und aktualisiere den Index
def load_directory(directories):
    current_hashes = load_hashes()
    new_hashes = {}
    files_to_reindex = []

    # Überprüfe und speichere neue/aktualisierte Dateien
    for directory in directories:
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_hash = calculate_file_hash(file_path)
                new_hashes[filename] = file_hash

                # Wenn Datei neu oder geändert ist, zur Reindexierung hinzufügen
                if current_hashes.get(filename) != file_hash:
                    files_to_reindex.append(file_path)

    # Erstelle den Index nur mit neuen/aktualisierten Dateien
    if files_to_reindex:
        reader = SimpleDirectoryReader(files_to_reindex)
        documents = reader.load_data()
        index = VectorStoreIndex.from_documents(documents)
        save_hashes(new_hashes)
    else:
        index = VectorStoreIndex([])

    return index


# Pull Git-Repository und aktualisiere den Index
def update_git_repo(repo_path):
    if os.path.exists(repo_path):
        repo = Repo(repo_path)
        repo.remotes.origin.pull()
    else:
        Repo.clone_from("https://github.com/gematik/api-erp", repo_path)


# Initiales Laden der Verzeichnisse und Erstellen des Index
update_git_repo("C:/Repos/Github/gematik/api-erp/")
index = load_directory(directories)

# Definiere die Prompts und erstelle die Agenten
agents = [
    ConversableAgent(
        name="Kartenlesegerät_Agent",
        system_message="Du bist ein Expertenagent für das Kartenlesegerät Cherry ST1506. Deine Aufgabe ist es, technische Anfragen und Probleme im Zusammenhang mit diesem Gerät zu beantworten. Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. Du bist der Ansprechpartner für alle Fragen rund um das Cherry ST1506 Kartenlesegerät.",
        llm_config={"config_list": autogen_az_balanced_configlist},
    ),
    ConversableAgent(
        name="Gematik_eRezept_Agent",
        system_message="Du bist ein Expertenagent für Gematik und eRezept. Deine Aufgabe ist es, technische und fachliche Anfragen im Zusammenhang mit diesen Themen zu beantworten. Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. Du bist der Ansprechpartner für alle Fragen rund um Gematik und eRezept.",
        llm_config={"config_list": autogen_az_balanced_configlist},
    ),
    ConversableAgent(
        name="Chat_Koordinator_Agent",
        system_message="Du bist der Agent, der die Chatkommunikation koordiniert. Deine Aufgabe ist es, Anfragen zu sammeln, an die entsprechenden Spezialisten weiterzuleiten und deren Antworten zusammenzuführen. Sei präzise, höflich und achte darauf, dass die Kommunikation klar und organisiert ist. Du bist der Ansprechpartner für die Koordination der Expertenantworten.",
        llm_config={"config_list": autogen_az_balanced_configlist},
    ),
    ConversableAgent(
        name="Gematik_GitHub_Agent",
        system_message="Du bist ein Expertenagent für die Recherche auf GitHub, speziell für das Gematik API-ERP Repository. Deine Aufgabe ist es, technische Informationen und Updates aus diesem Repository zu liefern. Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. Du bist der Ansprechpartner für alle Fragen rund um das Gematik API-ERP Repository.",
        llm_config={"config_list": autogen_az_balanced_configlist},
    ),
    ConversableAgent(
        name="Entwickler_Agent",
        system_message="Du bist ein Entwicklerspezialist mit umfassendem Wissen in Business Central AL, JavaScript, Control-Addin, Websockets und elektronische Zertifikate. Deine Aufgabe ist es, technische Anfragen und Probleme in diesen Bereichen zu beantworten. Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. Du bist der Ansprechpartner für alle Entwicklerfragen in diesen Bereichen.",
        llm_config={"config_list": autogen_az_balanced_configlist},
    ),
    ConversableAgent(
        name="Kritischer_Agent",
        system_message="Du bist ein kritischer Agent mit Expertise in allen oben genannten Bereichen. Deine Aufgabe ist es, die Antworten der anderen Agenten zu überprüfen, zu hinterfragen und zu verbessern. Sei konstruktiv, präzise, höflich und achte darauf, dass deine Kritik zur Verbesserung der Gesamtantworten beiträgt. Du bist der Ansprechpartner für die Qualitätssicherung der Expertenantworten.",
        llm_config={"config_list": autogen_az_logical_configlist},
    ),
    LLamaIndexConversableAgent(
        "Datenbank_Agent",
        llama_index_agent=database_specialist,
        system_message="Du bist ein Expertenagent für die Vektor-Datenbank. Deine Aufgabe ist es, relevante Informationen aus den Quellen (PDFs und Webseiten) zu suchen und bereitzustellen. Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. Du bist der Ansprechpartnerfür alle Fragen zur Vektor-Datenbank.",
        description="Ein Experte mit Zugriff auf eine Vektor-Datenbank welche aktuelle Information aus PDF und Website Quellen bereitstellen kann.",
    )
]

user_proxy = UserProxyAgent(
    name="User_Proxy",
    system_message="Du bist der Benutzer. Dein Ziel ist es, Informationen und Unterstützung von den Agenten zu erhalten.",
    llm_config={"config_list": autogen_az_balanced_configlist},
    code_execution_config=False,
    human_input_mode="TERMINATE",
)

group_chat = GroupChat(
    agents=[user_proxy] + agents,
    messages=[],
    max_round=500,
    send_introductions=True,
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": autogen_az_balanced_configlist},
)

def gradio_interface(query):
    chat_result = user_proxy.initiate_chat(group_chat_manager, message=query)
    return chat_result.summary

# Gradio App
iface = gr.Interface(fn=gradio_interface, inputs="text", outputs="text", title="Expertengruppe KI")

# Starte die Gradio App
iface.launch()

