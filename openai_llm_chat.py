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

    def prepare_prompt (self, query: str) -> str:
        template = """
        You are a helpful, polite, fact-based tutor. You are teaching university students about Machine Learning and Data analysis using Python. You will answer the question in a brief and simple manner. If the student asked you about non academic related stuffs, you may politely guide the student to only chat with you about academic related content. You may use the context provided below if it is useful to answer the question. 

        Context: 
        {context}

        Question: 
        {question}

        Your Answer:
        """
        context = self.search_db(query)
        context = re.sub(r'(\w)\1{2,}', r'\1\1', context)
        return template.format(context=context, question=query)

    def get_completion(self, prompt:str) -> str:
        client = OpenAI()
        completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{'role': 'user', "content": prompt}])
        return completion.choices[0].message.content

    def query_openai (self, query: str) -> str:
        openai.api_key = self.openai_token

        prompt = self.prepare_prompt(query)
        print(prompt)
        query_result = self.get_completion(prompt)
        return query_result


