# Project Name

Cohere Weviate Wikipedia Retrieval using LangChain

## Description

A backend API to perform search over Wikipedia using LangChain, Cohere and Weaviate

## Getting Started

### Prerequisites

To use this project, you will need to have the following installed on your machine:

- Python 3.8 or above
- pip
- virtualenv

### Installing

To install and run this project on your local machine, follow these steps:

1. Clone the repository onto your machine using the following command:

```
git clone https://github.com/menloparklab/cohere-weviate-wikipedia-retrieval
```

2. Create a virtual environment for the project using the following command:

```
python3 -m venv venv
```

3. Activate the virtual environment using the following command:

```
source venv/bin/activate
```

4. Install the project dependencies using the following command:

```
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory of the project and add your API keys. You can use the `.env.copy` file as a template.

    Weaviate api keys and url are left intentionally. These are read only api provided by Weaviate for demo purposes.

6. To test your output and results, use the provided jupyter notebook. You can easily run this in Colab as well.



7. To start the API routes using Flask, run the following command:

```
gunicorn app:app
```

### Below are the endpoints and examples to call them

1. `/retrieve`
   
   This endpoint generates an answer to a query using retrieval-based QA. To use this endpoint, send a POST request to `http://<host>/retrieve` with the following JSON payload:

   ```
   {
       "query": "<your query>",
       "language": "<language>"
   }
   ```

   The `query` field should contain the query for which you want to generate an answer. The `language` field is optional and should be set to the language of the query. If the `language` field is not set, the default language is English.

   Example JSON:

   ```
   {
       "query": "What is the capital of France?",
       "language": "english"
   }
   ```

2. `/retrieve-list`

   This endpoint returns a list of most similar embeddings to the query using the vectorstore. To use this endpoint, send a POST request to `http://<host>/retrieve-list` with the following JSON payload:

   ```
   {
       "query": "<your query>",
       "k": <k>
   }
   ```

   The `query` field should contain the query for which you want to generate an answer. The `k` field is optional and should be set to the number of most similar embeddings you want to retrieve. If the `k` field is not set, the default value is 4.

   Example JSON:

   ```
   {
       "query": "What is the capital of France?",
       "k": 4
   }
   ```

3. `/retrieve-compr`

   This endpoint generates an answer to a query using Contextual Compression. To use this endpoint, send a POST request to `http://<host>/retrieve-compr` with the following JSON payload:

   ```
   {
       "query": "<your query>",
       "k": <k>,
       "top_n": <top_n>,
       "language": "<language>"
   }
   ```

   The `query` field should contain the query for which you want to generate an answer. The `k` and `top_n` fields are optional and should be set to the number of most similar embeddings you want to retrieve and the number of compressed documents you want to consider, respectively. If the `k` and `top_n` fields are not set, the default values are 9 and 3, respectively. The `language` field is optional and should be set to the language of the query. If the `language` field is not set, the default language is English.

   Example JSON:

   ```
   {
       "query": "What is the capital of France?",
       "k": 9,
       "top_n": 3,
       "language": "english"
   }
   ```

4. `/retrieve-compr-list`

   This endpoint returns a list of most similar embeddings to the query using Contextual Compression. To use this endpoint, send a POST request to `http://<host>/retrieve-compr-list` with the following JSON payload:

   ```
   {
       "query": "<your query>",
       "k": <k>,
       "top_n": <top_n>
   }
   ```

   The `query` field should contain the query for which you want to generate an answer. The `k` and `top_n` fields are optional and should be set to the number of most similar embeddings you want to retrieve and the number of compressed documents you want to consider, respectively. If the `k` and `top_n` fields are not set, the default values are 9 and 3, respectively.


5. `/chat-no-history`

    This route allows the user to chat with the application without any historical chat context. It accepts the following parameters in a JSON request body:
    - `query`: The user's query. Required.
    - `k`: An integer value for the number of results to retrieve from the model. Optional, defaults to 9.
    - `top_n`: An integer value for the number of top search results to consider for generating an answer. Optional, defaults to 3.

    The route then uses the `compression` function to retrieve the top `k` results from the model, and constructs a prompt using the user's query. The prompt is passed to the machine learning model, and the output is parsed using a `parser` object. If a language is detected in the output, it is used for subsequent queries, otherwise the default is English. The `RetrievalQA` class is used to generate a response using the `qa` object, and the search result is returned as a JSON response.

    Example JSON

    ```json
    {
        "query": "What is the capital of France?",
        "k": 5,
        "top_n": 2
    }
    ```

    Example Response

    ```json
    {
        "search_result": "Paris is the capital of France."
    }
    ```

6. `/chat-with-history`

    This route allows the user to chat with the application using historical chat context. It accepts the same parameters as the previous route:
    - `query`: The user's query. Required.
    - `k`: An integer value for the number of results to retrieve from the model. Optional, defaults to 9.
    - `top_n`: An integer value for the number of top search results to consider for generating an answer. Optional, defaults to 3.

    In addition, this route maintains a memory of past conversations using the `ConversationBufferMemory` class, and generates responses using the `ConversationalRetrievalChain` class. The memory key for this route is set to `"chat_history"`. The search result is returned as a JSON response.

    Example Json

    ```json
    {
        "query": "What is the capital of Spain?",
        "k": 3,
        "top_n": 1
    }
    ```

    Example Response

    ```json
    {
        "search_result": "The capital of Spain is Madrid."
    }
    ```

  
