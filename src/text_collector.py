import re
import time
import requests
from bs4 import BeautifulSoup

# CONFIG
SECTION_URL = "https://news.naver.com/section/103"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://news.naver.com/",
    "Accept-Language": "ko-KR,ko;q=0.9",
}


# 1) Crawling
def _get_headline_article_url(session: requests.Session) -> tuple[str, str]:
    """
    https://news.naver.com/section/103 에서
    '헤드라인 뉴스' 블록의 첫 번째 기사 URL과 제목을 반환합니다.
    """
    resp = session.get(SECTION_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # JS:
    # document.getElementsByClassName('sa_list')[0]
    #   .getElementsByClassName('sa_text')[0]
    #   .getElementsByTagName('a')[0]
    first_a = soup.select_one(".sa_list .sa_text a")

    if not first_a:
        raise ValueError(
            "기사 링크를 찾지 못했습니다. 네이버 HTML 구조가 변경되었을 수 있습니다."
        )

    article_url = first_a["href"]
    if article_url.startswith("/"):
        article_url = "https://news.naver.com" + article_url

    title = first_a.get_text(strip=True)
    return article_url, title


def _fetch_article_body(session: requests.Session, url: str) -> tuple[str, str, str]:
    """
    기사 URL에서 제목과 본문을 가져옵니다.
    반환: (제목, 본문, 기사_URL)
    """
    time.sleep(0.5)  # 서버 부하 방지
    resp = session.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # 제목
    title_tag = (
        soup.find("h2", id="title_area")
        or soup.find("h3", id="articleTitle")
        or soup.find("h2", class_=re.compile(r"title"))
    )
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    # 본문
    body_tag = (
        soup.find("article", id="dic_area")
        or soup.find("div", id="articleBodyContents")
        or soup.find("div", class_=re.compile(r"newsct_article|article_body"))
    )
    if body_tag:
        # 광고·스크립트 제거
        for tag in body_tag(["script", "style", "figure", "figcaption"]):
            tag.decompose()
        body = body_tag.get_text(separator=" ", strip=True)
    else:
        body = ""

    return title, body, url


def collect_news(section_url: str = SECTION_URL) -> dict:
    """
    네이버 뉴스 IT/과학 섹션 헤드라인 첫 번째 기사를 수집합니다.

    반환:
        {
            "title": str,
            "body": str,
            "url": str,
            "raw_text": str  # 제목 + 본문 합본
        }
    """
    print("[수집] 네이버 뉴스 IT/과학 섹션 접속 중...")
    session = requests.Session()

    try:
        article_url, preview_title = _get_headline_article_url(session)
        print(f"[수집] 헤드라인 기사 URL: {article_url}")

        title, body, url = _fetch_article_body(session, article_url)
        print(f"[수집] 기사 제목: {title}")
        print(f"[수집] 본문 길이: {len(body)}자\n")

        raw_text = f"{title}\n\n{body}"
        return {"title": title, "body": body, "url": url, "raw_text": raw_text}

    except Exception as exc:
        print(f"[수집 오류] {exc}")
        print("[수집] 크롤링에 실패했습니다. 네트워크 또는 HTML 구조를 확인해 주세요.")
        raise


# 2) Refine
def clean_text(raw_text: str) -> str:
    """
    텍스트를 정제합니다.
    - 한글 자모 및 완성형 한글만 유지
    - 중복 공백 제거
    """
    cleaned = re.sub(r"[^ㄱ-ㅎㅏ-ㅣ가-힣\s]", "", raw_text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    print("[정제] 텍스트 정제 완료")
    print(f"[정제] 정제 후 길이: {len(cleaned)}자")
    print(f"[정제] 미리보기: {cleaned[:80]}...\n")
    return cleaned