import os
import gradio as gr
import pprint
from openai import AzureOpenAI
import asyncio
import tkinter as tk
from tkinter import filedialog
import json

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
                grhistory.append([f"{display_name}\n---\n``` typescript\n{filecontent}\n```", "Ok."])
            elif file_extension == ".json":
                grhistory.append([f"{display_name}\n---\n``` json\n{filecontent}\n```", "Ok."])
            elif file_extension == ".xml":
                grhistory.append([f"{display_name}\n---\n``` xml\n{filecontent}\n```", "Ok."])            
            elif file_extension == ".ps1":
                grhistory.append([f"{display_name}\n---\n``` powershell\n{filecontent}\n```", "Ok."])
            else:
                grhistory.append([f"{display_name}\n---\n```\n{filecontent}```", "Ok."])
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")

def append_history(message):
    grhistory.append([message, "Ok."])

systemPromptPath = "Work-AI-Functions-Support/SystemPrompt.txt"

# Load initial files into history
load_file_into_history('Work-AI-Functions-Support/Introduction.txt')
load_file_into_history('Work-AI-Functions/config/settings.py')
load_file_into_history('Work-AI-Functions/tools/__init__.py')
load_file_into_history('Work-AI-Functions/tools/azure_devops_tool.py')
load_file_into_history('Work-AI-Functions/tools/functions.py')
load_file_into_history('Work-AI-Functions/tools/git_tool.py')
load_file_into_history('Work-AI-Functions/tools/jira_tool.py')
load_file_into_history('Work-AI-Functions/tools/multi_git_repository_tool.py')
load_file_into_history('Work-AI-Functions/tools/xliff_tool.py')
load_file_into_history('Work-AI-Functions/main.py')
load_file_into_history('Work-AI-Functions/requirements.txt')


# Function to convert Gradio history to Azure OpenAI messages format
def gradio_history_to_azure_openai_messages(gradio_history):
    messages = []
    try:
        with open(systemPromptPath, 'r', encoding='utf-8') as file:
            filecontent = file.read()
            messages.append({"role": "system", "content": filecontent})
    except Exception as e:
        print(f"Error loading system prompt: {e}")
    
    for user_input, model_response in gradio_history:
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": model_response})
    return messages

# Asynchronous chat function to interact with Azure OpenAI
async def chat(message, history):
    messages = gradio_history_to_azure_openai_messages(history)    
    if hasattr(message, "text"):
        prompt = message.text
    else:
        try:
            prompt = message["text"]
        except KeyError:
            prompt = message                   
    messages.append({"role": "user", "content": prompt})
    try:
        response = llm.chat.completions.create(model='gpt-4o', 
                                               messages=messages, 
                                               stream=True, 
                                               temperature=0.2, 
                                               top_p=0.9, 
                                               frequency_penalty=0.0, 
                                               presence_penalty=0.0, 
                                               #max_tokens=4096
                                               )
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
        fn=chat,
        chatbot=chatbot,
        title="Development Bot",
        autofocus=True,
        multimodal=True,
        fill_width=True,
        fill_height=True,
    )

# Launch the Gradio interface
demo.launch()





