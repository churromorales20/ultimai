from langchain_core.runnables import RunnableMap, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import format_document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts.prompt import PromptTemplate
from operator import itemgetter
from langchain_community.vectorstores.faiss import FAISS
from typing import List, Union
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os



os.environ["GOOGLE_API_KEY"] = "AIzaSyDuz_7HUA9hfzkB6NU0tPEWvYG9uaKpnP8"
embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07") 
vectorstore = FAISS.from_texts(
    [
        "James Phoenix works as a data engineering and LLM consultant at JustUnderstandingData",
        "James is 31 years old.",
    ],
    embedding=embedding,
)

retriever = vectorstore.as_retriever()

_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
  Chat History:
  
  {chat_history}
  Follow Up Input: {question}
  Standalone question:"""


CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(template)

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

def _format_chat_history(chat_history: List[Union[HumanMessage, SystemMessage, AIMessage]]) -> str:
    buffer = ""
    for dialogue_turn in chat_history:
        if isinstance(dialogue_turn, HumanMessage):
            buffer += "\nHuman: " + dialogue_turn.content
        elif isinstance(dialogue_turn, AIMessage):
            buffer += "\nAssistant: " + dialogue_turn.content
        elif isinstance(dialogue_turn, SystemMessage):
            buffer += "\nSystem: " + dialogue_turn.content
    return buffer

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

_inputs = RunnableMap(
    standalone_question=RunnablePassthrough.assign(
        chat_history=lambda x: _format_chat_history(x["chat_history"])
    )
    | CONDENSE_QUESTION_PROMPT
    | llm
    | StrOutputParser(),
)

_context = {
    "context": itemgetter("standalone_question") | retriever | _combine_documents,
    "question": lambda x: x["standalone_question"],
}

conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | llm

response = conversational_qa_chain.invoke(
    {
        "question": "where did James work?",
        "chat_history": [],
    }
)

print(response)