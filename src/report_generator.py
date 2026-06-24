from datetime import datetime
from pathlib import Path


def generate_report(
    article: dict,            # {"title", "body", "url", "raw_text"}
    clean_text: str,
    nouns: list[str],
    word_freq: dict[str, int],
    wordcloud_path: str,
    top_words_path: str,
    output_path: str = "report/report.md",
    top_n: int = 20,
) -> str:
    """
    분석 결과를 Markdown 보고서로 작성합니다.
    이미지는 report/ 폴더 내 파일명만 상대 경로로 참조합니다.

    반환값: 저장된 보고서 파일 경로
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    top_words = list(word_freq.items())[:top_n]
    total_tokens = len(nouns)
    unique_words = len(word_freq)
    top_total = sum(c for _, c in top_words)
    top_ratio = top_total / total_tokens * 100 if total_tokens else 0
    avg_freq = total_tokens / unique_words if unique_words else 0
    top5_words = [w for w, _ in top_words[:5]]

    wc_filename  = Path(wordcloud_path).name
    top_filename = Path(top_words_path).name

    # 상위 단어 테이블 행
    table_rows = "\n".join(
        f"| {rank} | {word} | {count} | {'█' * min(count, 30)} |"
        for rank, (word, count) in enumerate(top_words, start=1)
    )

    # 본문 미리보기 (150자)
    body_preview = article.get("body", "")[:150].replace("\n", " ")

    md = f"""# 📰 네이버 뉴스 헤드라인 텍스트 분석 보고서

> **생성 일시:** {now}  
> **분석 도구:** KoNLPy (Okt) · PyTorch · WordCloud · BeautifulSoup4

---

## 1. 수집 기사 정보

| 항목 | 내용 |
|------|------|
| **제목** | {article.get("title", "-")} |
| **출처** | [네이버 뉴스 IT/과학]({article.get("url", "#")}) |
| **본문 미리보기** | {body_preview}… |

---

## 2. 텍스트 수집 및 정제

| 구분 | 값 |
|------|----|
| 원본 텍스트 길이 | {len(article.get("raw_text", "")):,}자 |
| 정제 후 텍스트 길이 | {len(clean_text):,}자 |
| 제거된 문자 수 | {len(article.get("raw_text", "")) - len(clean_text):,}자 |
| 정제 방식 | 한글 자모·완성형 외 문자 제거, 중복 공백 정리 |

---

## 3. 형태소 분석 결과

- **형태소 분석기:** KoNLPy `Okt`
- **추출 기준:** 명사(nouns) · 2글자 이상 · 불용어 제거
- **추출된 명사 토큰 수:** {total_tokens:,}개
- **고유 단어 수:** {unique_words:,}개
- **평균 단어 빈도:** {avg_freq:.2f}회

---

## 4. 단어 빈도 계산 (PyTorch Tensor)

```
단어 → 정수 ID 매핑
  ↓ torch.tensor() 변환
  ↓ torch.bincount() 집계
  ↓ 빈도 딕셔너리 역변환
```

- 상위 {top_n}개 단어의 총 등장 횟수: **{top_total}회** (전체의 **{top_ratio:.1f}%**)

---

## 5. 워드클라우드

![워드클라우드]({wc_filename})

---

## 6. 상위 {top_n}개 단어 빈도

![상위 단어 차트]({top_filename})

### 상세 데이터

| 순위 | 단어 | 빈도 | 시각화 |
|:----:|------|:----:|--------|
{table_rows}

---

## 7. 종합 해석

분석된 기사에서 가장 많이 등장한 단어는 **{top5_words[0]}**, **{top5_words[1]}**, **{top5_words[2]}** 등으로,  
해당 기사는 주로 `{' / '.join(top5_words[:3])}` 관련 주제를 다루고 있습니다.

전체 **{unique_words}개** 고유 명사 중 상위 **{top_n}개**가 전체 빈도의 <b>{top_ratio:.1f}%</b>를 차지하여,  
텍스트의 핵심 주제가 {'비교적 집중' if top_ratio > 50 else '비교적 분산'}되어 있음을 확인할 수 있습니다.

---

*본 보고서는 자동 생성되었습니다.*
"""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(md.strip(), encoding="utf-8")

    # print(md.strip())
    print(f"\n[보고서] 마크다운 보고서 저장 완료 → {output_path}")
    return str(output_path)