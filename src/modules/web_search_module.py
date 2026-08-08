"""
Web Search Module - Internet Research Capability
Provides web search (DuckDuckGo, free, no API key) and basic page scraping.
Results are fed back to the agent loop for the LLM to synthesize.
"""
import json
import re
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus


# Try to import httpx (preferred) or fall back to urllib
try:
    import httpx
    HTTP_CLIENT = "httpx"
except ImportError:
    HTTP_CLIENT = "urllib"


class WebSearchModule:
    """
    Web search using DuckDuckGo HTML search (no API key needed).
    Optionally supports Brave Search API if BRAVE_API_KEY is set.
    """

    def __init__(self):
        self.enabled = True
        self._brave_api_key = None

        # Try to load Brave API key from env
        import os
        self._brave_api_key = os.getenv("BRAVE_API_KEY")

        if self._brave_api_key:
            print("✓ Web Search ready (Brave Search API)")
        else:
            print("✓ Web Search ready (DuckDuckGo HTML)")

    # ------------------------------------------------------------------
    # Public: Search
    # ------------------------------------------------------------------
    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web and return a list of results.
        Each result: {"title": ..., "url": ..., "snippet": ...}
        """
        if self._brave_api_key:
            return await self._search_brave(query, num_results)
        return await self._search_duckduckgo(query, num_results)

    # ------------------------------------------------------------------
    # Public: Fetch page content
    # ------------------------------------------------------------------
    async def fetch_page(self, url: str, max_chars: int = 5000) -> str:
        """Fetch a web page and extract readable text content."""
        try:
            html = await self._http_get(url, timeout=10)
            if not html:
                return f"Failed to fetch: {url}"
            text = self._extract_text_from_html(html)
            if len(text) > max_chars:
                text = text[:max_chars] + "\n...[truncated]"
            return text
        except Exception as exc:
            return f"Error fetching {url}: {exc}"

    # ------------------------------------------------------------------
    # DuckDuckGo HTML search (no API key)
    # ------------------------------------------------------------------
    async def _search_duckduckgo(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search DuckDuckGo via HTML scraping."""
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            html = await self._http_get(url, headers=headers, timeout=10)
            if not html:
                return []

            results = []
            # Parse DuckDuckGo HTML results
            # Each result is in a <div class="result"> or <a class="result__a">
            result_blocks = re.findall(
                r'<a\s+class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
                r'<a\s+class="result__snippet"[^>]*>(.*?)</a>',
                html,
                re.DOTALL,
            )

            if not result_blocks:
                # Fallback: try simpler pattern
                result_blocks = re.findall(
                    r'<a\s[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                    html,
                    re.DOTALL,
                )
                for href, title in result_blocks[:num_results]:
                    clean_url = self._clean_ddg_url(href)
                    results.append({
                        "title": self._strip_html(title),
                        "url": clean_url,
                        "snippet": "",
                    })
            else:
                for href, title, snippet in result_blocks[:num_results]:
                    clean_url = self._clean_ddg_url(href)
                    results.append({
                        "title": self._strip_html(title),
                        "url": clean_url,
                        "snippet": self._strip_html(snippet),
                    })

            return results

        except Exception as exc:
            print(f"[WebSearch] DuckDuckGo error: {exc}")
            return []

    # ------------------------------------------------------------------
    # Brave Search API (optional, needs BRAVE_API_KEY)
    # ------------------------------------------------------------------
    async def _search_brave(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search using Brave Search API."""
        url = f"https://api.search.brave.com/res/v1/web/search?q={quote_plus(query)}&count={num_results}"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self._brave_api_key,
        }

        try:
            response_text = await self._http_get(url, headers=headers, timeout=10)
            if not response_text:
                return []

            data = json.loads(response_text)
            results = []
            for item in data.get("web", {}).get("results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                })
            return results

        except Exception as exc:
            print(f"[WebSearch] Brave Search error: {exc}")
            return []

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------
    async def _http_get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
    ) -> Optional[str]:
        """Make an HTTP GET request."""
        if HTTP_CLIENT == "httpx":
            return await self._http_get_httpx(url, headers, timeout)
        return self._http_get_urllib(url, headers, timeout)

    async def _http_get_httpx(self, url, headers, timeout) -> Optional[str]:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            resp = await client.get(url, headers=headers or {})
            resp.raise_for_status()
            return resp.text

    def _http_get_urllib(self, url, headers, timeout) -> Optional[str]:
        import urllib.request
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")

    # ------------------------------------------------------------------
    # HTML helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove HTML tags and decode entities."""
        text = re.sub(r"<[^>]+>", "", text)
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("&quot;", '"').replace("&#x27;", "'").replace("&nbsp;", " ")
        return text.strip()

    @staticmethod
    def _clean_ddg_url(href: str) -> str:
        """Extract actual URL from DuckDuckGo redirect."""
        # DDG wraps URLs like //duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com&...
        import urllib.parse
        if "uddg=" in href:
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            urls = parsed.get("uddg", [])
            if urls:
                return urls[0]
        if href.startswith("//"):
            return "https:" + href
        return href

    @staticmethod
    def _extract_text_from_html(html: str) -> str:
        """Extract readable text from HTML, stripping scripts/styles/tags."""
        # Remove script and style blocks
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
        # Remove all tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text
