# Apply agno-ck metadata fix before any agno imports
import agno_metadata_fix

import json
from textwrap import dedent
from typing import Dict, Iterator, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.workflow import RunEvent, RunResponse, Workflow
from pydantic import BaseModel, Field

from db.session import db_url
from workflows.settings import workflow_settings


class NewsArticle(BaseModel):
    title: str = Field(..., description="Title of the article.")
    url: str = Field(..., description="Link to the article.")
    summary: Optional[str] = Field(..., description="Summary of the article if available.")


class SearchResults(BaseModel):
    articles: list[NewsArticle]


class ScrapedArticle(BaseModel):
    title: str = Field(..., description="Title of the article.")
    url: str = Field(..., description="Link to the article.")
    summary: Optional[str] = Field(..., description="Summary of the article if available.")
    content: Optional[str] = Field(
        ...,
        description="Full article content in markdown format. None if content is unavailable.",
    )


class BlogPostGenerator(Workflow):
    """Advanced workflow for generating professional blog posts with proper research and citations."""

    description: str = dedent("""\
    An intelligent blog post generator that creates engaging, well-researched content.
    This workflow orchestrates multiple AI agents to research, analyze, and craft
    compelling blog posts that combine journalistic rigor with engaging storytelling.
    The system excels at creating content that is both informative and optimized for
    digital consumption.
    """)

    # Search Agent: Handles intelligent web searching and source gathering
    searcher: Agent = Agent(
        model=OpenRouter(id="moonshotai/kimi-k2:free"),
        tools=[DuckDuckGoTools()],
        description=dedent("""\
        You are BlogResearch-X, an elite research assistant specializing in discovering
        high-quality sources for compelling blog content. Your expertise includes:

        - Finding authoritative and trending sources
        - Evaluating content credibility and relevance
        - Identifying diverse perspectives and expert opinions
        - Discovering unique angles and insights
        - Ensuring comprehensive topic coverage\
        """),
        instructions=dedent("""\
        1. Search Strategy 🔍
           - Find 10-15 relevant sources and select the 5-7 best ones
           - Prioritize recent, authoritative content
           - Look for unique angles and expert insights
        2. Source Evaluation 📊
           - Verify source credibility and expertise
           - Check publication dates for timeliness
           - Assess content depth and uniqueness
        3. Diversity of Perspectives 🌐
           - Include different viewpoints
           - Gather both mainstream and expert opinions
           - Find supporting data and statistics
        
        IMPORTANT: Return your response as a JSON object with this format:
        {
            "articles": [
                {
                    "title": "Article Title",
                    "url": "https://example.com/article",
                    "summary": "Brief summary of the article"
                }
            ]
        }\
        """),
        # response_model not supported with Kimi-k2
        # structured_outputs=False,
    )

    # Content Scraper: Extracts and processes article content
    article_scraper: Agent = Agent(
        model=OpenRouter(id="moonshotai/kimi-k2:free"),
        tools=[Newspaper4kTools()],
        description=dedent("""\
        You are ContentBot-X, a specialist in extracting and processing digital content
        for blog creation. Your expertise includes:

        - Efficient content extraction
        - Smart formatting and structuring
        - Key information identification
        - Quote and statistic preservation
        - Maintaining source attribution\
        """),
        instructions=dedent("""\
        1. Content Extraction 📑
           - Extract content from the article
           - Preserve important quotes and statistics
           - Maintain proper attribution
           - Handle paywalls gracefully
        2. Content Processing 🔄
           - Format text in clean markdown
           - Preserve key information
           - Structure content logically
        3. Quality Control ✅
           - Verify content relevance
           - Ensure accurate extraction
           - Maintain readability
        
        IMPORTANT: Return your response as a JSON object with this format:
        {
            "title": "Article Title",
            "url": "Article URL",
            "summary": "Brief summary",
            "content": "Full article content in markdown format"
        }\
        """),
        # response_model not supported with Kimi-k2
        # structured_outputs=False,
    )

    # Content Writer Agent: Crafts engaging blog posts from research
    writer: Agent = Agent(
        model=OpenRouter(id="moonshotai/kimi-k2:free"),
        description=dedent("""\
        You are BlogMaster-X, an elite content creator combining journalistic excellence
        with digital marketing expertise. Your strengths include:

        - Crafting viral-worthy headlines
        - Writing engaging introductions
        - Structuring content for digital consumption
        - Incorporating research seamlessly
        - Optimizing for SEO while maintaining quality
        - Creating shareable conclusions\
        """),
        instructions=dedent("""\
        1. Content Strategy 📝
           - Craft attention-grabbing headlines
           - Write compelling introductions
           - Structure content for engagement
           - Include relevant subheadings
        2. Writing Excellence ✍️
           - Balance expertise with accessibility
           - Use clear, engaging language
           - Include relevant examples
           - Incorporate statistics naturally
        3. Source Integration 🔍
           - Cite sources properly
           - Include expert quotes
           - Maintain factual accuracy
        4. Digital Optimization 💻
           - Structure for scanability
           - Include shareable takeaways
           - Optimize for SEO
           - Add engaging subheadings\
        """),
        expected_output=dedent("""\
        # {Viral-Worthy Headline}

        ## Introduction
        {Engaging hook and context}

        ## {Compelling Section 1}
        {Key insights and analysis}
        {Expert quotes and statistics}

        ## {Engaging Section 2}
        {Deeper exploration}
        {Real-world examples}

        ## {Practical Section 3}
        {Actionable insights}
        {Expert recommendations}

        ## Key Takeaways
        - {Shareable insight 1}
        - {Practical takeaway 2}
        - {Notable finding 3}

        ## Sources
        {Properly attributed sources with links}\
        """),
        markdown=True,
    )

    def run(  # type: ignore
        self,
        topic: str,
        use_search_cache: bool = True,
        use_scrape_cache: bool = True,
        use_cached_report: bool = True,
    ) -> Iterator[RunResponse]:
        logger.info(f"Generating a blog post on: {topic}")

        # Use the cached blog post if use_cache is True
        if use_cached_report:
            cached_blog_post = self.get_cached_blog_post(topic)
            if cached_blog_post:
                yield RunResponse(content=cached_blog_post)
                return

        # Search the web for articles on the topic
        search_results: Optional[SearchResults] = self.get_search_results(topic, use_search_cache)
        # If no search_results are found for the topic, end the workflow
        if search_results is None or len(search_results.articles) == 0:
            yield RunResponse(
                content=f"Sorry, could not find any articles on the topic: {topic}",
            )
            return

        # Scrape the search results
        scraped_articles: Dict[str, ScrapedArticle] = self.scrape_articles(topic, search_results, use_scrape_cache)

        # Prepare the input for the writer
        writer_input = {
            "topic": topic,
            "articles": [v.model_dump() for v in scraped_articles.values()],
        }

        # Run the writer and yield the response
        yield from self.writer.run(json.dumps(writer_input, indent=4), stream=True)

        # Save the blog post in the cache
        if self.writer.run_response:
            self.add_blog_post_to_cache(topic, str(self.writer.run_response.content))

    def get_cached_blog_post(self, topic: str) -> Optional[str]:
        logger.info("Checking if cached blog post exists")

        return self.session_state.get("blog_posts", {}).get(topic)

    def add_blog_post_to_cache(self, topic: str, blog_post: str):
        logger.info(f"Saving blog post for topic: {topic}")
        self.session_state.setdefault("blog_posts", {})
        self.session_state["blog_posts"][topic] = blog_post

    def get_cached_search_results(self, topic: str) -> Optional[SearchResults]:
        logger.info("Checking if cached search results exist")
        search_results = self.session_state.get("search_results", {}).get(topic)
        return (
            SearchResults.model_validate(search_results)
            if search_results and isinstance(search_results, dict)
            else search_results
        )

    def add_search_results_to_cache(self, topic: str, search_results: SearchResults):
        logger.info(f"Saving search results for topic: {topic}")
        self.session_state.setdefault("search_results", {})
        self.session_state["search_results"][topic] = search_results

    def get_cached_scraped_articles(self, topic: str):
        logger.info("Checking if cached scraped articles exist")
        scraped_articles = self.session_state.get("scraped_articles", {}).get(topic)
        return (
            ScrapedArticle.model_validate(scraped_articles)
            if scraped_articles and isinstance(scraped_articles, dict)
            else scraped_articles
        )

    def add_scraped_articles_to_cache(self, topic: str, scraped_articles: Dict[str, ScrapedArticle]):
        logger.info(f"Saving scraped articles for topic: {topic}")
        self.session_state.setdefault("scraped_articles", {})
        self.session_state["scraped_articles"][topic] = scraped_articles

    def get_search_results(self, topic: str, use_search_cache: bool, num_attempts: int = 3) -> Optional[SearchResults]:
        # Get cached search_results from the session state if use_search_cache is True
        if use_search_cache:
            try:
                search_results_from_cache = self.get_cached_search_results(topic)
                if search_results_from_cache is not None:
                    search_results = SearchResults.model_validate(search_results_from_cache)
                    logger.info(f"Found {len(search_results.articles)} articles in cache.")
                    return search_results
            except Exception as e:
                logger.warning(f"Could not read search results from cache: {e}")

        # If there are no cached search_results, use the searcher to find the latest articles
        for attempt in range(num_attempts):
            try:
                searcher_response: RunResponse = self.searcher.run(topic)
                if searcher_response is not None and searcher_response.content is not None:
                    # Try to parse the response as SearchResults
                    if isinstance(searcher_response.content, SearchResults):
                        search_results = searcher_response.content
                    elif isinstance(searcher_response.content, str):
                        # Try to parse JSON string response
                        try:
                            import re
                            # Extract JSON from the response if it's embedded in text
                            json_match = re.search(r'\{.*\}', searcher_response.content, re.DOTALL)
                            if json_match:
                                json_str = json_match.group()
                                data = json.loads(json_str)
                                search_results = SearchResults.model_validate(data)
                            else:
                                # If no JSON found, create a simple response
                                logger.warning("No JSON found in response, creating empty results")
                                search_results = SearchResults(articles=[])
                        except (json.JSONDecodeError, Exception) as e:
                            logger.warning(f"Failed to parse JSON response: {e}")
                            # Create empty results as fallback
                            search_results = SearchResults(articles=[])
                    else:
                        logger.warning(f"Unexpected response type: {type(searcher_response.content)}")
                        search_results = SearchResults(articles=[])
                    
                    article_count = len(search_results.articles)
                    logger.info(f"Found {article_count} articles on attempt {attempt + 1}")
                    # Cache the search results
                    self.add_search_results_to_cache(topic, search_results)
                    return search_results
                else:
                    logger.warning(f"Attempt {attempt + 1}/{num_attempts} failed: No response")
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{num_attempts} failed: {str(e)}")

        logger.error(f"Failed to get search results after {num_attempts} attempts")
        return None

    def scrape_articles(
        self, topic: str, search_results: SearchResults, use_scrape_cache: bool
    ) -> Dict[str, ScrapedArticle]:
        scraped_articles: Dict[str, ScrapedArticle] = {}

        # Get cached scraped_articles from the session state if use_scrape_cache is True
        if use_scrape_cache:
            try:
                scraped_articles_from_cache = self.get_cached_scraped_articles(topic)
                if scraped_articles_from_cache is not None:
                    scraped_articles = scraped_articles_from_cache
                    logger.info(f"Found {len(scraped_articles)} scraped articles in cache.")
                    return scraped_articles
            except Exception as e:
                logger.warning(f"Could not read scraped articles from cache: {e}")

        # Scrape the articles that are not in the cache
        for article in search_results.articles:
            if article.url in scraped_articles:
                logger.info(f"Found scraped article in cache: {article.url}")
                continue

            article_scraper_response: RunResponse = self.article_scraper.run(article.url)
            if article_scraper_response is not None and article_scraper_response.content is not None:
                # Try to parse the response as ScrapedArticle
                if isinstance(article_scraper_response.content, ScrapedArticle):
                    scraped_article = article_scraper_response.content
                elif isinstance(article_scraper_response.content, str):
                    # Try to parse JSON string response
                    try:
                        import re
                        # Extract JSON from the response if it's embedded in text
                        json_match = re.search(r'\{.*\}', article_scraper_response.content, re.DOTALL)
                        if json_match:
                            json_str = json_match.group()
                            data = json.loads(json_str)
                            scraped_article = ScrapedArticle.model_validate(data)
                        else:
                            # If no JSON found, create a simple response
                            logger.warning(f"No JSON found for article: {article.url}")
                            scraped_article = ScrapedArticle(
                                title=article.title,
                                url=article.url,
                                summary=article.summary,
                                content=None
                            )
                    except (json.JSONDecodeError, Exception) as e:
                        logger.warning(f"Failed to parse scraped article JSON: {e}")
                        scraped_article = ScrapedArticle(
                            title=article.title,
                            url=article.url,
                            summary=article.summary,
                            content=None
                        )
                else:
                    logger.warning(f"Unexpected scraper response type: {type(article_scraper_response.content)}")
                    scraped_article = ScrapedArticle(
                        title=article.title,
                        url=article.url,
                        summary=article.summary,
                        content=None
                    )
                
                scraped_articles[scraped_article.url] = scraped_article
                logger.info(f"Scraped article: {scraped_article.url}")

        # Save the scraped articles in the session state
        self.add_scraped_articles_to_cache(topic, scraped_articles)
        return scraped_articles


# Run the workflow if the script is executed directly
def write_blog_post(self, topic: str, scraped_articles: Dict[str, ScrapedArticle]) -> Iterator[RunResponse]:
    logger.info("Writing blog post")
    # Prepare the input for the writer
    writer_input = {
        "topic": topic,
        "articles": [v.model_dump() for v in scraped_articles.values()],
    }
    # Run the writer and yield the response
    yield from self.writer.run(json.dumps(writer_input, indent=4), stream=True)
    # Save the blog post in the cache
    self.add_blog_post_to_cache(topic, self.writer.run_response.content)


def get_blog_post_generator(debug_mode: bool = False) -> BlogPostGenerator:
    return BlogPostGenerator(
        workflow_id="generate-blog-post-on",
        storage=PostgresStorage(
            table_name="blog_post_generator_workflows",
            db_url=db_url,
            auto_upgrade_schema=True,
            mode="workflow",
        ),
        debug_mode=debug_mode,
        monitoring=True,
    )
