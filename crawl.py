import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from typing import List, Dict
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class InternshipScraper(BaseModel):
    api_key: str = Field(..., description="FireCrawl API key")
    search_results: List[Dict] = Field(default_factory=list)

    def scrape_internships(self, urls: List[str]) -> List[Dict]:
        app = FirecrawlApp(api_key=self.api_key)
        
        for url in urls:
            crawl_result = app.crawl_url(
                url,
                params={
                    'crawlerOptions': {
                        'limit': 5  # Adjust this as needed
                    },
                    'pageOptions': {
                        'onlyMainContent': True
                    }
                },
                wait_until_done=True  # Wait for the crawl to complete
            )
            
            markdown_data_list = []
            for item in crawl_result:
                # Check if item has a to_markdown method
                if hasattr(item, 'to_markdown'):
                    markdown_data_list.append(item.to_markdown())
                else:
                    markdown_data_list.append(str(item))  # Fallback to string conversion
            
            markdown_data = "\n\n".join(markdown_data_list)
            
            self.search_results.append({
                'url': url,
                'content': markdown_data
            })
        
        return self.search_results

# Define the specific URLs to be crawled
urls_to_crawl = [
    "https://www.indeed.com/jobs?q=data+intern&l=&from=searchOnDesktopSerp&vjk=1a287c960d35d0ef",
    "https://www.indeed.com/jobs?q=summer+data+intern&l=&from=searchOnDesktopSerp&vjk=fa03889ef433d327",
    "https://www.indeed.com/jobs?q=summer+SWE+intern&l=&from=searchOnDesktopSerp&vjk=bfd7f32fa5861409"
]

# Initialize the InternshipScraper
scraper = InternshipScraper(api_key=os.getenv('FIRECRAWL_API_KEY'))

# Perform scraping on specific URLs
search_results = scraper.scrape_internships(urls=urls_to_crawl)

# Print results
for result in search_results:
    print(f"URL: {result['url']}")
    print(f"Crawled Content:\n{result['content'][:500]}...")  # Print first 500 characters of crawled content
    print("\n---\n")
