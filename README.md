# konlpy_practice_project

자연어 텍스트 데이터 전처리 프로젝트 과제

프로젝트명 : konlpy_practice_project
깃 리포지토리 이름도 동일하게 생성함
main 브렌치 사용함

뉴스 기사, PDF 텍스트, 크롤링 데이터 중 하나를 수집하여 다음 과정을 수행하시오.
```
텍스트 수집 # 네이버 뉴스 1건
텍스트 정제
형태소 분석
불용어 제거
단어 빈도 계산
PyTorch Tensor 변환
워드클라우드 생성
상위 20개 단어 시각화
결과 분석 보고서 작성
```
작성한 모든 내용을 깃허브에 푸시하시오.

내일 수업 시작 전까지 깃 주소를 디스코드 '실시간' 채널에 업로드하시오.

---
 
##  프로젝트 구조
 
```
project/
├── main.py                    # 전체 파이프라인 실행 진입점
├── README.md                  # 프로젝트 설명 (이 파일)
│
├── src/
│   ├── text_collector.py      # 뉴스 크롤링 + 텍스트 정제
│   ├── wordcloud_generator.py # 형태소 분석 · 빈도 계산 · 시각화
│   └── report_generator.py    # Markdown 보고서 생성
│
└── (실행 후 생성)
    └── report/
        ├── wordcloud.png      # 워드클라우드 이미지
        ├── top_words.png      # 상위 20개 단어 빈도 차트
        └── report.md          # 분석 보고서 (이미지 상대 경로 참조)
```
 
---

##  실행
 
```bash
python main.py
```
 
실행하면 아래 파일이 현재 디렉터리에 생성됩니다.
 
| 파일 | 설명 |
|------|------|
| `wordcloud.png` | 워드클라우드 이미지 |
| `top_words.png` | 상위 20개 단어 빈도 수평 막대 차트 |
| `report.md` | 전체 분석 결과 Markdown 보고서 |
 
---