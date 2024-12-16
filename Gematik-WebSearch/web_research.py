from langchain_community.utilities import SearchAPIWrapperBase
...
class WebResearchRetriever(BaseRetriever):
    """Search retriever."""

    # Inputs
    vectorstore: VectorStore = Field(
        ..., description="Vector store for storing web pages"
    )
    llm_chain: LLMChain
    search: SearchAPIWrapperBase = Field(..., description="Search API Wrapper")
    ...



DEFAULT_LLAMA_SEARCH_PROMPT = PromptTemplate(
    input_variables=["question", "search_engine"],
    template="""<<SYS>> \n You are an assistant tasked with improving {search_engine} search \
results. \n <</SYS>> \n\n [INST] Generate THREE {search_engine} search queries that \
are similar to this question. The output should be a numbered list of questions \
and each should have a question mark at the end: \n\n {question} [/INST]""",
)

DEFAULT_SEARCH_PROMPT = PromptTemplate(
    input_variables=["question", "search_engine"]],
    template="""You are an assistant tasked with improving {search_engine} search \
results. Generate THREE {search_engine} search queries that are similar to \
this question. The output should be a numbered list of questions and each \
should have a question mark at the end: {question}""",
)

# And later in the code where the prompts are used:

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:

        # Get search questions
        search_eng_name = self.search.search_engine_name
        logger.info(f"Generating questions for {search_eng_name} Search ...")
        result = self.llm_chain({"question": query, "search_engine": search_eng_name})
