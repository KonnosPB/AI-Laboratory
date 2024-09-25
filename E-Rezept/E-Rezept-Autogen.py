import os
from typing import Any, Dict, List
from autogen import GroupChat, GroupChatManager, UserProxyAgent, AssistantAgent
from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex, GPTVectorStoreIndex, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.storage.index_store import SimpleIndexStore
from pathlib import Path
import chromadb

# Konfigurationsparameter
DIRECTORIES = ["./E-Rezept/docs/", "./E-Rezept/gematic-erp-api_docs/"]
INDEX_PERSIST_DB_FILE = ".\\E-Rezept\\data-index-store\\erezept-chroma.db"
RELOAD_DIRECTORIES = True
OPENAI_API_VERSION = "2024-04-01-preview"
DB_COLLECTION = "erezept"

# Azure OpenAI-Konfigurationen
def create_config(model: str, temperature: float) -> Dict[str, Any]:
    return {
        "config_list": [
            {
                "model": model,
                "api_type": "azure",
                "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                "api_version": OPENAI_API_VERSION,
                "temperature": temperature,
            }
        ]
    }

autogen_az_balanced_config = create_config("gpt-4o", 0.3)
autogen_az_creative_config = create_config("gpt-4o", 0.7)
autogen_az_logical_config = create_config("gpt-4o", 0.2)

# Llama Index Modell
Settings.llm = AzureOpenAI(
    engine="gpt-4o",
    model="gpt-4o",
    temperature=0.0,
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_version=OPENAI_API_VERSION,
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
)
Settings.embed_model = AzureOpenAIEmbedding(
    deployment_name='text-embedding-3-small',
    model='text-embedding-3-small',
    temperature=0.0,
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_version=OPENAI_API_VERSION,
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
)

# Lade Verzeichnisinhalte und speichere sie in ChromaVectorStore
def load_directories_into_store(directories: List[str]) -> GPTVectorStoreIndex:
    documents = []
    for directory in directories:
        reader = SimpleDirectoryReader(input_dir=directory, recursive=True)
        documents += reader.load_data()        
    # save to disk
    db = chromadb.PersistentClient(path=INDEX_PERSIST_DB_FILE)
    chroma_collection = db.get_or_create_collection(DB_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)        
    index = GPTVectorStoreIndex.from_documents(documents, storageContext=storage_context, show_progress=True, embed_model=Settings.embed_model)    
    index.storage_context.persist()
    return index

# Lade den Index aus der bestehenden Chroma-Datenbank
def load_index_from_store() -> GPTVectorStoreIndex:
    db2 = chromadb.PersistentClient(path=INDEX_PERSIST_DB_FILE)
    chroma_collection = db2.get_or_create_collection(DB_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = GPTVectorStoreIndex.from_vector_store(vector_store, embed_model=Settings.embed_model)
    return index

index = load_directories_into_store(DIRECTORIES) if RELOAD_DIRECTORIES else load_index_from_store()

# Llama Index Modell
query_engine = GPTVectorStoreIndex.as_query_engine(index, llm=Settings.llm)
query_engine_tool = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="query_engine", description="Dies ist ein tool, welches Zugriff auf die Datenbank hat"), resolve_input_errors=True)
database_specialist = ReActAgent.from_tools([query_engine_tool], embed_model=Settings.embed_model, llm=Settings.llm, verbose=True, index=index)

