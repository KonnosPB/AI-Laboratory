#pip install azure-devops
#pip install msrest
#pip install jira
#pip install GitPython

import os
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.work_item_tracking.models import Wiql
from jira import JIRA
import git

def get_git_info(command: str, repo_path: str = '.'):
    """
    Führt ein Git-Kommando im angegebenen Repository aus und gibt das Ergebnis zurück.

    Parameter:
    - command (str): Das Git-Kommando, das ausgeführt werden soll (z.B. 'status', 'log').
    - repo_path (str): Der Pfad zum Git-Repository. Standardmäßig das aktuelle Verzeichnis.

    Rückgabewert:
    - Das Ergebnis des Git-Kommandos als Zeichenkette.

    Beispiel:
    ```python
    result = get_git_info('status')
    print(result)
    ```
    """
    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        raise ValueError(f"Invalid Git repository at path: {repo_path}")

    # Ausführen des Git-Kommandos
    if command == 'status':
        result = repo.git.status()
    elif command == 'log':
        result = repo.git.log()
    elif command == 'branch':
        result = repo.git.branch()
    elif command == 'diff':
        result = repo.git.diff()
    else:
        raise ValueError(f"Unsupported Git command: {command}")

    return result

def get_azure_devops_workitems(query):
    """
    Sucht Azure DevOps Work Items basierend auf einer WIQL Query und zeigt diese an.

    Parameter:
    - query (str): Eine WIQL Query, die die gewünschten Work Items definiert.

    Rückgabewert:
    - Eine Liste von Work Items, wobei jedes Work Item ein Objekt mit den abgerufenen Feldern ist.

    Beispiel:
    ```python
    query = \"""
    SELECT [System.Id], [System.Title], [System.State]
    FROM WorkItems
    WHERE [System.AssignedTo] = @Me
    AND [System.State] <> 'Closed'
    ORDER BY [System.ChangedDate] DESC
    \"""
    work_items = get_azure_devops_workitems(query)
    for item in work_items:
        print(f"ID: {item.id}, Title: {item.fields['System.Title']}, State: {item.fields['System.State']}")
    ```
    """

    # Personal Access Token (PAT) aus der Umgebungsvariable abrufen
    personal_access_token = os.getenv('PSDEV_AZURE_DEVOPS_TOKEN')
    if not personal_access_token:
        raise ValueError("Personal Access Token not found in environment variable 'PSDEV_AZURE_DEVOPS_TOKEN'")

    # Azure DevOps Organisation URL (z.B. https://dev.azure.com/{organization})    
    organization_url = os.getenc('PSDEV_AZURE_DEVOPS_ORGANISATION_URL'

    # Verbindung herstellen
    credentials = BasicAuthentication('', personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)

    # Work Item Tracking Client abrufen
    wit_client = connection.clients.get_work_item_tracking_client()

    # WIQL (Work Item Query Language) Query ausführen
    wiql = Wiql(query=query)
    result = wit_client.query_by_wiql(wiql).work_items

    # Work Items abrufen
    work_items = []
    if result:
        ids = [item.id for item in result]
        work_items = wit_client.get_work_items(ids)

    return work_items


# Tool Definition für LangChain
azure_devops_tool = Tool(
    name="get_azure_devops_workitems",
    func=get_azure_devops_workitems,
    description="""
    Sucht Azure DevOps Work Items basierend auf einer WIQL Query und zeigt diese an.

    Parameter:
    - query (str): Eine WIQL Query, die die gewünschten Work Items definiert.

    Rückgabewert:
    - Eine Liste von Work Items, wobei jedes Work Item ein Objekt mit den abgerufenen Feldern ist.

    Beispiel:
    ```python
    query = \"""
    SELECT [System.Id], [System.Title], [System.State]
    FROM WorkItems
    WHERE [System.AssignedTo] = @Me
    AND [System.State] <> 'Closed'
    ORDER BY [System.ChangedDate] DESC
    \"""
    work_items = get_azure_devops_workitems(query)
    for item in work_items:
        print(f"ID: {item.id}, Title: {item.fields['System.Title']}, State: {item.fields['System.State']}")
    ```
    """
)

def get_jira_issues(query: str):
    """
    Sucht Jira Issues basierend auf einer JQL Query und zeigt diese an.

    Parameter:
    - query (str): Eine JQL Query, die die gewünschten Issues definiert.

    Rückgabewert:
    - Eine Liste von Issues, wobei jedes Issue ein Objekt mit den abgerufenen Feldern ist.

    Beispiel:
    ```python
    query = 'assignee = currentUser() AND status != Closed ORDER BY updated DESC'
    issues = get_jira_issues(query)
    for issue in issues:
        print(f"ID: {issue.key}, Title: {issue.fields.summary}, State: {issue.fields.status.name}")
    ```
    """
    # API Token aus der Umgebungsvariable abrufen
    api_token = os.getenv('PSDEV_JIRA_API_TOKEN')
    if not api_token:
        raise ValueError("API Token not found in environment variable 'PSDEV_JIRA_API_TOKEN'")

    # Jira Server URL und Benutzername
    jira_server = 'https://your-domain.atlassian.net'
    jira_user = 'your-email@example.com'  # Ersetze dies durch deine Jira-Benutzer-E-Mail

    # Verbindung zu Jira herstellen
    jira_options = {'server': jira_server}
    jira = JIRA(options=jira_options, basic_auth=(jira_user, api_token))

    # JQL Query ausführen
    issues = jira.search_issues(query)

    return issues

# Tool Definition für LangChain
jira_tool = Tool(
    name="get_jira_issues",
    func=get_jira_issues,
    description="""
    Sucht Jira Issues basierend auf einer JQL Query und zeigt diese an.

    Parameter:
    - query (str): Eine JQL Query, die die gewünschten Issues definiert.

    Rückgabewert:
    - Eine Liste von Issues, wobei jedes Issue ein Objekt mit den abgerufenen Feldern ist.

    Beispiel:
    ```python
    query = 'assignee = currentUser() AND status != Closed ORDER BY updated DESC'
    issues = get_jira_issues(query)
    for issue in issues:
        print(f"ID: {issue.key}, Title: {issue.fields.summary}, State: {issue.fields.status.name}")
    ```
    """
)  

# Tool Definition für LangChain
git_tool = Tool(
    name="get_git_info",
    func=get_git_info,
    description="""
    Führt ein Git-Kommando im angegebenen Repository aus und gibt das Ergebnis zurück.

    Parameter:
    - command (str): Das Git-Kommando, das ausgeführt werden soll (z.B. 'status', 'log', 'branch', 'diff').
    - repo_path (str): Der Pfad zum Git-Repository. Standardmäßig das aktuelle Verzeichnis.

    Rückgabewert:
    - Das Ergebnis des Git-Kommandos als Zeichenkette.

    Beispiel:
    ```python
    result = get_git_info('status')
    print(result)
    ```
    """
)



# # Beispielaufruf der Funktion
# if __name__ == "__main__":
#     query = "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.AssignedTo] = @Me AND [System.State] <> 'Closed' ORDER BY [System.ChangedDate] DESC"
#     work_items = get_azure_devops_workitems(query)
#     for item in work_items:
#         print(f"ID: {item.id}, Title: {item.fields['System.Title']}, State: {item.fields['System.State']}")

# # Beispielaufruf der Funktion
# if __name__ == "__main__":
#     query = 'assignee = currentUser() AND status != Closed ORDER BY updated DESC'
#     issues = get_jira_issues(query)
#     for issue in issues:
#         print(f"ID: {issue.key}, Title: {issue.fields.summary}, State: {issue.fields.status.name}")        

# Beispielaufruf der Funktion
#if __name__ == "__main__":
#    result = get_git_info('status')
#    print(result)