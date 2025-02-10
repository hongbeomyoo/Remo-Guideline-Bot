# import os
# import json
# from langchain.docstore.document import Document
# from langchain_openai import OpenAIEmbeddings
# import faiss
# from langchain_community.vectorstores import FAISS
# from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_openai import ChatOpenAI
# from langchain.chains import RetrievalQA

# class GuidelineBot:
#     def __init__(self, json_path: str, openai_api_key: str):
#         self.json_path = json_path
#         self.openai_api_key = openai_api_key
#         self.documents = self.load_json_documents()
#         self.embeddings = OpenAIEmbeddings(openai_api_key = self.openai_api_key)
#         self.vectorstore = self.create_vector_store()
#         self.chat_model = ChatOpenAI(openai_api_key=self.openai_api_key, temperature=0.7, model="chatgpt-4o-latest")
#         self.qa_chain = RetrievalQA.from_chain_type(
#             llm=self.chat_model,
#             chain_type="stuff",
#             retriever=self.vectorstore.as_retriever()
#         )

#     def load_json_documents(self):
#         with open(self.json_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         documents = []
#         for entry in data:
#             # 제목과 내용을 결합하여 하나의 텍스트로 구성합니다.
#             text = f"{entry.get('title', '')}\n{entry.get('content', '')}"
#             metadata = {"section": entry.get("section", "")}
#             doc = Document(page_content=text, metadata=metadata)
#             documents.append(doc)
#         return documents

#     def create_vector_store(self):
#         """
#         문서 리스트를 기반으로 FAISS 벡터 스토어를 생성합니다.
        
#         - OpenAIEmbeddings를 사용해 각 Document의 임베딩을 생성한 후,
#         - FAISS.from_documents()를 호출하여 임베딩 벡터들을 인덱싱합니다.
#         """
#         vectorstore = FAISS.from_documents(self.documents, self.embeddings)
#         print('create vectorstore')
#         return vectorstore

#     def search_relevant(self, query: str):
#         """
#         사용자 질문에 대해 FAISS 벡터 스토어를 이용해 관련 문서를 검색합니다.
        
#         - query: 사용자가 입력한 질문 텍스트.
#         - retriever.get_relevant_documents() 메서드를 사용하여 유사도가 높은 Document 리스트를 반환합니다.
#         """
#         retriever = self.vectorstore.as_retriever()
#         results = retriever.get_relevant_documents(query)
#         print(results)
#         return results

#     def answer_question(self, question: str):
#         """
#         사용자 질문을 받아 QA 체인을 통해 답변을 생성합니다.
        
#         - 내부적으로 RetrievalQA 체인이 사용자 질문을 처리하면서 FAISS로부터 관련 문서를 가져오고,
#           LLM에게 해당 문맥을 제공하여 최종 답변을 생성합니다.
#         - 반환 값은 LLM이 구성한 답변 문자열입니다.
#         """
#         result = self.qa_chain.invoke({"query": question})
#         return result.get("answer", "")

# if __name__ == "__main__":
#     json_path = os.path.join(os.path.dirname(__file__), "../data/remo_guideline.json")
#     load_dotenv()
#     openai_api_key = os.getenv("OPENAI_API_KEY"),


#     bot = GuidelineBot(json_path, openai_api_key)
    
#     question = input("질문을 입력하세요: ")
#     document = bot.search_relevant(question)
#     answer = bot.answer_question(question)
#     print(answer)

import os
import json
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

class GuidelineBot:
    def __init__(self, json_path: str, openai_api_key: str):
        self.json_path = json_path
        self.openai_api_key = openai_api_key
        self.documents = self.load_json_documents()
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.vectorstore = self.create_vector_store()
        self.chat_model = ChatOpenAI(openai_api_key=self.openai_api_key, temperature=0.7, model="chatgpt-4o-latest")
        self.qa_chain = self.create_qa_chain()

    def load_json_documents(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        documents = []
        for entry in data:
            text = f"{entry.get('title', '')}\n{entry.get('content', '')}"
            metadata = {"section": entry.get("section", "")}
            doc = Document(page_content=text, metadata=metadata)
            documents.append(doc)
        return documents

    def create_vector_store(self):
        vectorstore = FAISS.from_documents(self.documents, self.embeddings)
        return vectorstore

    def create_qa_chain(self):
        retriever = self.vectorstore.as_retriever()
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise.\n\n{context}"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        combine_docs_chain = create_stuff_documents_chain(self.chat_model, prompt)
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
        return retrieval_chain

    def answer_question(self, question: str):
        result = self.qa_chain.invoke({"input": question})
        return result.get("answer", "")

if __name__ == "__main__":
    load_dotenv()
    json_path = os.path.join(os.path.dirname(__file__), "../data/remo_guideline.json")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    bot = GuidelineBot(json_path, openai_api_key)
    
    question = input("질문을 입력하세요: ")
    answer = bot.answer_question(question)
    print(answer)
