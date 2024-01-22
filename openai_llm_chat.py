from openai import OpenAI
import os
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

class OPENAI_chat:
    def __init__(self, key: str):
        self.openai_token = key
        os.environ['OPENAI_API_KEY'] = str(self.openai_token)
        self.embedding = OpenAIEmbeddings()
        self.db = FAISS.load_local('faiss_index', self.embedding)

    def search_db (self, query: str) -> str:
        temp_result = self.db.similarity_search(query)
        result = ""
        for i in temp_result:
            result += i.page_content
        return result.replace("\n", " ")

    def prepare_prompt (self, query: str, history: str) -> str:
        template = """
        You are a helpful, polite, fact-based assistant. You are teaching university students about Data Science and Artificial Intelligence using Python. The module code is MS0003. You will answer the question in a brief and simple manner. If the student asked you about non academic related stuffs, you may politely guide the student to only chat with you about academic related content. Fristly, you should refer to the history of conversation between you and the student. Then, you may use the context provided below if it is useful to answer the question.

        History:
        {history}

        Context:
        {context}

        Question:
        {question}

        Your Answer:
        """
        context = self.search_db(query)
        context = re.sub(r'(\w)\1{2,}', r'\1\1', context) #remove character level duplicates
        return template.format(context=context, question=query, history=history)

    def get_completion(self, prompt:str) -> str:
        client = OpenAI()
        completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{'role': 'user', "content": prompt}])
        return completion.choices[0].message.content

    def query_openai (self, query: str, history: str) -> str:
        prompt = self.prepare_prompt(query, history)
        print(prompt)
        query_result = self.get_completion(prompt)
        return query_result, prompt


# Author: Thway
# GitHub: https://github.com/mgthway/llm_chatbot/
