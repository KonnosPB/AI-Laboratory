import os
from langchain import LangChain
from modules import devops, jira, git, development, conversation_manager, critical_thinker
from tools import azure_devops_tool, jira_tool, git_tool
from utils.environment import load_environment

# Lade Umgebungsvariablen
load_environment()

# Erstelle eine LangChain-Instanz und füge die Tools und KIs hinzu
chain = LangChain(
    tools=[azure_devops_tool, jira_tool, git_tool],
    llms=[
        {"name": "devops_expert", "model": "gpt-4o", "specialization": "DevOps"},
        {"name": "jira_expert", "model": "gpt-4o", "specialization": "JIRA"},
        {"name": "git_expert", "model": "gpt-4o", "specialization": "GIT"},
        {"name": "development_expert", "model": "gpt-4o", "specialization": "C#, PowerShell, Python, Dynamics Business Central"},
        {"name": "conversation_manager", "model": "gpt-4o", "specialization": "Conversation Management"},
        {"name": "critical_thinker", "model": "gpt-4o", "specialization": "Critical Thinking"}
    ],
    environment={
        "AZURE_OPENAI_ENDPOINT": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.environ.get("AZURE_OPENAI_API_KEY"),
        "OPENAI_API_VERSION": "2024-04-01-preview"
    }
)

# Beispiel für die Koordination einer Anfrage
def handle_request(request_type, query):
    if request_type == "devops":
        result = chain.run_tool("get_azure_devops_workitems", query=query)
    elif request_type == "jira":
        result = chain.run_tool("get_jira_issues", query=query)
    elif request_type == "git":
        result = chain.run_tool("get_git_info", command=query)
    else:
        result = f"Unknown request type: {request_type}"
    
    # Kritisches Denken anwenden, um die Antwort zu überprüfen
    critical_thinker = chain.get_llm("critical_thinker")
    validated_result = critical_thinker.validate(result)
    
    return validated_result

# Beispielaufruf der Funktion
if __name__ == "__main__":
    query = "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.AssignedTo] = @Me AND [System.State] <> 'Closed' ORDER BY [System.ChangedDate] DESC"
    response = handle_request("devops", query)
    print(response)
