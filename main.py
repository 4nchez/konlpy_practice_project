import sys
from pathlib import Path

# src 폴더를 모듈 탐색 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.text_collector import collect_news, clean_text
from src.wordcloud_generator import (
    analyze_morpheme,
    calc_word_frequency,
    generate_wordcloud,
    plot_top_words,
)
from src.report_generator import generate_report

# CONFIG
REPORT_DIR     = Path("report")
WORDCLOUD_PATH = str(REPORT_DIR / "wordcloud.png")
TOP_WORDS_PATH = str(REPORT_DIR / "top_words.png")
REPORT_PATH    = str(REPORT_DIR / "report.md")
TOP_N          = 20

# report 폴더가 없으면 자동 생성
REPORT_DIR.mkdir(exist_ok=True)


def main() -> None:
    """
    전체 분석 파이프라인:
      1. 네이버 뉴스 IT/과학 헤드라인 첫 번째 기사 크롤링
      2. 텍스트 정제 (한글만 유지, 공백 정리)
      3. 형태소 분석 — Okt 명사 추출 + 불용어 제거
      4. PyTorch Tensor 기반 단어 빈도 계산
      5. 워드클라우드 생성 (report/wordcloud.png)
      6. 상위 20개 단어 막대 차트 생성 (report/top_words.png)
      7. Markdown 보고서 생성 (report/report.md)
    """
    print("=" * 60)
    print("   네이버 뉴스 헤드라인 텍스트 분석 파이프라인 시작")
    print("=" * 60 + "\n")

    # Step 1 · 크롤링
    article = collect_news()

    # Step 2 · 정제
    cleaned = clean_text(article["raw_text"])

    # Step 3 · 형태소 분석
    nouns = analyze_morpheme(cleaned)

    # Step 4 · 단어 빈도 계산
    word_freq = calc_word_frequency(nouns)

    # Step 5 · 워드클라우드
    wc_path = generate_wordcloud(word_freq, output_path=WORDCLOUD_PATH)

    # Step 6 · 상위 단어 차트
    top_path = plot_top_words(word_freq, top_n=TOP_N, output_path=TOP_WORDS_PATH)

    # Step 7 · 보고서
    report_path = generate_report(
        article=article,
        clean_text=cleaned,
        nouns=nouns,
        word_freq=word_freq,
        wordcloud_path=wc_path,
        top_words_path=top_path,
        output_path=REPORT_PATH,
        top_n=TOP_N,
    )

    print("\n" + "=" * 60)
    print("   분석 완료! 생성된 파일:")
    print(f"   - 워드클라우드    : {wc_path}")
    print(f"   - 단어 빈도 차트   : {top_path}")
    print(f"   - 분석 보고서 (MD) : {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()