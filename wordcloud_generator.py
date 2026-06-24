import os
import torch
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from konlpy.tag import Okt

# CONFIG
STOPWORDS = {
    "있다", "하다", "이다", "되다", "않다", "없다", "같다", "위해",
    "통해", "대해", "관련", "이후", "지난", "오는", "현재", "최근",
    "것이", "것을", "수도", "때문", "이번", "다양", "함께", "활용",
    "강화", "마련", "주목", "전망", "진행", "나타", "이루", "아끼",
    "가져", "제기", "높아", "신설", "편성", "집중", "박차", "힘쓰",
    "기자", "뉴스", "연합", "뉴시스", "헤럴드", "기사", "제공",
    "저작권", "무단", "배포", "금지", "저작", "재배포", "ⓒ",
}

# 폰트 탐색
def _get_font_path() -> str:
    candidates = [
        "C:/Windows/Fonts/malgun.ttf",          # Windows
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
        "/Library/Fonts/AppleGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
        "/usr/share/fonts/nanum/NanumGothic.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    for font in fm.findSystemFonts():
        if any(k in font.lower() for k in ("malgun", "nanum", "gothic", "gulim", "batang")):
            return font
    raise FileNotFoundError(
        "한글 폰트를 찾을 수 없습니다. NanumGothic 등 한글 폰트를 설치해 주세요."
    )


# 형태소 분석
def analyze_morpheme(clean_text: str) -> list[str]:
    """Okt로 명사 추출 후 불용어·단음절 제거."""
    print("[형태소] Okt 형태소 분석 시작...")
    okt = Okt()
    nouns = okt.nouns(clean_text)
    nouns = [n for n in nouns if len(n) > 1 and n not in STOPWORDS]
    print(f"[형태소] 추출 명사 수: {len(nouns)}개")
    print(f"[형태소] 미리보기: {nouns[:15]}\n")
    return nouns


# PyTorch 빈도 계산
def calc_word_frequency(nouns: list[str]) -> dict[str, int]:
    """torch.bincount()를 이용한 단어 빈도 계산."""
    vocab = sorted(set(nouns))
    word_to_id = {word: idx for idx, word in enumerate(vocab)}
    word_ids_tensor = torch.tensor([word_to_id[w] for w in nouns])
    counts_tensor = torch.bincount(word_ids_tensor)

    word_freq = {
        vocab[i]: int(counts_tensor[i].item())
        for i in range(len(vocab))
    }
    word_freq = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True))

    print("[빈도] PyTorch Tensor 기반 빈도 계산 완료")
    top10 = {k: v for k, v in list(word_freq.items())[:10]}
    print(f"[빈도] 상위 10개: {top10}\n")
    return word_freq


# 워드클라우드 생성
def generate_wordcloud(word_freq: dict[str, int], output_path: str = "wordcloud.png") -> str:
    """워드클라우드를 생성하고 PNG로 저장합니다."""
    font_path = _get_font_path()
    print(f"[워드클라우드] 폰트: {font_path}")

    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        width=900,
        height=600,
        max_words=100,
        colormap="RdYlBu",
    ).generate_from_frequencies(word_freq)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("네이버 뉴스 헤드라인 워드클라우드", fontsize=18, pad=15,
                 fontproperties=fm.FontProperties(fname=font_path))
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"[워드클라우드] 저장 완료 → {output_path}\n")
    return output_path


# 상위 N 단어 막대 차트
def plot_top_words(
    word_freq: dict[str, int],
    top_n: int = 20,
    output_path: str = "top_words.png",
) -> str:
    """상위 N개 단어 빈도 수평 막대 차트를 저장합니다."""
    top_items = list(word_freq.items())[:top_n]
    words, counts = zip(*top_items)

    font_path = _get_font_path()
    fp = fm.FontProperties(fname=font_path)

    cmap = plt.get_cmap("Blues", top_n + 4)
    colors = [cmap(i + 4) for i in range(top_n)]

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(
        list(reversed(words)),
        list(reversed(counts)),
        color=list(reversed(colors)),
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_xlabel("빈도수", fontproperties=fp, fontsize=12)
    ax.set_title(f"상위 {top_n}개 단어 빈도", fontproperties=fp, fontsize=16)
    ax.set_yticklabels(list(reversed(words)), fontproperties=fp, fontsize=11)

    for bar, cnt in zip(bars, list(reversed(counts))):
        ax.text(
            bar.get_width() + 0.05,
            bar.get_y() + bar.get_height() / 2,
            str(cnt),
            va="center",
            fontsize=10,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"[시각화] 상위 {top_n}개 차트 저장 완료 → {output_path}\n")
    return output_path