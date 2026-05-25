from dataclasses import dataclass

from playwright.sync_api import sync_playwright

from ncaa_baseball.config import Config


@dataclass(slots=True)
class PageResult:
    url: str
    final_url: str
    html: str
    title: str


def fetch_page(
    url: str,
    config: Config,
) -> PageResult:
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(
            headless=config.headless,
        )

        page = browser.new_page()

        page.goto(
            url,
            wait_until="networkidle",
            timeout=config.navigation_timeout_ms,
        )

        result = PageResult(
            url=url,
            final_url=page.url,
            html=page.content(),
            title=page.title(),
        )

        browser.close()

        return result
