import os
from autogen import ConversableAgent

def build_model_config(temparature: float = 0, top_P: float=0.9 ):
    return { "model": "gpt-4o", 
             "api_type": "azure", 
             "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
             "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
             "api_version": "2024-04-01-preview",
             "temperature":temparature,
             "top_p": float
            }

def build_model_configs(*args):
    args_list = list(args)
    result = {"config_list": args_list},
    return result

def build_conversable_agent(name: str, description: str, system_prompt: str, human_input_mode: str = "NEVER"):
    agent = ConversableAgent(
        name=name,
        description=description,
        llm_config=build_model_configs(build_model_config()),    
        system_message=system_prompt,
        code_execution_config=False,
        function_map=None,
        human_input_mode=str,
        )
    return agent
    
gitAgent = build_conversable_agent(name="git_agent", 
                                   description="Ein Spezialist für die Informationnbeschaffung von Git Repositories.",
                                   system_prompt="Du bist ein Spezialist für die Informationnbeschaffung von Git Repositories. Deine Antworten sind präzise, bündig und exakt. Es ist ein Ehre für dich, wenn du gute Ergebnisse ablieferst"
                                   )

devopsAgent = build_conversable_agent(name="git_agent", 
                                   description="Ein Spezialist für die Informationnbeschaffung von Git Repositories.",
                                   system_prompt="Du bist ein Spezialist für die Informationnbeschaffung von Git Repositories. Deine Antworten sind präzise, bündig und exakt. Es ist ein Ehre für dich, wenn du gute Ergebnisse ablieferst"
                                   )

jiraAgent = build_conversable_agent(name="git_agent", 
                                   description="Ein Spezialist für die Informationnbeschaffung von Git Repositories.",
                                   system_prompt="Du bist ein Spezialist für die Informationnbeschaffung von Git Repositories. Deine Antworten sind präzise, bündig und exakt. Es ist ein Ehre für dich, wenn du gute Ergebnisse ablieferst"
                                   )

reviewerAgent = build_conversable_agent(name="git_agent", 
                                   description="Ein Spezialist für die Informationnbeschaffung von Git Repositories.",
                                   system_prompt="Du bist ein Spezialist für die Informationnbeschaffung von Git Repositories. Deine Antworten sind präzise, bündig und exakt. Es ist ein Ehre für dich, wenn du gute Ergebnisse ablieferst"
                                   )
