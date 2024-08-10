import httpx
import re
import json
import asyncio
from indeed_scraper import ScrapflyClient, ScrapeConfig
from urllib.parse import urlencode

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
}

def parse_search_page(html: str):
    data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
    data = json.loads(data[0])
    return {
        "results": data["metaData"]["mosaicProviderJobCardsModel"]["results"],
        "meta": data["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"],
    }

async def scrape_search(client: httpx.AsyncClient, query: str, location: str, max_results: int = 50):
    def make_page_url(offset):
        parameters = {"q": query, "l": location, "filter": 0, "start": offset}
        return "https://www.indeed.com/jobs?" + urlencode(parameters)

    print(f"Scraping first page of search: {query=}, {location=}")
    response_first_page = await client.get(make_page_url(0))
    data_first_page = parse_search_page(response_first_page.text)

    results = data_first_page["results"]
    total_results = sum(category["jobCount"] for category in data_first_page["meta"])
    if total_results > max_results:
        total_results = max_results

    print(f"Scraping remaining {total_results - 10 / 10} pages")
    other_pages = [make_page_url(offset) for offset in range(10, total_results + 10, 10)]
    for response in await asyncio.gather(*[client.get(url=url) for url in other_pages]):
        results.extend(parse_search_page(response.text)["results"])
    return results

async def main():
    async with httpx.AsyncClient() as client:
        jobs = await scrape_search(client, "summer data internship", "USA", max_results=50)
        for job in jobs:
            print(job)

if __name__ == "__main__":
    asyncio.run(main())
