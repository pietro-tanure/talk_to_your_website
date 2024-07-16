from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import HTMLToDocument
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret


class URLChat:
    def __init__(
        self, llm_model: str = "llama3", split_by: str = "sentence", split_length: int = 15
    ):
        """Model that answers questions based on the content of a given URL

        Args:
            llm_model (str, optional): LLM used for text generation. Defaults to "llama3".
            split_by (str, optional): Splits the document from the URL into smaller parts before indexing.
                Can split by "word", "sentence", "passage" (paragraph), or "page". Defaults to "sentence".
            split_length (int, optional): The chunk size, which is the number of words, sentences, or passages. Defaults to 15.

        Raises:
            ValueError: User must choose one of the available LLM: 'llama3', 'mixtral', 'gemma', 'gemma2', 'whisper'
        """
        if llm_model == "llama3":
            self.model = "llama3-8b-8192"
        elif llm_model == "mixtral":
            self.model = "mixtral-8x7b-32768"
        elif llm_model == "gemma":
            self.model = "gemma-7b-it"
        elif llm_model == "gemma2":
            self.model = "gemma2-9b-it"
        elif llm_model == "whisper":
            self.model = "whisper-large-v3"
        else:
            raise ValueError(
                "Choose one of the available LLM: 'llama3', 'mixtral', 'gemma', 'gemma2', 'whisper'"
            )

        # Components for url indexing pipeline
        self.fetcher = LinkContentFetcher()
        self.converter = HTMLToDocument()
        self.document_store = InMemoryDocumentStore()
        self.preprocessor = DocumentSplitter(split_by=split_by, split_length=split_length)
        self.document_writer = DocumentWriter(document_store=self.document_store)
        self.index_pipeline = self.build_index_pipeline(
            self.fetcher, self.converter, self.preprocessor, self.document_writer
        )

        # Components for question answering pipeline
        self.retriever = InMemoryBM25Retriever(document_store=self.document_store)
        self.prompt = [ChatMessage.from_system(
            """
            According to the contents of this website:
            {% for document in documents %}
            {{document.content}}
            {% endfor %}
            Answer the user's question.
            """
        )]
        self.prompt_builder = ChatPromptBuilder(template=self.prompt)
        self.llm = OpenAIChatGenerator(
            api_key=Secret.from_env_var("GROQ_API_KEY"),
            api_base_url="https://api.groq.com/openai/v1",
            model=self.model,
        )
        self.ask_pipeline = self.build_ask_pipeline(self.retriever, self.prompt_builder, self.llm)
        self.messages = {}

    def build_index_pipeline(self, fetcher, converter, preprocessor, document_writer):
        index_pipeline = Pipeline()
        index_pipeline.add_component("fetcher", fetcher)
        index_pipeline.add_component("converter", converter)
        index_pipeline.add_component("preprocessor", preprocessor)
        index_pipeline.add_component("document_writer", document_writer)

        index_pipeline.connect("fetcher.streams", "converter.sources")
        index_pipeline.connect("converter.documents", "preprocessor.documents")
        index_pipeline.connect("preprocessor.documents", "document_writer.documents")
        return index_pipeline

    def build_ask_pipeline(self, retriever, prompt_builder, llm):
        ask_pipeline = Pipeline()
        ask_pipeline.add_component("retriever", retriever)
        # ask_pipeline.add_component("question_prompt_builder", question_prompt_builder)
        ask_pipeline.add_component("prompt_builder", prompt_builder)
        ask_pipeline.add_component("llm", llm)

        ask_pipeline.connect("retriever", "prompt_builder.documents")
        ask_pipeline.connect("prompt_builder.prompt", "llm.messages")
        return ask_pipeline

    def index(self, url: str):
        """Send a url so that the model extracts and indexes its content

        Args:
            url (str): full URL. Example: "https://en.wikipedia.org/wiki/Brazil"
        """
        self.index_pipeline.run({"fetcher": {"urls": [url]}})

    def ask(self, url: str, question: str) -> str:
        """Send a url that has been previously indexed using the _index_ method and a question relating to it, 
        this will create a chat and you can ask followup questions related to that url.

        Args:
            url (str): a url that has been previously indexed using _index_ method. Example: "https://en.wikipedia.org/wiki/Brazil"
            question (str): a question relating to the url. Example: "What is the population of Brazil"

        Returns:
            str: A string containing the reply generated by the model.
        """
        if url not in self.messages:
            self.messages[url] = self.prompt.copy()
        
        self.messages[url].append(ChatMessage.from_user(question))
        response = self.ask_pipeline.run({
                "retriever": {"query": question, "filters": {"url": url}, "top_k": 15},
                "prompt_builder": {"template": self.messages[url]},
            })["llm"]["replies"][0]
        self.messages[url].append(response)

        return response.content
