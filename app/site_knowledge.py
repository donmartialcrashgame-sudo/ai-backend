import re
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

SITE_URL = "https://game-api.online"
SITEMAP_URL = f"{SITE_URL}/sitemap.xml"
CACHE_TTL = 600
MAX_PAGES = 20
MAX_PAGE_CHARS = 12000
MAX_CONTEXT_CHARS = 3000

_cache = {"expires": 0.0, "pages": {}}


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Game-API-AI/1.0"})
    with urlopen(request, timeout=8) as response:
        raw = response.read(MAX_PAGE_CHARS * 4)
    parser = TextParser()
    parser.feed(raw.decode("utf-8", errors="ignore"))
    return " ".join(parser.parts)[:MAX_PAGE_CHARS]


def discover_pages():
    urls = [SITE_URL + "/"]
    try:
        xml = fetch_text(SITEMAP_URL)
        found = re.findall(r"https?://[^\s<>]+", xml)
        for url in found:
            url = url.rstrip("/ ")
            parsed = urlparse(url)
            if parsed.netloc == urlparse(SITE_URL).netloc and url not in urls:
                urls.append(url)
            if len(urls) >= MAX_PAGES:
                break
    except Exception:
        pass
    return urls


def load_pages():
    now = time.time()
    if _cache["pages"] and now < _cache["expires"]:
        return _cache["pages"]

    pages = {}
    for url in discover_pages():
        try:
            text = fetch_text(url)
            if text:
                pages[url] = text
        except Exception:
            continue

    _cache["pages"] = pages
    _cache["expires"] = now + CACHE_TTL
    return pages


def search_site(query: str) -> str:
    """Search game-api.online pages and return a small relevant context."""
    pages = load_pages()
    if not pages:
        return "No live website content could be retrieved right now."

    terms = set(re.findall(r"[a-z0-9]{3,}", query.lower()))
    scored = []
    for url, text in pages.items():
        lower = text.lower()
        score = sum(lower.count(term) for term in terms)
        if url.rstrip("/") == SITE_URL:
            score += 1
        scored.append((score, url, text))

    scored.sort(reverse=True, key=lambda item: item[0])
    selected = []
    remaining = MAX_CONTEXT_CHARS
    for score, url, text in scored:
        if remaining <= 0:
            break
        if score == 0 and selected:
            continue
        excerpt = text[:remaining]
        selected.append(f"SOURCE: {url}\nCONTENT: {excerpt}")
        remaining -= len(excerpt)

    return "\n\n".join(selected)
