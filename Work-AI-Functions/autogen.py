

def buildmodel()
    {
        {"model": "gpt-4o", 
                                 "api_type": "azure", 
                                 "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                                 "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                                 "api_version": "2024-04-01-preview",                                 
                                }
    }