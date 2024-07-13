import asyncio
from typing import AsyncGenerator

from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import (
    ChatPromptTemplate,
)
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS


class StreamingConversationChain:
    """
    Class for handling streaming conversation chains.
    It creates and stores memory for each conversation,
    and generates responses using the ChatOpenAI model from LangChain.
    """

    def __init__(
        self,
        openai_api_key: str,
        temperature: float = 0.7,
        model_name="gpt-4-1106-preview",
    ):
        self.memories = {}
        self.model_name = model_name
        self.openai_api_key = openai_api_key
        self.temperature = temperature
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=500, chunk_overlap=0
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key
        )  # pyright: ignore [reportCallIssue]

        prd_loader = CSVLoader(file_path="app/resources/sample_data/arte_down.csv")
        prd = prd_loader.load()

        prd_texts = self.text_splitter.split_documents(prd)

        self.vectorstore = FAISS.from_documents(prd_texts, self.embeddings)
        self.retriever = self.vectorstore.as_retriever()

    def add_docs(self, jsonl_path: str, schema):
        json_loader = JSONLoader(
            jsonl_path,
            jq_schema=schema,
            text_content=False,
            json_lines=True,
        )
        style_info = json_loader.load()
        style_texts = self.text_splitter.split_documents(style_info)
        self.vectorstore.add_documents(style_texts)

    async def generate_response(
        self,
        selected_template,
        message: str,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronous function to generate a response for a conversation.
        It creates a new conversation chain for each message and uses a
        callback handler to stream responses as they're generated.
        :param conversation_id: The ID of the conversation.
        :param message: The message from the user.
        """
        prompt = ChatPromptTemplate.from_template(selected_template)
        llm = ChatOpenAI(
            model_name=self.model_name,  # pyright: ignore [reportCallIssue]
            streaming=True,
            temperature=self.temperature,
            openai_api_key=self.openai_api_key,  # pyright: ignore [reportCallIssue]
        )
        # To-do
        # 1. Add a style data in retriever
        # 2. error handler
        if kwargs.get("subject") in ["sn000008", "sn000009"]:
            chain = llm
            selected_template = selected_template.format(
                question=kwargs.get("subject_name"), context=""
            )
            message = message + "\n\n" + selected_template
            self.generation_mode = "gpt"
        else:
            chain = (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            self.generation_mode = "rag"

        buffer = ""
        in_text_block = False

        replace_dict = {}
        if "summary" in kwargs:
            replace_dict["[summary_template]"] = kwargs["summary"]
        if "review_resource" in kwargs:
            replace_dict["[reviews]"] = kwargs["review_resource"]  # dict
        if "youtube_resource" in kwargs:
            replace_dict["[youtube_uri]"] = kwargs["youtube_resource"]  # list
        if "insta_resource" in kwargs:
            replace_dict["[instagram_uri]"] = kwargs["insta_resource"]  # list
        if "img_url" in kwargs:
            replace_dict["[img_uri]"] = kwargs["img_url"]  # list

        find_words = replace_dict.keys()

        try:
            for chunk in chain.stream(message):
                if self.generation_mode == "gpt":
                    chunk = chunk.content  # pyright: ignore [reportAttributeAccessIssue]
                buffer += chunk  # pyright: ignore [reportOperatorIssue]

                if buffer.startswith("__text__") or buffer.startswith("__title__"):
                    in_text_block = True
                    start_kwrd = "__text__" if "__text__" in buffer else "__title__"
                    buffer = ""
                    start_idx = 0
                    yield "data: " + start_kwrd + "\n\n"
                elif in_text_block:
                    if start_idx == 0:  # pyright: ignore [reportPossiblyUnboundVariable]
                        yield "data: [SOS]" + chunk + "\n\n"  # pyright: ignore [reportOperatorIssue]
                        start_idx += 1  # pyright: ignore [reportPossiblyUnboundVariable]
                    elif "\n" in chunk:  # pyright: ignore [reportOperatorIssue]
                        in_text_block = False
                        buffer = ""
                        chunk = chunk.replace(
                            "\n", ""
                        )  # pyright: ignore [reportAttributeAccessIssue]
                        yield "data: " + chunk + "[EOS]" + "\n\n"
                    else:
                        yield "data: " + chunk + "\n\n"  # pyright: ignore [reportOperatorIssue]
                elif "\n" in buffer or buffer.endswith(tuple(find_words)):
                    msg = buffer.replace("\n", "").strip()
                    buffer = ""
                    if "[summary_template]" in msg:
                        replace_str = replace_dict.get("[summary_template]", "")
                        msg = "__summary__" + replace_str
                        buffer = ""
                    elif "[reviews]" in msg:
                        temp_msg = msg.split("[reviews]")
                        reviews_msgs = replace_dict.get("[reviews]", {})
                        if reviews_msgs:
                            msg = temp_msg[0] + replace_dict.get("[reviews]")
                            buffer = temp_msg[1]
                        else:
                            msg = ""
                    elif "[youtube_uri]" in msg:
                        temp_msg = msg.split("[youtube_uri]")
                        youtube_urls = replace_dict.get("[youtube_uri]", [])
                        if youtube_urls:
                            youtube_url = youtube_urls.pop(0)
                            msg = temp_msg[0] + youtube_url
                        else:
                            msg = ""
                    elif "[instagram_uri]" in msg:
                        temp_msg = msg.split("[instagram_uri]")
                        insta_urls = replace_dict.get("[instagram_uri]", [])
                        if insta_urls:
                            insta_urls = insta_urls.pop(0)
                            msg = temp_msg[0] + insta_urls
                        else:
                            msg = ""
                    elif "[img_uri]" in msg:
                        temp_msg = msg.split("[img_uri]")
                        img_urls = replace_dict.get("[img_urls]", [])
                        if img_urls:
                            img_urls = img_urls.pop(0)
                            msg = temp_msg[0] + img_urls
                        else:
                            msg = ""
                    yield "data: " + msg + "\n\n"
        except asyncio.CancelledError as e:
            print("Caught cancelled error in generate_response")
            raise e
