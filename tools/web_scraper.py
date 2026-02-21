"""
Web Scraper Tool
================
Extracts content, metadata, and article text from URLs.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class WebScrapingResult:
    """Result from web scraping."""
    success: bool
    url: str = ""
    title: str = ""
    description: str = ""
    main_content: str = ""
    author: str = ""
    publish_date: str = ""
    key_points: List[str] = field(default_factory=list)
    sharing_angles: List[str] = field(default_factory=list)
    domain: str = ""
    error_message: str = ""


class WebScraper:
    """
    Scrapes web pages and extracts structured content for LinkedIn posts.
    
    Dependency note: beautifulsoup4 and requests are required.
    """

    def __init__(self, llm_provider=None):
        self.llm = llm_provider
        logger.info("✅ WebScraper initialized")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def scrape(self, url: str) -> WebScrapingResult:
        """Scrape a URL and extract content."""
        if not self._is_valid_url(url):
            return WebScrapingResult(success=False, url=url, error_message="Invalid URL")

        try:
            html, final_url = self._fetch(url)
            if not html:
                return WebScrapingResult(success=False, url=url, error_message="Failed to fetch URL")

            parsed = self._parse_html(html, final_url)
            if self.llm:
                parsed.key_points = self._extract_key_points(parsed.main_content)
                parsed.sharing_angles = self._suggest_angles(parsed)

            return parsed

        except Exception as exc:
            logger.error(f"❌ Scraping failed for {url}: {exc}")
            return WebScrapingResult(success=False, url=url, error_message=str(exc))

    def scrape_multiple(self, urls: List[str]) -> List[WebScrapingResult]:
        return [self.scrape(u) for u in urls]

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------

    def _is_valid_url(self, url: str) -> bool:
        try:
            r = urlparse(url)
            return r.scheme in ("http", "https") and bool(r.netloc)
        except Exception:
            return False

    def _fetch(self, url: str):
        """Fetch HTML using requests + basic headers."""
        try:
            import requests  # type: ignore

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            if resp.status_code == 200:
                return resp.text, resp.url
            return None, url
        except ImportError:
            logger.warning("⚠️ requests not installed.")
            return None, url
        except Exception as exc:
            logger.error(f"Fetch error: {exc}")
            return None, url

    def _parse_html(self, html: str, url: str) -> WebScrapingResult:
        """Parse HTML and extract structured content."""
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except ImportError:
            logger.warning("⚠️ beautifulsoup4 not installed.")
            return WebScrapingResult(
                success=True,
                url=url,
                title="Page content unavailable",
                main_content=self._strip_tags(html)[:2000],
                domain=urlparse(url).netloc,
            )

        soup = BeautifulSoup(html, "html.parser")
        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title = ""
        if soup.title:
            title = soup.title.string or ""

        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")

        author = ""
        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author:
            author = meta_author.get("content", "")

        # Extract main article text
        article = soup.find("article") or soup.find("main") or soup.find("body")
        main_content = ""
        if article:
            main_content = " ".join(article.get_text(separator=" ").split())[:5000]

        return WebScrapingResult(
            success=True,
            url=url,
            title=title.strip(),
            description=description.strip(),
            main_content=main_content,
            author=author.strip(),
            domain=urlparse(url).netloc,
        )

    def _strip_tags(self, html: str) -> str:
        """Remove HTML tags with regex when BeautifulSoup is unavailable."""
        return re.sub(r"<[^>]+>", " ", html)

    def _extract_key_points(self, text: str) -> List[str]:
        if not text or not self.llm:
            return []
        try:
            result = self.llm.generate(
                prompt=f"List 3-5 key points from this article for a LinkedIn post:\n\n{text[:3000]}",
                system_prompt="Be concise and insightful.",
            )
            if result.success:
                return [l.strip().lstrip("•-0123456789. ") for l in result.content.split("\n") if l.strip()][:5]
        except Exception:
            pass
        return []

    def _suggest_angles(self, data: WebScrapingResult) -> List[str]:
        if not self.llm:
            return []
        try:
            context = f"Title: {data.title}\nDescription: {data.description}"
            result = self.llm.generate(
                prompt=f"Suggest 3 LinkedIn post angles for sharing this article:\n{context}",
                system_prompt="Be creative and audience-focused.",
            )
            if result.success:
                return [l.strip().lstrip("•-0123456789. ") for l in result.content.split("\n") if l.strip()][:3]
        except Exception:
            pass
        return []
