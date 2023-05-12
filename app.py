# importing necessary flask functions
from flask import Flask, request
from flask_cors import CORS
import os

# Flask config
app = Flask(__name__)
CORS(app)

# Default route to test if the app is properly deployed
@app.route("/")
def read_root():
    return {"LangChainApp": "Working"}

from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
cohere_api_key = os.getenv('COHERE_API_KEY')
weaviate_api_key = os.getenv('weaviate_api_key')
weaviate_url = os.getenv('weaviate_url')

# Retrieval code using langchain functions
import weaviate
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Weaviate
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from prompt import PROMPT

# Connect to the Weaviate demo databse containing 10M wikipedia vectors
# This uses a public READ-ONLY Weaviate API key
auth_config = weaviate.auth.AuthApiKey(api_key=weaviate_api_key) 

client = weaviate.Client( url=weaviate_url, auth_client_secret=auth_config, 
                         additional_headers={ "X-Cohere-Api-Key": cohere_api_key})

## Defining vectorstore, embedding model, and llm
vectorstore = Weaviate(client,  index_name="Articles", text_key="text")
vectorstore._query_attrs = ["text", "title", "url", "views", "lang", "_additional {distance}"]
vectorstore.embedding =CohereEmbeddings(model="embed-multilingual-v2.0", cohere_api_key=cohere_api_key)
llm =OpenAI(temperature=0, openai_api_key=openai_api_key)

# This route helps generate answer
@app.route("/retrieve", methods=['POST'])
def retrieve_resp():
    query = request.json.get("query")
    language = request.json.get("language", "english") 
    qa = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever(), chain_type_kwargs={"prompt": PROMPT.partial(language=language)})
    search_result = qa({"query": query})
    return {"search_result":search_result}

# This route gets list of most similar embeddings to the questions asked
@app.route("/retrieve-list", methods=['POST'])
def retrieve_list():
    query = request.json.get("query")
    k = request.json.get("k", 4)
    docs_list = vectorstore.similarity_search(query, k)
    return {"docs_list": str(docs_list)}


# Contextual compression implementation
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
# this function uses Cohere rerand method to perform Contextual Compression
def compression(k, top_n):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    compressor = CohereRerank(model='rerank-multilingual-v2.0', top_n=top_n )
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
    return compression_retriever

# This route helps generate answer using Contextual Compression
@app.route("/retrieve-compr", methods=['POST'])
def retrieve_compressed_resp():
    query = request.json.get("query")
    k = request.json.get("k", 9)
    top_n = request.json.get("top_n", 3)
    language = request.json.get("language", "english")
    compression_retriever = compression(k, top_n)
    qa = RetrievalQA.from_chain_type(llm, retriever=compression_retriever, chain_type_kwargs={"prompt": PROMPT.partial(language=language)})
    search_result = qa({"query": query})
    return {"search_result":search_result}

# This route gets list of most similar embeddings to the questions asked with Contextual Compression
@app.route("/retrieve-compr-list", methods=['POST'])
def retrieve_compressed_list():
    query = request.json.get("query")
    k = request.json.get("k", 9)
    top_n = request.json.get("top_n", 3)
    compression_retriever = compression(k, top_n)
    compressed_docs_list = compression_retriever.get_relevant_documents(query)
    return {"compressed_docs_list":str(compressed_docs_list)}

# Parsing the user input
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
# Defining user input
class UserInput(BaseModel):
    question: str = Field(description="question asked by a user")
    language: str = Field(description="language requested by the user to respond in")

# Set up a parser + inject instructions into the prompt template.
parser = PydanticOutputParser(pydantic_object=UserInput)

prompt = PromptTemplate(
    template="Take the user input which contains a question and a language to return results in, and extract the question and language. Extracted question should not have language in it.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)
memory = ConversationBufferWindowMemory( k=3, memory_key="chat_history", return_messages=True)

# This route allows to chat with our application without historical chat context
@app.route("/chat-no-history", methods=['POST'])
def chat_no_history():
    query = request.json.get("query")
    k = request.json.get("k", 9)
    top_n = request.json.get("top_n", 3)
    compression_retriever = compression(k, top_n)
    _input = prompt.format_prompt(query=query)
    output = llm(_input.to_string())
    parsed_results = parser.parse(output)
    language = parsed_results.language or "english"
    qa = RetrievalQA.from_chain_type(llm, retriever=compression_retriever, chain_type_kwargs={"prompt": PROMPT.partial(language=language)})
    search_result = qa({"query": parsed_results.question})
    return {"search_result":search_result['result']}

# This route allows to chat with our application with history
@app.route("/chat-with-history", methods=['POST'])
def chat_history():
    query = request.json.get("query")
    k = request.json.get("k", 9)
    top_n = request.json.get("top_n", 3)
    compression_retriever = compression(k, top_n)
    _input = prompt.format_prompt(query=query)
    output = llm(_input.to_string())
    parsed_results = parser.parse(output)
    language = parsed_results.language or "english"
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=compression_retriever,memory=memory, combine_docs_chain_kwargs={"prompt": PROMPT.partial(language=language)})
    search_result = qa({"question": parsed_results.question})
    return {"search_result":search_result['answer']}
