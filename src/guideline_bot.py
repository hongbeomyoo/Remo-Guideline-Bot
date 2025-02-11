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

    def create_qa_chain(self, user_question: str):
        retriever = self.vectorstore.as_retriever()
        retrieved_docs = retriever.get_relevant_documents(user_question)
        print(retrieved_docs)
        system_prompt = (
            "당신은 회사 'REMO'의 임직원들에게 회사 내규에 대해 답변해 주는 비서 역할입니다."
            "회사 내규에 관련된 질문이 아니라면, 일반적인 답변을 해 주면서 회사 내규와 관련된 질문을 해 달라고 유도하세요."
            "회사 내규에 관련된 질문이라면, 사용자의 질문 뒤에 관련 내규 문서가 첨부됩니다. 해당 내규 문서들의 내용 중, 질문과 관련있는 내용들을 참고해서 답변해 주세요."
            "답변에 어떤 규정을 참고했는지 출처를 첨부해야 합니다."
            "관련 회사 내규 규정은 다음과 같습니다.\n규정:{context}\n\n"
            "규정을 참고해서, 임직원들에게 도움이 될 수 있는 답변을 해 주세요!"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_question),
            ]
        )
        chain = create_stuff_documents_chain(self.chat_model, prompt)
        answer = chain.invoke({"context": retrieved_docs})
        return answer
    

if __name__ == "__main__":
    load_dotenv()
    json_path = os.path.join(os.path.dirname(__file__), "../data/remo_guideline.json")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    bot = GuidelineBot(json_path, openai_api_key)
    
    question = input("질문을 입력하세요: ")
    answer = bot.create_qa_chain(user_question= question)



# import os
# import json
# from langchain.docstore.document import Document
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import FAISS
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate
# from dotenv import load_dotenv

# class GuidelineBot:
#     def __init__(self, json_path: str, openai_api_key: str):
#         self.json_path = json_path
#         self.openai_api_key = openai_api_key
#         self.documents = self.load_json_documents()
#         self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
#         self.vectorstore = self.create_vector_store()
#         self.chat_model = ChatOpenAI(
#             openai_api_key=self.openai_api_key, 
#             temperature=0.7, 
#             model="chatgpt-4o-latest"
#         )
#         # 로고 파일 경로 (예: assets 폴더 내에 company_logo.png)
#         self.logo_path = os.path.join(os.path.dirname(__file__), "../data/REMO_logo.png")
    
#     def load_json_documents(self):
#         with open(self.json_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         documents = []
#         for entry in data:
#             text = f"{entry.get('title', '')}\n{entry.get('content', '')}"
#             metadata = {"section": entry.get("section", "")}
#             doc = Document(page_content=text, metadata=metadata)
#             documents.append(doc)
#         return documents

#     def create_vector_store(self):
#         vectorstore = FAISS.from_documents(self.documents, self.embeddings)
#         return vectorstore

#     def create_qa_chain(self, user_question: str):
#         retriever = self.vectorstore.as_retriever()
#         retrieved_docs = retriever.get_relevant_documents(user_question)
#         system_prompt = (
#             "당신은 회사 'REMO'의 임직원들에게 회사 내규에 대해 답변해 주는 비서 역할입니다."
#             "회사 내규에 관련된 질문이 아니라면, 일반적인 답변을 해 주면서 회사 내규와 관련된 질문을 해 달라고 유도하세요."
#             "회사 내규에 관련된 질문이라면, 사용자의 질문 뒤에 관련 내규 문서가 첨부됩니다. 해당 내규 문서들의 내용 중, 질문과 관련있는 내용들을 참고해서 답변해 주세요."
#             "답변에 어떤 규정을 참고했는지 출처를 첨부해야 합니다."
#             "관련 회사 내규 규정은 다음과 같습니다.\n규정:{context}\n\n"
#             "규정을 참고해서, 임직원들에게 도움이 될 수 있는 답변을 해 주세요!"
#         )
#         prompt = ChatPromptTemplate.from_messages(
#             [
#                 ("system", system_prompt),
#                 ("human", user_question),
#             ]
#         )
#         chain = create_stuff_documents_chain(self.chat_model, prompt)
#         answer = chain.invoke({"context": retrieved_docs})
#         return answer

#     def classify_question(self, question: str):
#         """
#         LLM 체인을 사용하여 사용자의 질문이 회사 로고 요청에 해당하는지 판단합니다.
#         프롬프트는 질문을 재구성하여 'logo_request' 혹은 'other' 중 하나를 반환하도록 설계합니다.
#         """
#         classification_prompt = (
#             "다음 질문이 회사 로고(logo) 요청에 해당하면 'logo_request'를, 그렇지 않으면 'other'를 출력하세요.\n"
#             "질문: {question}\n"
#             "답변:"
#         )
#         prompt = ChatPromptTemplate.from_template(classification_prompt)
#         # 분류 전용 체인을 생성합니다.
#         chain = create_stuff_documents_chain(self.chat_model, prompt)
#         result = chain.invoke({"question": question})
#         # LLM의 답변에서 'logo_request' 문자열이 포함되었는지 판단합니다.
#         if "logo_request" in result.lower():
#             return "logo_request"
#         else:
#             return "other"

#     def get_company_logo(self):
#         """
#         미리 서버(또는 파일 시스템)에 저장된 회사 로고 이미지 파일의 경로를 반환합니다.
#         """
#         if os.path.exists(self.logo_path):
#             return f"회사 로고 파일 경로: {self.logo_path}"
#         else:
#             return "회사 로고 파일을 찾을 수 없습니다."

#     def answer_question(self, question: str):
#         """
#         LLM을 사용하여 사용자의 질문이 로고 요청인지 분류한 후, 그 결과에 따라 적절한 답변을 반환합니다.
#         """
#         classification = self.classify_question(question)
#         if classification == "logo_request":
#             return self.get_company_logo()
#         else:
#             return self.create_qa_chain(user_question=question)

# if __name__ == "__main__":
#     load_dotenv()
#     json_path = os.path.join(os.path.dirname(__file__), "../data/remo_guideline.json")
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     bot = GuidelineBot(json_path, openai_api_key)
    
#     question = input("질문을 입력하세요: ")
#     answer = bot.answer_question(question)
#     print(answer)
