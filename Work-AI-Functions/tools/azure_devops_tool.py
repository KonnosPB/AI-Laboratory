from langchain.tools import Tool
from modules.devops import DevOpsExpert

def get_azure_devops_workitems(query):
    # Implementiere die Logik für Azure DevOps Work Items
    pass

azure_devops_tool = Tool(
    name="get_azure_devops_workitems",
    func=get_azure_devops_workitems,
    description="Sucht Azure DevOps Work Items basierend auf einer WIQL Query und zeigt diese an."
)
