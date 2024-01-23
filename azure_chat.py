import os
from openai import AzureOpenAI
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import re

class AZURE_chat:
  def __init__(self, openai_key: str, azure_key: str, endpoint: str, deployment_name: str, max_token: int = 500):
    os.environ['OPENAI_API_KEY'] = openai_key
    os.environ["AZURE_OPENAI_KEY"] = azure_key
    os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
    self.embedding = OpenAIEmbeddings()
    self.db = FAISS.load_local('faiss_index', self.embedding)
    self.deployment_name = deployment_name 
    self.max_token = max_token
  
  def search_db (self, query: str) -> str:
    temp_result = self.db.similarity_search(query)
    result = ""
    for i in temp_result:
        result += i.page_content
    return result.replace("\n", " ")
  
  def prepare_prompt (self, query: str, history: str) -> str:
    template = """
    You are a helpful, polite, fact-based assistant who cracks lame jokes in Singlish.
    You are a personalised helper for the course MS0003 Data Science and Artificial Intelligence. The module code is MS0003. 
    Your job is to help them answer questions abotu the course and course content.
    Here are some details about the course.
    The course professors are Professor Leonard Ng Wei Tat and Professor Kedar Hippalgaonkar.
    The teaching assistants are Maung Thway, Pepe, Andy Paul Chen, Eleonore, Nong Wei, and Andre Lim.
    You should be able to deal with course-related enwquiries, both administrative and content-wise.
    The course has two CAs, CA1 on Week 6 and CA2 on Week 10. 
    THe course scoring breakdown is 30% for CA1, 30% for CA2 and 40% for the final group project.
    CAs are individual assignments while the group project is evaluated on a individual and group basis.
    Students will form groups after the term break. Please advise them to make friends as soon as possible.
    If they ask when we are meeting, tell them we have 1, 1 hours lecture per week at LT3 on Monday's 1330 to 1420 and an 2 hour tutorial Either on Monday 1630 to 1820 or wednesday
    1530 to 1720.
    Please bring laptops for both tutorials and pen and paper for the lectures.
    
    You will answer the question in a brief and simple manner. Please provide example code when asked.
    If the student asked you about non academic related stuff, make a sarcastric joke and then politely guide the student to only chat with you about academic related content. 
    Fristly, you should refer to the history of conversation between you and the student. 
    Then, you may use the context provided below if it is useful to answer the question.

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
    client =  AzureOpenAI(
      api_key=os.getenv("AZURE_OPENAI_KEY"),  
      api_version="2023-12-01-preview",
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
      )
    completion = client.completions.create(model=self.deployment_name, prompt=prompt, max_tokens=self.max_token)
    return completion.choices[0].text

  def query_azure (self, query: str, history: str) -> str:
    prompt = self.prepare_prompt(query, history)
    print(prompt)
    query_result = self.get_completion(prompt)
    return query_result, prompt


# Author: Thway
# GitHub: https://github.com/mgthway/llm_chatbot/
