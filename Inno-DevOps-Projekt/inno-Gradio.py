import os
import gradio as gr
import pprint
from openai import AzureOpenAI
import asyncio
import tkinter as tk
from tkinter import filedialog
import json

# Example usage
system_prompt_path = "./Inno-DevOps-Projekt/SystemPrompt.txt"
initial_files = [
    './Inno-DevOps-Projekt/Introduction.txt',
    'C:/Repos/DevOps/HC-Work/Product_MED/Product_MED_DotNet_ImagePdfService/Kumavision.ImageUtils/Kumavision.ImageUtils.csproj',
    'C:/Repos/DevOps/HC-Work/Product_MED/Product_MED_DotNet_ImagePdfService/Kumavision.Web.Api.ImageUtils.Install/Kumavision.Web.Api.ImageUtils.Install.csproj',
    'C:/Repos/DevOps/HC-Work/Product_MED/Product_MED_DotNet_ImagePdfService/Kumavision.Web.Api.ImageUtils.Service/Kumavision.Web.Api.ImageUtils.Service.csproj',
    'C:/Repos/DevOps/HC-Work/Product_MED/Product_MED_DotNet_ImagePdfService/Kumavision.Web.Api.ImageUtils.Test/Kumavision.Web.Api.ImageUtils.Test.csproj',
    'C:/Repos/DevOps/HC-Work/Product_MED/Product_MED_DotNet_ImagePdfService/scripts/update-version.ps1',
    'C:/Repos/DevOps/HC-Work/Product_MED/Product_MED_DotNet_ImagePdfService/Installer_Script.iss',
    'C:/Repos/DevOps/HC-Work/Product_MED/Product_MED_DotNet_ImagePdfService/azure-pipeline.yaml'
]

# Global variable to store chat history
grhistory = []

# Function to load a file into chat history
def load_file_into_history(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            filecontent = file.read()
            # Entferne das BOM, falls vorhanden
            if filecontent.startswith('\ufeff'):
                filecontent = filecontent.lstrip('\ufeff')
            file_name, file_extension = os.path.splitext(file_path)
            display_name = os.path.basename(file_path)
            print(f"Loading {file_path}")
            if file_extension == ".ts":
                grhistory.append([f"{display_name}\n---\n```typescript\n{filecontent}\n```", "Ok."])
            elif file_extension == ".json":
                grhistory.append([f"{display_name}\n---\n```json\n{filecontent}\n```", "Ok."])
            elif file_extension == ".xml":
                grhistory.append([f"{display_name}\n---\n```xml\n{filecontent}\n```", "Ok."])            
            elif file_extension == ".ps1":
                grhistory.append([f"{display_name}\n---\n```powershell\n{filecontent}\n```", "Ok."])
            else:
                grhistory.append([f"{display_name}\n---\n```\n{filecontent}\n```", "Ok."])
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")

def append_history(message):
    grhistory.append([message, "Ok."])

# Function to convert Gradio history to Azure OpenAI messages format
def gradio_history_to_azure_openai_messages(gradio_history, system_prompt_path):
    messages = []
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as file:
            filecontent = file.read()
            messages.append({"role": "system", "content": filecontent})
    except Exception as e:
        print(f"Error loading system prompt: {e}")
    
    for user_input, model_response in gradio_history:
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": model_response})
    return messages

# Asynchronous chat function to interact with Azure OpenAI
async def chat(message, history, system_prompt_path):
    messages = gradio_history_to_azure_openai_messages(history, system_prompt_path)
    prompt = message
    if hasattr(message, "text"):
        prompt = message.text
    messages.append({"role": "user", "content": prompt})
    try:
        response = llm.chat.completions.create(model='gpt-4o', messages=messages, stream=True, temperature=0.5)
        aimessage = ""
        for chunk in response:
            if len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    aimessage += delta.content
                    yield aimessage
    except Exception as e:
        print(f"Error during chat interaction: {e}")
        yield "An error occurred during the chat interaction."

# Function to save chat history to a file
def save_history():
    print("#save_history")
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    print(f"#file_path {file_path}")
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(grhistory, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")
    root.destroy()

# Function to load chat history from a file
def load_history():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                new_history = json.load(file)
                grhistory.clear()
                grhistory.extend(new_history)
        except Exception as e:
            print(f"Error loading history: {e}")
    root.destroy()
    return grhistory

# Initialize Azure OpenAI client
llm = AzureOpenAI(azure_deployment='gpt-4o')

# Custom CSS for chatbot styling
custom_css = """
<style>
    .chatbot-bubble {
        max-width: 100%;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
</style>
"""

# Head style for responsive design
head_style = """
<style>
@media (min-width: 1536px)
{
    .gradio-container {
        min-width: var(--size-full) !important;
    }
}
</style>
"""

def create_interface(system_prompt_path, initial_files):
    # Load initial files into history
    for file_path in initial_files:
        load_file_into_history(file_path)

    # Gradio chatbot component
    chatbot = gr.Chatbot(value=grhistory, height="100%", min_width="100%", render_markdown=True, bubble_full_width=True, show_copy_button=True, elem_classes="chatbot-bubble")
    
    # Gradio interface setup
    with gr.Blocks(head=head_style) as demo:
        gr.Markdown("# Development Bot")
        gr.HTML(custom_css)  # Add custom CSS here
        chatbot.render()
        with gr.Row():
            save_button = gr.Button("Save Chat History")
            load_button = gr.Button("Load Chat History")

        save_button.click(fn=save_history)
        load_button.click(fn=load_history, outputs=chatbot)

        gr.ChatInterface(
            fn=lambda message, history: chat(message, history, system_prompt_path),
            chatbot=chatbot,
            title="Development Bot",
            autofocus=True,
            multimodal=True,
            fill_width=True,
            fill_height=True,
        )

    # Launch the Gradio interface
    demo.launch()

create_interface(system_prompt_path, initial_files)
