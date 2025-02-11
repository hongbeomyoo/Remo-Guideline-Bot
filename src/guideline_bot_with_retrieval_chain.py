import os
import json
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

class RetrievalGuidelineBot:
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