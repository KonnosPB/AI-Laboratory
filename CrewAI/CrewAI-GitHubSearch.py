import os
from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import WebsiteSearchTool, ScrapeWebsiteTool, TXTSearchTool, DirectorySearchTool, DirectoryReadTool, FileReadTool, GithubSearchTool
from dotenv import load_dotenv
from langchain_openai import AzureOpenAI, AzureOpenAIEmbeddings


gh_token = "TODO";

dir_tool = DirectoryReadTool("./logs")
file_tool = FileReadTool()

apiKey = os.getenv("OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

embedding_rag_dir_search = dict(
        provider="openai",
        config=dict (
            azure_deployment="azure/text-embedding-3-large",
            model="text-embedding-3-large",        
            api_base=endpoint,    
            api_key=apiKey,
            api_version="2024-04-01-preview"
            )
    )  

print("embedding rag search loaded")

llm_rag_dir_search = dict(
        provider="openai",
        config=dict (
            azure_deployment="gpt-4o",
            model="gpt-4o",        
            api_base=endpoint,    
            api_key=apiKey,
            api_version="2024-04-01-preview"
            )
    )

print("llm rag search loaded")

github_search_tool = GithubSearchTool(
    gh_token=gh_token,    
    content_types=['code',],
    config=dict(
        llm=llm_rag_dir_search,
        embedder=embedding_rag_dir_search,
    ),
);

print("tools loaded")


llm = LLM(
    model = "azure/gpt-4o",    
    api_version="2024-04-01-preview",
    api_base=endpoint,    
    api_key=apiKey
)
print("researcher llm loaded")

llm_agent = Agent(
    role='Research',
    goal='Research any question i have and answer in german',
    backstory="Ein Assistent für mich Antworten findet.",    
    llm=llm,
    tools=[github_search_tool, dir_tool, file_tool]
)
print("researcher agent loaded")

llm_chat_manager = LLM(
    model = "azure/gpt-4o",    
    api_version="2024-04-01-preview",
    api_base=endpoint,    
    temperature=0.5,
    api_key=apiKey,    
)
print("chat manager loaded")




task = Task(
        description="Wieviele dateien im repository gematik/api-erp?",
        expected_output="Das korrekte ergebnis unter berücksichtigung der datei extension",       
        agent=llm_agent,
        human_input=True
    )
print("task loaded")


crew = Crew(
    tasks=[task], 
    tool=[file_tool, dir_tool],
    agents=[llm_agent],
    manager_llm=llm_chat_manager,  # Mandatory if manager_agent is not set
    process=Process.hierarchical,  # Specifies the hierarchical management approach
    respect_context_window=True,  # Enable respect of the context window for tasks
    memory=False,  # Enable memory usage for enhanced task execution
    manager_agent=None,  # Optional: explicitly set a specific agent as manager instead of the manager_llm
    planning=False,  # Enable planning feature for pre-execution strategy
    verbose=True,    
)

result = crew.kickoff()
print(result)