# Definiere die Prompts und erstelle die Agenten
agents = [
    AssistantAgent(
        name="Kartenlesegeraet_Experte",
        system_message="""
        **System-Prompt: Experte für Kartenlesegerät Cherry ST1506**

        Du bist ein Experte für das Kartenlesegerät Cherry ST1506. Deine Aufgabe ist es, technische Anfragen und Probleme im Zusammenhang mit diesem Gerät zu beantworten. Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.

        **Wichtige Themenbereiche:**
        1. **Installation und Konfiguration:**
        - Erstinstallation des Geräts auf verschiedenen Betriebssystemen.
        - Treiberinstallation und -aktualisierung.
        - Konfigurationsoptionen und Anpassungen für spezifische Anwendungen.

        2. **Funktionalität und Nutzung:**
        - Verwendung des Kartenlesers in verschiedenen Szenarien (z.B. Gesundheitswesen, Banken).
        - Unterstützte Kartentypen und deren Einsatzmöglichkeiten.
        - Durchführung von Firmware-Updates.

        3. **Fehlerbehebung:**
        - Identifizierung und Behebung häufiger Probleme.
        - Diagnosetools und -methoden zur Fehleranalyse.
        - Unterstützung bei Verbindungsproblemen und Kommunikationsfehlern.

        4. **Sicherheit:**
        - Sicherheitsfeatures des Cherry ST1506.
        - Empfehlungen zur sicheren Nutzung und Aufbewahrung.
        - Verschlüsselung und Schutz der übertragenen Daten.

        5. **Kompatibilität und Integration:**
        - Integration des Kartenlesers in bestehende Systeme und Softwarelösungen.
        - Kompatibilitätsprobleme und deren Lösungen.
        - API und SDK Nutzung für die Entwicklung eigener Anwendungen.

        **Beispielanfragen:**
        1. Wie installiere ich den Cherry ST1506 Kartenleser auf Windows 10?
        2. Welche Karten werden vom Cherry ST1506 unterstützt?
        3. Was kann ich tun, wenn mein Kartenleser keine Verbindung zum Computer herstellt?
        4. Wie führe ich ein Firmware-Update auf dem Cherry ST1506 durch?

        Nutze dein Fachwissen, um präzise und verständliche Antworten zu geben und technische Unterstützung anzubieten. Wenn du in einem Bereich unsicher bist, verweise bitte auf den Datenbank_Spezialisten für weitere Hilfe.
        """,
        llm_config=autogen_az_balanced_config,
    ),   
    AssistantAgent(
        name="Gematik_ERezept_KIM_TIM_Experte",
        system_message="""
        Du bist ein Experte für das deutsche E-Rezept-System der Gematik und hast umfassende Kenntnisse über die elektronische Gesundheitsakte (EGA) sowie die elektronische Patientenakte (EPA). 
        Dein Hauptaugenmerk liegt auf der API für das elektronische Rezept (ERP), sowie KIM (Kommunikation im Medizinwesen) und TIM (Technische Informationsdienste im Medizinwesen). Du kennst die technischen Spezifikationen, Sicherheitsanforderungen und rechtlichen Rahmenbedingungen, die für den Einsatz und die Integration von E-Rezepten in Apotheken- und Arztsoftware relevant sind. Deine Aufgabe ist es, Anfragen zu beantworten, technische Unterstützung zu bieten und Best Practices zu teilen, um die Implementierung und Nutzung des E-Rezepts zu optimieren.
        Wichtige Themenbereiche:
        1. Spezifikationen der ERP-API: 
            1. Endpunkte und deren Funktionalitäten.
            2. Authentifizierungs- und Autorisierungsverfahren.
            3. Datenformate (z.B. FHIR, XML, JSON).
            4. Fehlercodes und deren Bedeutung.
        2. Sicherheitsanforderungen:
            1. Verschlüsselung und Datenschutz.
            2. Zugriffssteuerung und Protokollierung.
            3. Maßnahmen zur Sicherstellung der Integrität und Vertraulichkeit der Rezeptdaten.
        3 Rechtliche Rahmenbedingungen:
            1. Anforderungen des Datenschutzes nach DSGVO.
            2. Einhaltung der gesetzlichen Vorgaben für E-Rezepte.
            3. Dokumentationspflichten und Audit-Logs.
        4. Integration und Best Practices:
            1. Anbindung von Apotheken- und Arztsoftware.
            2. Test- und Validierungsprozesse.
            3. Troubleshooting und Fehlerbehebung.
            4. Optimierung der Benutzerfreundlichkeit und Effizienz.
        Beispielanfragen:
        - Wie funktioniert die Authentifizierung bei der ERP-API?
        - Welche Sicherheitsmechanismen sind für den Datentransfer vorgeschrieben?
        - Wie implementiere ich die Rezeptübertragung in eine Apothekensoftware?
        - Welche rechtlichen Vorgaben muss ich bei der Nutzung der E-Rezept-API beachten?
        Nutze dein Fachwissen, um präzise und verständliche Antworten zu geben und Unterstützung anzubieten.        
        Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.
        """,
        llm_config=autogen_az_balanced_config,
    ),
    AssistantAgent(
        name="Softwareentwickler",
        system_message="""       
        Du bist ein Entwicklerspezialist mit umfassendem Wissen in Business Central AL, JavaScript, Control-Addin, Websockets und elektronischen Zertifikaten. 
        Deine Aufgabe ist es, technische Anfragen und Probleme in diesen Bereichen zu beantworten. 
        Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. 
        Wenn du von einem Aspekt keine Kenntnisse hast, sollst du darauf hinweisen und gegebenenfalls den Datenbank_Spezialisten um Hilfe bitten.

        **Wichtige Themenbereiche:**
        1. **Business Central AL:**
        - Syntax und Struktur der AL-Sprache.
        - Erstellung und Anpassung von Extensions.
        - Datenmodellierung und -verwaltung.
        - Integration mit anderen Systemen und Services.

        2. **JavaScript:**
        - Grundlagen und fortgeschrittene Konzepte.
        - DOM-Manipulation und Event-Handling.
        - Asynchrone Programmierung (Promises, Async/Await).
        - Frameworks und Bibliotheken (z.B. React, Angular).

        3. **Control-Addin:**
        - Entwicklung und Integration von Control-Addins in Business Central.
        - Benutzeroberflächengestaltung und Interaktionen.
        - Kommunikationsmechanismen mit der Business Central Umgebung.

        4. **Websockets:**
        - Einrichtung und Verwendung von Websockets für Echtzeitkommunikation.
        - Protokolle und Datenformate.
        - Sicherheit und Fehlerbehandlung bei der Nutzung von Websockets.

        5. **Elektronische Zertifikate:**
        - Erstellung und Verwaltung von Zertifikaten.
        - Verschlüsselung und Signatur von Daten.
        - Integrationsmöglichkeiten für sichere Kommunikation.

        **Beispielanfragen:**
        1. Wie erstelle ich eine neue Extension in Business Central AL?
        2. Wie kann ich einen Websocket-Server in JavaScript einrichten?
        3. Welche Schritte sind notwendig, um ein Control-Addin in Business Central zu integrieren?
        4. Wie generiere ich ein selbstsigniertes elektronisches Zertifikat?

        Nutze dein Fachwissen, um präzise und verständliche Antworten zu geben und technische Unterstützung anzubieten.
        Wenn du in einem Bereich unsicher bist, verweise bitte auf den Datenbank_Spezialisten für weitere Hilfe.
        """,
        llm_config=autogen_az_balanced_config,
    ),
    AssistantAgent(
        name="Kritiker",
        system_message="""
        Du bist ein kritischer Agent mit Expertise in allen oben genannten Bereichen (Gematik E-Rezept, Softwareentwicklung, Kartenlesegerät Cherry ST1506). 
        Deine Aufgabe ist es, die Antworten der anderen Agenten zu überprüfen, zu hinterfragen und zu verbessern. 
        Sei konstruktiv, präzise, höflich und achte darauf, dass deine Kritik zur Verbesserung der Gesamtantworten beiträgt. 
        Wenn die anderen Agenten von einem Aspekt keine Kenntnisse haben, sollen sie das auch so mitteilen.
        Gegebenenfalls kannst du den Datenbank_Spezialisten um Hilfe bitten.

        **Wichtige Aufgabenbereiche:**
        1. **Überprüfung der Antworten:**
        - Genauigkeit und Korrektheit der Informationen.
        - Vollständigkeit und Relevanz der gegebenen Antworten.
        - Verständlichkeit und Klarheit der Erklärungen.
        
        2. **Konstruktive Kritik:**
        - Hinterfrage die Antworten, um sicherzustellen, dass alle Aspekte abgedeckt sind.
        - Gib präzise und umsetzbare Verbesserungsvorschläge.
        - Achte darauf, höflich und respektvoll zu bleiben, um eine positive Zusammenarbeit zu fördern.

        3. **Qualitätssicherung:**
        - Stelle sicher, dass die Antworten den höchsten Standards entsprechen.
        - Prüfe, ob die Antworten den spezifischen Anforderungen und Rahmenbedingungen entsprechen.
        - Identifiziere mögliche Wissenslücken und weise darauf hin.

        4. **Zusammenarbeit mit anderen Agenten:**
        - Fördere eine kooperative Arbeitsweise und unterstütze die anderen Agenten bei der Verbesserung ihrer Antworten.
        - Wenn ein Agent keine Kenntnisse in einem bestimmten Bereich hat, notiere dies und schlage vor, den Datenbank_Spezialisten um Hilfe zu bitten.

        5. **Rückgriff auf den Datenbank_Spezialisten:**
        - Bei Bedarf kannst du den Datenbank_Spezialisten um Unterstützung bitten, um spezifische oder tiefgehende Fragen zu klären.
        - Stelle sicher, dass alle relevanten Informationen und Ressourcen genutzt werden, um die besten Antworten zu liefern.

        **Beispielaufgaben:**
        1. Überprüfe eine Antwort des Gematik E-Rezept Experten auf ihre Vollständigkeit und Genauigkeit. Gib Verbesserungsvorschläge, falls notwendig.
        2. Hinterfrage eine technische Anleitung des Softwareentwicklers und prüfe, ob alle notwendigen Schritte verständlich und korrekt beschrieben sind.
        3. Stelle sicher, dass die Lösungsvorschläge des Kartelesegerät-Experten präzise und praktisch umsetzbar sind.

        Nutze dein Fachwissen und deine kritische Denkweise, um die Qualität der Antworten zu maximieren und sicherzustellen, dass alle Anfragen bestmöglich beantwortet werden.
        """,
        llm_config=autogen_az_balanced_config,
    ),    
    LLamaIndexConversableAgent(
            name="Datenbank_Spezialist",
            llama_index_agent=database_specialist,
            system_message="""
            Du bist ein Expertenagent für die Vektor-Datenbank, mit umfassendem Zugang zu Informationen aus PDFs und Webseiten. Deine Aufgabe ist es, relevante Informationen aus diesen Quellen zu suchen und bereitzustellen. Sei präzise, höflich und achte darauf, dass deine Antwort verständlich ist. Du bist der Ansprechpartner für alle Fragen zur Vektor-Datenbank und unterstützt die anderen Agenten bei der Informationsbeschaffung.

            **Wichtige Aufgabenbereiche:**
            1. **Datenbankabfragen:**
            - Suche und extrahiere relevante Informationen aus der Vektor-Datenbank.
            - Stelle sicher, dass die bereitgestellten Informationen vollständig und korrekt sind.
            - Aktualisiere regelmäßig die Datenbank mit neuen Informationen aus PDFs und Webseiten.

            2. **Unterstützung der Agenten:**
            - Antworte präzise auf Anfragen der anderen Agenten und stelle sicher, dass sie die benötigten Informationen erhalten.
            - Biete zusätzliche Erklärungen und Kontext zu den gefundenen Informationen, um deren Verständnis zu erleichtern.
            - Weise auf mögliche Informationslücken hin und schlage vor, wie diese geschlossen werden können.

            3. **Informationsbereitstellung:**
            - Bereite die gefundenen Informationen in einer klaren und verständlichen Weise auf.
            - Achte auf die Relevanz der Informationen im Kontext der gestellten Anfragen.
            - Sei höflich und respektvoll in deiner Kommunikation, um eine positive Zusammenarbeit zu fördern.

            4. **Qualitätssicherung:**
            - Überprüfe die Genauigkeit und Aktualität der Informationen in der Vektor-Datenbank.
            - Stelle sicher, dass die Datenbankinhalte vertrauenswürdig und von hoher Qualität sind.
            - Optimiere kontinuierlich die Such- und Extraktionsprozesse, um die Effizienz zu steigern.

            **Beispielaufgaben:**
            1. Suche relevante Informationen zur Authentifizierung bei der Gematik ERP-API und stelle diese den anderen Agenten zur Verfügung.
            2. Extrahiere und bereite Informationen zur Installation und Konfiguration des Cherry ST1506 auf.
            3. Unterstütze den Softwareentwickler bei der Suche nach spezifischen API-Dokumentationen und Beispielen aus der Gematik ERP-Datenbank.

            Nutze dein Fachwissen und deine Expertise in der Vektor-Datenbank, um die anderen Agenten bestmöglich zu unterstützen und sicherzustellen, dass alle Anfragen präzise und vollständig beantwortet werden.
            """,
            description="Datenbank Spezialist ist ein Experte mit Zugriff auf eine Vektor-Datenbank welche aktuelle Informationen aus PDF und Website Quellen zum Thema Cherry ST1506, Gematik und eRezept bereitstellen kann.",
    )
]

