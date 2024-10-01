from langchain.tools import Tool
from modules.jira import JiraExpert

def get_jira_issues(query):
    # Implementiere die Logik für JIRA Issues
    pass

jira_tool = Tool(
    name="get_jira_issues",
    func=get_jira_issues,
    description="Sucht Jira Issues basierend auf einer JQL Query und zeigt diese an."
)
