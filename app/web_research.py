import html
import re
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


CURRENT_PATTERNS = (
    r"\b(latest|today|tonight|now|currently|current|recent|recently|this week|this month)\b",
    r"\b(news|headline|headlines|update|updates|breaking|what happened|what's happening)\b",
    r"\b(yesterday|tomorrow)\b",
)


def needs_web_research(query: str) -> bool:
    q = query.lower().strip()
    return any(re.search(pattern, q) for pattern in CURRENT_PATTERNS)


def _clean(value: str, limit: int = 280) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


def search_web(query: str, limit: int = 2) -> str:
    """Retrieve compact current-news snippets without using an external AI service."""
    q = quote(query[:180])
    url = f"https://www.bing.com/news/search?q={q}&format=rss"
    request = Request(
        url,
        headers={"User-Agent": "Game-API-AI/1.0 (+https://game-api.online)"},
    )

    try:
        with urlopen(request, timeout=6) as response:
            data = response.read(160000)
        root = ET.fromstring(data)
    except Exception:
        return ""

    results = []
    for item in root.findall(".//item"):
        title = _clean(item.findtext("title"), 180)
        description = _clean(item.findtext("description"), 320)
        link = _clean(item.findtext("link"), 240)
        if not title:
            continue
        results.append(f"[NEWS] {title}\n{description}\nSource: {link}")
        if len(results) >= limit:
            break

    return "\n\n".join(results)
