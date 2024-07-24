import os
import gradio as gr
import pprint
from openai import AzureOpenAI
import asyncio
import tkinter as tk
from tkinter import filedialog
import json

grhistory = []

def load_file_into_history(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:        
        filecontent =  file.read()
        file_name, file_extension = os.path.splitext(file_path)  
        display_name = os.path.basename(file_path) 
        print(f"#file extension: {file_extension}")     
        if file_extension == ".ts":
            grhistory.append([f"{display_name}\n---\n``` typescript\n{filecontent}\n```", "Ok."])
        elif file_extension == ".json":
            grhistory.append([f"{display_name}\n---\n``` json\n{filecontent}\n```", "Ok."])
        elif file_extension == ".xml":
            grhistory.append([f"{display_name}\n---\n``` xml\n{filecontent}\n```", "Ok."])
        elif file_extension == ".ps1":
            grhistory.append([f"{display_name}\n---\n``` powershell\n{filecontent}\n```", "Ok."])
        else:
            grhistory.append([f"{display_name}\n---\n```{filecontent}```", "Ok."])

load_file_into_history('C:/Repos/Github/KonnosPB/AI-Laboratory/Prompts/Introdution-VSC-BusinesCentral-TestRunner.txt')
load_file_into_history('C:/Repos/Github/KonnosPB/BusinessCentral-AL-Test-Runner-App/src/codeunit/WebApi.Codeunit.al')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/package.json')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/apiClient.ts')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/project.ts')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/testRunner.ts')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/testViewProviders.ts')
load_file_into_history('C:/Repos/Github/KonnosPB/VSC-BusinessCentral-Test-Runner/src/extension.ts')

def gradio_history_to_azure_openai_messages(gradio_history):    
    messages = []   
    with open("C:/Repos/Github/KonnosPB/AI-Laboratory/Prompts/SystemPrompt-VSC-BusinesCentral-TestRunner.txt", 'r', encoding='utf-8') as file:
        filecontent =  file.read()
        messages.append({"role": "system", "content": filecontent})
    for user_input, model_response in gradio_history:
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": model_response})    
    return messages

async def chat(message, history):
    messages = gradio_history_to_azure_openai_messages(history)    
    prompt = message
    if (hasattr(message, "text")):
        prompt = message.text
    messages.append({"role": "user", "content": prompt})
    response = llm.chat.completions.create(model='gpt-4o', messages=messages, stream=True, temperature=0.5) 
    aimessage = ""
    for chunk in response:
        if len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content:                
                aimessage += delta.content
                yield aimessage

def save_history():
    print("#save_history")
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])    
    print(f"#file_path {file_path}");
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(grhistory, file, ensure_ascii=False, indent=4)
    root.destroy()

def load_history():
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            new_history = json.load(file)
            grhistory.clear()
            grhistory.extend(new_history)
    root.destroy()
    return grhistory

llm = AzureOpenAI(azure_deployment='gpt-4o')
chatbot = gr.Chatbot(value=grhistory, height="100%", min_width="100%", render_markdown=True, bubble_full_width=True, show_copy_button=True)

with gr.Blocks() as demo:
    gr.Markdown("# Development Bot")
    chatbot.render()    
    with gr.Row():
        save_button = gr.Button("Save Chat History")
        load_button = gr.Button("Load Chat History")

    save_button.click(fn=save_history)
    load_button.click(fn=load_history, outputs=chatbot)

    gr.ChatInterface(
        fn=chat,
        chatbot=chatbot,
        title="Development Bot",
        autofocus=True,
        multimodal=True,
        fill_width=True,
        fill_height=True,        
    )

demo.launch()