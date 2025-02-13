import os
import json
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

class GuidelineOllamaBot:
    def __init__(self, json_path: str, openai_api_key: str):
        self.json_path = json_path
        self.openai_api_key = openai_api_key
        self.documents = self.load_json_documents()
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.vectorstore = self.create_vector_store()
        # ChatOpenAI 인스턴스를 Ollama API를 사용하도록 수정:
        self.chat_model = ChatOpenAI(
            openai_api_key="dummy",                   # Ollama는 API 키가 필요 없으므로 더미 값 사용
            openai_api_base="http://localhost:6203/v1/",  # Ollama API 엔드포인트 (환경에 따라 변경)
            temperature=0.1,
            model="deepseek-r1:671b"                    # 지정한 모델 이름
        )
        self.logo_path = os.path.join(os.path.dirname(__file__), "../data/logo.jpg")
    
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

    def create_qa_chain(self, query: str):
        # retriever를 통해 사용자의 쿼리와 관련된 문서를 검색합니다.
        retriever = self.vectorstore.as_retriever()
        retrieved_docs = retriever.get_relevant_documents(query)
        system_prompt = (
            "당신은 회사 'REMO'의 임직원들에게 회사 내규에 대해 답변해 주는 비서 역할입니다. "
            "회사 내규에 관련된 질문이 아니라면, 일반적인 답변을 해 주면서 회사 내규와 관련된 질문을 해 달라고 유도하세요. "
            "회사 내규에 관련된 질문이라면, 사용자의 질문 뒤에 관련 내규 문서가 첨부됩니다. 해당 내규 문서들의 내용 중, 질문과 관련있는 내용들을 참고해서 답변해 주세요. "
            "관련 회사 내규 규정은 다음과 같습니다.\n규정:{context}\n\n"
            "규정이 사용자의 질문과 관련이 없다면, 더 자세한 질문을 유도하세요."
            "답변에 어떤 규정을 참고했는지 출처를 첨부해야 합니다. "
            "규정 양식은 답변의 마지막에 '출처: 제oo조(규정 종류)' 와 같은 형식으로 제공해 주세요."
            "규정을 참고해서, 임직원들에게 도움이 될 수 있는 답변을 해 주세요!"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", query)
        ])
        chain = create_stuff_documents_chain(self.chat_model, prompt)
        answer = chain.invoke({"context": retrieved_docs})
        return answer

    def get_company_logo(self):
        if os.path.exists(self.logo_path):
            return f"회사 로고 파일 경로:{self.logo_path}"
        else:
            return "회사 로고 파일을 찾을 수 없습니다."

    def load_toc(self):
        toc_path = os.path.join(os.path.dirname(self.json_path), "../data/remo_toc.json")
        try:
            with open(toc_path, "r", encoding="utf-8") as f:
                toc_data = json.load(f)
            toc_text = json.dumps(toc_data, ensure_ascii=False, indent=2)
            prompt_template = ChatPromptTemplate.from_template(
                "아래의 JSON 형식 목차 데이터를 보기 좋은 텍스트 형태로 정리해 주세요.\n\n"
                "JSON 데이터:\n{toc}\n\n"
                "사용자가 쉽게 이해할 수 있도록 깔끔한 형식으로 정리해 주세요."
            )
            # LLM 체인 실행
            formatted_toc = self.chat_model.invoke(prompt_template.format(toc=toc_text))
            return formatted_toc.content.strip()
        except Exception as e:
            return f"목차 정보를 불러오는 중 오류가 발생했습니다: {e}"

    def classify_question(self, question: str):
        classification_prompt = ChatPromptTemplate.from_template(
            "다음 질문에 대해, 만약 질문이 회사 로고 요청(예: '회사의 로고를 제공해 줘')에 해당하면 'logo_request', "
            "만약 질문이 회사 내규의 목차를 보여달라는 요청(예: '회사 내규의 목차를 보여줘')에 해당하면 'toc_request'를 출력하고, "
            "그렇지 않다면 질문에서 가장 핵심적인 단어(예: '연차', '근로수당' 등)를 한 단어로 출력하세요.\n"
            "질문: {question}\n"
            "답변:"
        )

        classification_chain = classification_prompt | self.chat_model | RunnablePassthrough()
        
        result = classification_chain.invoke({"question": question})
        return result.content.strip().lower()

    def answer_question(self, question: str):
        """
        질문을 LLM 체인을 통해 분류한 후,
         - 'logo_request'이면 get_company_logo()를 반환하고,
         - 'toc_request'이면 load_toc()를 반환하며,
         - 그 외에는 분류 체인이 추출한 핵심 키워드를 검색 쿼리로 사용해 create_qa_chain()을 실행합니다.
        """
        label = self.classify_question(question)
        print(label)
        if label == "logo_request":
            return self.get_company_logo()
        elif label == "toc_request":
            return self.load_toc()
        else:
            # label(예: "연차"나 "근로수당")를 검색 쿼리로 사용합니다.
            return self.create_qa_chain(query=label)

if __name__ == "__main__":
    load_dotenv()
    json_path = os.path.join(os.path.dirname(__file__), "../data/remo_guideline.json")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    bot = GuidelineOllamaBot(json_path)
    
    question = input("질문을 입력하세요: ")
    answer = bot.answer_question(question)
    print(answer)
