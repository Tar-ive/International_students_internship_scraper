import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
# from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from crawl4ai import WebCrawler
from typing import List, Dict
from pydantic import Field

# Load environment variables
load_dotenv()

# Initialize tools
duckduckgo_search = DuckDuckGoSearchRun()
web_crawler = WebCrawler()
web_crawler.warmup()

# Initialize LLM
llm = ChatOpenAI(
    model='gpt-4o-mini',
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

class EnhancedSearchAgent(Agent):
    search_results: List[Dict] = Field(default_factory=list)
    
    def web_search(self, query: str, site: str) -> List[Dict]:
        search_query = f"{query} site:{site}"
        results = duckduckgo_search.run(search_query)
        # Print results to inspect the structure
        print(f"Results for query '{search_query}': {results}")
        return [{'url': result['link'], 'title': result['title'], 'snippet': result['snippet']} for result in results]

    def crawl_website(self, url: str) -> str:
        result = web_crawler.run(url=url)
        return result.markdown

    def perform_search(self, query: str, sites: List[str], num_results: int = 5) -> List[Dict]:
        for site in sites:
            search_results = self.web_search(query, site)[:num_results]
            for result in search_results:
                result['content'] = self.crawl_website(result['url'])
            self.search_results.extend(search_results)
        return self.search_results

# Define the specific sites to be included in the search
specific_sites = ["indeed.com", "linkedin.com", "workday.com"]

# Initialize the EnhancedSearchAgent with specific sites
search_agent = EnhancedSearchAgent(
    role="Internship Search Agent",
    goal="Search for summer 2025 internships in the US for international undergraduate students, mainly sophomores, in fields like data science, data engineering, data analysis, machine learning, software engineering, and business intelligence.",
    backstory="Expert at web crawling and internet searches, specializing in finding internship opportunities",
    tools=[duckduckgo_search],
    verbose=True,
    llm=llm
)

# Perform search on specific sites
search_results = search_agent.perform_search(query="summer 2025 internship", sites=specific_sites, num_results=5)

# Uncomment the following lines if you want to include additional agents and tasks
# eligibility_checker_agent = Agent(
#     role="Eligibility Checker Agent",
#     goal="Check if the internships found are open to international students and verify the eligibility criteria for the internships in the US.",
#     backstory="Expert at analyzing and validating internship information with a focus on international student requirements",
#     tools=[duckduckgo_search],
#     verbose=True,
#     llm=llm,
#     limit=5,  # Limit the number of searches
#     max_execution_time=100  # Max execution time in seconds (5 minutes)
# )

# location_filter_agent = Agent(
#     role="Location Filter Agent",
#     goal="Filter internships by location within the US and identify internships that offer relocation assistance or visa sponsorship.",
#     backstory="Expert at filtering and identifying internships based on location and visa requirements",
#     tools=[duckduckgo_search],
#     verbose=True,
#     llm=llm,
#     limit=5,  # Limit the number of searches
#     max_execution_time=100  # Max execution time in seconds (5 minutes)
# )

# industry_matcher_agent = Agent(
#     role="Industry Matcher Agent",
#     goal="Match internships with the student's field of study or interest and identify internships in industries within the US that are open to international students.",
#     backstory="Expert at matching internships with students' fields of study and interests",
#     tools=[duckduckgo_search],
#     verbose=True,
#     llm=llm,
#     limit=5,  # Limit the number of searches
#     max_execution_time=100  # Max execution time in seconds (5 minutes)
# )

# visa_requirement_agent = Agent(
#     role="Visa Requirement Agent",
#     goal="Research visa requirements for internships in the US and identify internships that offer visa sponsorship or support.",
#     backstory="Expert at researching and identifying visa requirements and sponsorship opportunities for internships",
#     tools=[duckduckgo_search],
#     verbose=True,
#     llm=llm,
#     limit=5,  # Limit the number of searches
#     max_execution_time=100  # Max execution time in seconds (5 minutes)
# )

# Define Tasks
search_task = Task(
    description="""Search for summer 2025 internship opportunities in the US for international undergraduate students, mainly sophomores, in fields like 
                   data science, data engineering, data analysis, machine learning, software engineering, and business intelligence. 
                   Focus on programs that explicitly welcome international applicants and have clear visa sponsorship information. 
                   Use web crawling to gather detailed information from company websites and specific job boards like Indeed, LinkedIn, and Workday.
                   The results should include the name, description, application details, and links to apply to the internships.""",
    expected_output="A list of summer 2025 internship opportunities in the US including the name, description, application details, and links to the internships.",
    agent=search_agent
)

# Uncomment the following lines if you want to include additional tasks
# eligibility_task = Task(
#     description="""Check if the internships found are open to international students and verify the eligibility criteria for each internship in the US.""",
#     expected_output="A list of internships in the US that are open to international students, including eligibility criteria.",
#     agent=eligibility_checker_agent
# )

# location_task = Task(
#     description="""Filter the internships by location within the US and identify those that offer relocation assistance or visa sponsorship.""",
#     expected_output="A list of internships filtered by location within the US, including details on relocation assistance or visa sponsorship.",
#     agent=location_filter_agent
# )

# industry_task = Task(
#     description="""Match the internships with the student's field of study or interest and identify those in industries within the US that are open to international students.""",
#     expected_output="A list of internships matched with the student's field of study or interest, including industry details.",
#     agent=industry_matcher_agent
# )

# visa_task = Task(
#     description="""Research the visa requirements for the internship locations in the US and identify internships that offer visa sponsorship or support.""",
#     expected_output="A list of internships with details on visa requirements and sponsorship or support in the US.",
#     agent=visa_requirement_agent
# )

# Uncomment the following lines if you want to include a Crew
# Create Crew
# internship_crew = Crew(
#     agents=[search_agent, eligibility_checker_agent, location_filter_agent, industry_matcher_agent, visa_requirement_agent],
#     tasks=[search_task, eligibility_task, location_task, industry_task, visa_task],
#     verbose=2,
#     process=Process.sequential
# )

# Run the crew with error handling
# try:
#     result = internship_crew.kickoff()
#     print(result)
# except Exception as e:
#     print(f"An error occurred: {e}")

# After the crew has finished, you can access the detailed search results
for result in search_agent.search_results:
    print(f"URL: {result['url']}")
    print(f"Title: {result['title']}")
    print(f"Snippet: {result['snippet']}")
    print(f"Crawled Content: {result['content'][:500]}...")  # Print first 500 characters of crawled content
    print("\n---\n")