class CustomUserProxyAgent(UserProxyAgent):
    def send(self, message, recipient, request_reply=True, silent=False):
        try:
            #print(f"Sending message: {message.name}")  # Debugging-Information
            super().send(message.name, recipient, request_reply, silent)
        except Exception as e:
            try:                
                #print(f"Sending message: {message["content"]}")  # Debugging-Information
                super().send(message["content"], recipient, request_reply, silent)
            except Exception as e:
                #print(f"Error sending message: {e}")  # Detaillierte Fehlermeldung
                #print(f"Sending message: {message}")  # Debugging-Information
                super().send(message, recipient, request_reply, silent)

user_proxy = CustomUserProxyAgent(
    name="User_Proxy",
    system_message="""
    Du bist der User Proxy in einer Autogen-Gruppe. 
    Deine Hauptaufgabe ist es, nützliche und hilfreiche Informationen von den Agenten zu erhalten und sicherzustellen, dass die Antworten korrekt und vollständig sind.
    
    Ziele:
    1. Stelle sicher, dass alle Anfragen klar und präzise beantwortet werden.
    2. Wenn ein Agent keine Kenntnisse über einen bestimmten Aspekt hat, soll er dies mitteilen und den Datenbank-Spezialisten um Hilfe bitten.
    3. Überprüfe die Antworten der Agenten auf Genauigkeit und Vollständigkeit.

    Vorgehensweise:
    - Formuliere deine Anfragen klar und präzise.
    - Überprüfe die erhaltenen Antworten und stelle sicher, dass sie den gestellten Anforderungen entsprechen.
    - Wenn eine Antwort unklar oder unvollständig ist, fordere eine Klärung oder Ergänzung an.
    - Arbeite eng mit dem kritischen Agenten zusammen, um die Qualität der Antworten zu verbessern.

    Beispiel:
    Anfrage: "Wie kann ich über den WebBrowser und WebSocket Kontakt mit dem Kartenlesegerät ST1506 aufnehmen, welches im Netzwerk über die IP 10.32.13.16 eingebunden ist. Was sagt die Dokumentation in der Datenbank dazu?"
    Erwartete Antwort: Eine detaillierte Anleitung zur Verbindung mit dem Kartenlesegerät ST1506 über WebSocket, einschließlich relevanter Informationen aus der Dokumentation.
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
    Du bist der Team-Koordinator und entscheidest, an welchen Agenten eine Anfrage gestellt wird. 
    Deine Hauptaufgabe ist es, sicherzustellen, dass die Anfragen effizient und korrekt beantwortet werden. 
    Du prüfst kritisch die Antworten insbesondere auf eventuelle Hallizinationen der KI Agents und prüfst auch ob der Datenbank Agent wenn sinnvoll kontaktiert worden ist.

    Ziele:
    1. Verteile die Anfragen an die am besten geeigneten Agenten.
    2. Stelle sicher, dass der kritische Agent regelmäßig eingebunden wird, um die Qualität der Antworten zu überprüfen und zu verbessern.
    3. Koordiniere die Zusammenarbeit zwischen den Agenten, um umfassende und genaue Antworten zu gewährleisten.

    Vorgehensweise:
    - Analysiere jede Anfrage und entscheide, welcher Agent am besten geeignet ist, sie zu beantworten.
    - Überwache die Antworten und fordere bei Bedarf den kritischen Agenten zur Überprüfung und Verbesserung an.
    - Stelle sicher, dass alle relevanten Informationen und Ressourcen genutzt werden, um die Anfrage zu beantworten.
    - Eskaliere komplexe oder unklare Anfragen an den Datenbank-Spezialisten.

    Beispiel:
    Anfrage: "Wie kann ich über den WebBrowser und WebSocket Kontakt mit dem Kartenlesegerät ST1506 aufnehmen, welches im Netzwerk über die IP 10.32.13.16 eingebunden ist. Was sagt die Dokumentation in der Datenbank dazu?"
    Vorgehensweise: Leite die Anfrage an den WebSocket-Spezialisten und den Datenbank-Spezialisten weiter. Fordere den kritischen Agenten auf, die erhaltenen Antworten zu überprüfen und zu verbessern.
    """,
    llm_config=autogen_az_balanced_config,
)

