import re
import json
import textract

def parse_company_regulations(text):
    results = []

    # 챕터 패턴: "제1장", "제2장" 등
    chapter_pattern = re.compile(r'(제\d+장)')
    # 챕터별 위치 찾기
    chapters = list(chapter_pattern.finditer(text))
    chapter_positions = [(m.start(), m.group(1)) for m in chapters]

    for idx, (start_pos, chapter_title) in enumerate(chapter_positions):
        chapter_start = start_pos
        chapter_end = chapter_positions[idx + 1][0] if idx + 1 < len(chapter_positions) else len(text)
        chapter_text = text[chapter_start:chapter_end]

        # "제"와 "조("를 기준으로 조의 시작점을 찾아 분리
        article_pattern = re.compile(r'(제\d+조\()')
        article_matches = list(article_pattern.finditer(chapter_text))

        if article_matches:
            # 각 조의 시작 위치를 리스트로 저장
            article_starts = [m.start() for m in article_matches]
            # 마지막 조의 끝은 챕터의 끝
            article_starts.append(len(chapter_text))

            for i in range(len(article_matches)):
                article_block = chapter_text[article_starts[i]:article_starts[i+1]].strip()
                # 첫 번째 ") + 공백" 을 기준으로 분리
                split_index = article_block.find(") ")
                if split_index != -1:
                    # ") "의 ")"까지 포함
                    title = article_block[:split_index+1].strip()  
                    # ") " 이후의 내용
                    content = article_block[split_index+2:].strip()   
                else:
                    title = article_block
                    content = ""

                # content 항목에서 \n 문자를 제거 (공백으로 대체)
                content = content.replace("\n", " ")

                obj = {
                    "section": chapter_title,
                    "title": title,
                    "content": content
                }
                results.append(obj)
        else:
            obj = {
                "section": chapter_title,
                "title": "",
                "content": chapter_text.strip().replace("\n", "")
            }
            results.append(obj)

    return results

if __name__ == "__main__":
    file_path = "../data/remo_guideline.doc"
    try:
        raw_bytes = textract.process(file_path)
        doc_text = raw_bytes.decode('utf-8')
    except Exception as e:
        print(f"파일 읽기 실패: {e}")
        exit(1)

    parsed_data = parse_company_regulations(doc_text)
    json_output = json.dumps(parsed_data, ensure_ascii=False, indent=2)
    
    with open('../data/remo_guideline.json', 'w', encoding='utf-8') as f:
        f.write(json_output)
