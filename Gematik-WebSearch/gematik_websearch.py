import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.retrievers.web_research import WebResearchRetriever

import os

st.set_page_config(page_title="Interweb Explorer", page_icon="🌐")

def settings():

    # Vectorstore    
    from langchain_core.vectorstores import InMemoryVectorStore
    from langchain_community.embeddings import AzureOpenAIEmbeddings
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = "text-embedding-3-large" 
    model_name = "text-embedding-3-large" 
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_api_version = os.getenv("OPENAI_API_VERSION")
    openai_organization = os.getenv("OPENAI_ORG_ID")
    embeddings_model = AzureOpenAIEmbeddings(
        # model=model_name,
        # default_headers=openai_api_key,
        # deployment=deployment_name,
        # embeddings_model=model_name,
        #base_url=azure_endpoint,
        #validate_base_url="https://kpa-az-open-ai-us2.openai.azure.com/openai",
        #azure_endpoint = azure_endpoint,
        #azure_deployment=deployment_name,
        #openai_api_key=openai_api_key,
        #openai_api_version=openai_api_version,
        #openai_organization=openai_organization,
        chunk_size=1024,
        )
    #embedding_size = 1536  
    #index = Chroma.I faiss.IndexFlatL2(embedding_size)  
    #vectorstore_public = Chroma(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
    vectorstore_public = InMemoryVectorStore(embeddings_model)

    # LLM
    from langchain.chat_models.azure_openai import AzureChatOpenAI
    llm = AzureChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)

    # Search
    #from langchain.utilities import GoogleSearchAPIWrapper
    from langchain_community.tools import DuckDuckGoSearchRun
    search = DuckDuckGoSearchRun()   

    # Initialize 
    web_retriever = WebResearchRetriever.from_llm(
        vectorstore=vectorstore_public,
        llm=llm, 
        search=search, 
        allow_dangerous_requests=True,
        num_search_results=3
    )

    return web_retriever, llm

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.info(self.text)


class PrintRetrievalHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container.expander("Context Retrieval")

    def on_retriever_start(self, query: str, **kwargs):
        self.container.write(f"**Question:** {query}")

    def on_retriever_end(self, documents, **kwargs):
        # self.container.write(documents)
        for idx, doc in enumerate(documents):
            source = doc.metadata["source"]
            self.container.write(f"**Results from {source}**")
            self.container.text(doc.page_content)


st.sidebar.image("img/ai.png")
st.header("`Interweb Explorer`")
st.info("`I am an AI that can answer questions by exploring, reading, and summarizing web pages."
    "I can be configured to use different modes: public API or private (no data sharing).`")

# Make retriever and llm
if 'retriever' not in st.session_state:
    st.session_state['retriever'], st.session_state['llm'] = settings()
web_retriever = st.session_state.retriever
llm = st.session_state.llm

# User input 
question = st.text_input("`Ask a question:`")

if question:

    # Generate answer (w/ citations)
    import logging
    logging.basicConfig()
    logging.getLogger("langchain.retrievers.web_research").setLevel(logging.INFO)    
    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(llm, retriever=web_retriever)

    # Write answer and sources
    retrieval_streamer_cb = PrintRetrievalHandler(st.container())
    answer = st.empty()
    stream_handler = StreamHandler(answer, initial_text="`Answer:`\n\n")
    result = qa_chain({"question": question},callbacks=[retrieval_streamer_cb, stream_handler])
    answer.info('`Answer:`\n\n' + result['answer'])
    st.info('`Sources:`\n\n' + result['sources'])