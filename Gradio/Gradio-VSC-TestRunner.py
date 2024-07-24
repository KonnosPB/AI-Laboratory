import os
import gradio as gr
import pprint
from openai import AzureOpenAI
import asyncio

grhistory = []
def load_file_into_history(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:        
        filecontent =  file.read()
        grhistory.append([filecontent, "Ok."])

load_file_into_history('C:/Repos/Github/KonnosPB/AI-Laboratory/Prompts/Introdution-VSC-BusinesCentral-TestRunner.txt')
load_file_into_history('C:/Repos/Github/KonnosPB/BusinessCentral-AL-Test-Runner-App/src/codeunit/WebApi.Codeunit.al')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/package.json')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/apiClient.ts')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/project.ts')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/testRunner.ts')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/testViewProviders.ts')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/extension.ts')

#Konvertiert eine Gradio-History in das Azure OpenAI-Nachrichtenformat.
def gradio_history_to_azure_openai_messages(gradio_history):    
    messages = []   
    with open("C:/Repos/Github/KonnosPB/AI-Laboratory/Prompts/SystemPrompt-VSC-BusinesCentral-TestRunner.txt", 'r', encoding='utf-8') as file:
        filecontent =  file.read()
        messages.append({"role": "system", "content": filecontent})
    for user_input, model_response in gradio_history:
        # Füge die Benutzer-Eingabe als Nachricht hinzu
        messages.append({"role": "user", "content": user_input})
        # Füge die Modell-Antwort als Nachricht hinzu
        messages.append({"role": "assistant", "content": model_response})    
    return messages

async def chat(message, history):
    #print("#message");pprint.pprint(message)    
    #print("#gradio-history"); pprint.pprint(history)    
    messages = gradio_history_to_azure_openai_messages(history)    
    #print("#az-history");pprint.pprint(message)    
    prompt = message
    if (hasattr(message, "text")):
        prompt = message.text
    #print("#prompt");pprint.pprint(prompt)  
    messages.append({"role": "user", "content": prompt})
    response = llm.chat.completions.create(model='gpt-4o', messages=messages, stream=True, temperature=0.5) 
    #print(f"#response");pprint.pprint(response)     
    aimessage = ""
    for chunk in response:
        ##print(f"#chunk");pprint.pprint(chunk)  
        if len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            ##print(f"#delta");pprint.pprint(delta)  
            if delta.content: # Get remaining generated response if applicable                
                aimessage += delta.content
                yield aimessage

llm = AzureOpenAI(azure_deployment='gpt-4o')
chatbot = gr.Chatbot(value=grhistory, height="100%")
demo = gr.ChatInterface(    
    fn=chat,    
    chatbot=chatbot,
    title="Development Bot",
    autofocus=True,
    multimodal=True,
)
demo.launch()