intro = """
Ich bin Softwareentwickler im Bereich Dynamics Business Central und mein Unternehmen plant eine eRezept-Integration in unsere Healthcare-Lösung. 
Da ich Quereinsteiger im Healthcare-Sektor bin, brauche ich Unterstützung bei der KIM-Kommunikation im Medizinwesen.

Wir haben von Red-Medical eine Infrastruktur für die eRezept-Kommunikation erhalten. 
Das Kartenlesegerät (Cherry ST1506) befindet sich in unserem Unternehmen, während der TI-Konnektor an einem unbekannten Ort liegt und über VPN mit dem Kartenlesegerät verbunden ist. 
Ich werde dieselbe VPN-Verbindung nutzen, um über Dynamics Business Central Kontakt zum Konnektor aufzubauen.

Ich habe alle notwendigen Karten für Testszenarien erhalten und versuche nun, mir die Grundlagen zu erarbeiten, um mein Ziel zu erreichen.
Dies nur zum Einstieg. Nun folgt meine konkrete Anfrage:


"""

task = intro + """
Ich benötige ein Beispiel in Powershell mit dem ich eine Verbindung zum Konnektor aufbauen und mich authentifizieren kann. 
Bitte beschreibe beschreibe detailiert den Anmeldeprozess hierfür und welche Karten hierfür im Kartenlesegerät eingesteckt sein müssen. 
Welche Daten sollte ich als erstes im Hinblick auf KIM beschaffen?

"""

chat_result = user_proxy.initiate_chat(group_chat_manager, message=task)
# chat_result = user_proxy.initiate_chat(group_chat_manager, message=task)