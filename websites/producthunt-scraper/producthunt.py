"""
This module contains the scraping logic for Product Hunt using Playwright.
It can scrape:
- Daily product listings
- Individual product details
- Product search results
- Historical archive data
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
import json


async def setup_page(page: Page) -> None:
    """
    Configure page with anti-detection measures.
    
    Args:
        page: Playwright page instance
    """
    # Set a realistic viewport
    await page.set_viewport_size({"width": 1920, "height": 1080})
    
    # Hide playwright automation signals
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)


async def scrape_daily_products(max_products: Optional[int] = None) -> List[Dict]:
    """
    Scrape products from the Product Hunt homepage (today's launches).
    
    Args:
        max_products: Maximum number of products to scrape (None for all)
    
    Returns:
        List of product dictionaries containing basic information
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        await setup_page(page)
        
        print("Navigating to Product Hunt homepage...")
        await page.goto('https://www.producthunt.com/', wait_until='networkidle', timeout=30000)
        
        # Wait for products to load
        await page.wait_for_selector('[data-test="homepage-section-0"]', timeout=15000)
        
        # Small delay to ensure content is rendered
        await asyncio.sleep(2)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')
        
        products = []
        product_cards = soup.select('div[data-test^="post-item"]')
        
        if max_products:
            product_cards = product_cards[:max_products]
        
        print(f"Found {len(product_cards)} products")
        
        for card in product_cards:
            try:
                # Extract product name and URL
                name_elem = card.select_one('a[href^="/posts/"]')
                if not name_elem:
                    continue
                    
                name = name_elem.text.strip()
                product_url = name_elem.get('href', '')
                full_url = f"https://www.producthunt.com{product_url}" if product_url.startswith('/') else product_url
                
                # Extract tagline
                tagline_elem = card.select_one('[color="subdued"]')
                tagline = tagline_elem.text.strip() if tagline_elem else ''
                
                # Extract upvotes
                upvote_elem = card.select_one('button[aria-label*="upvote"]')
                upvotes = upvote_elem.text.strip() if upvote_elem else '0'
                
                products.append({
                    'name': name,
                    'tagline': tagline,
                    'upvotes': upvotes,
                    'url': full_url
                })
                
            except Exception as e:
                print(f"Error parsing product card: {str(e)}")
                continue
        
        await browser.close()
        
        return products


async def scrape_product(product_url: str) -> Dict:
    """
    Scrape detailed information from a single product page.
    
    Args:
        product_url: Full URL to the product page
    
    Returns:
        Dictionary containing detailed product information
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        await setup_page(page)
        
        print(f"Scraping product: {product_url}")
        await page.goto(product_url, wait_until='networkidle', timeout=30000)
        
        # Wait for product content to load
        await page.wait_for_selector('[data-test="post-name"]', timeout=15000)
        
        # Human-like delay
        await asyncio.sleep(2)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')
        
        # Extract product name
        name_elem = soup.select_one('[data-test="post-name"]')
        name = name_elem.text.strip() if name_elem else 'N/A'
        
        # Extract tagline
        tagline_elem = soup.select_one('[data-test="post-tagline"]')
        tagline = tagline_elem.text.strip() if tagline_elem else ''
        
        # Extract description
        desc_elem = soup.select_one('[data-test="post-description"]')
        description = desc_elem.text.strip() if desc_elem else ''
        
        # Extract upvotes
        upvote_elem = soup.select_one('button[aria-label*="upvote"]')
        upvotes = upvote_elem.text.strip() if upvote_elem else '0'
        
        # Extract comment count
        comment_elem = soup.select_one('[data-test="post-comment-count"]')
        comments = comment_elem.text.strip() if comment_elem else '0'
        
        # Extract maker information
        makers = []
        maker_elements = soup.select('[data-test="post-maker"]')
        for maker in maker_elements:
            maker_name = maker.text.strip()
            maker_link = maker.get('href', '')
            if maker_link and maker_link.startswith('/'):
                maker_link = f"https://www.producthunt.com{maker_link}"
            makers.append({
                'name': maker_name,
                'profile_url': maker_link
            })
        
        # Extract website link
        website_elem = soup.select_one('a[data-test="post-product-link"]')
        website = website_elem.get('href', '') if website_elem else ''
        
        # Extract topics/categories
        topics = []
        topic_elems = soup.select('[data-test="post-topic"]')
        for topic in topic_elems:
            topics.append(topic.text.strip())
        
        await browser.close()
        
        product_data = {
            'name': name,
            'tagline': tagline,
            'description': description,
            'upvotes': upvotes,
            'comments': comments,
            'makers': makers,
            'website': website,
            'topics': topics,
            'url': product_url
        }
        
        return product_data


async def scrape_search(query: str, max_results: Optional[int] = None) -> List[Dict]:
    """
    Search for products on Product Hunt and scrape results.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
    
    Returns:
        List of product dictionaries from search results
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        await setup_page(page)
        
        search_url = f"https://www.producthunt.com/search?q={query.replace(' ', '+')}"
        print(f"Searching for: {query}")
        
        await page.goto(search_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')
        
        products = []
        product_cards = soup.select('div[data-test^="post-item"]')
        
        if max_results:
            product_cards = product_cards[:max_results]
        
        for card in product_cards:
            try:
                name_elem = card.select_one('a[href^="/posts/"]')
                if not name_elem:
                    continue
                
                name = name_elem.text.strip()
                product_url = name_elem.get('href', '')
                full_url = f"https://www.producthunt.com{product_url}" if product_url.startswith('/') else product_url
                
                tagline_elem = card.select_one('[color="subdued"]')
                tagline = tagline_elem.text.strip() if tagline_elem else ''
                
                upvote_elem = card.select_one('button[aria-label*="upvote"]')
                upvotes = upvote_elem.text.strip() if upvote_elem else '0'
                
                products.append({
                    'name': name,
                    'tagline': tagline,
                    'upvotes': upvotes,
                    'url': full_url,
                    'search_query': query
                })
                
            except Exception as e:
                print(f"Error parsing search result: {str(e)}")
                continue
        
        await browser.close()
        
        return products


async def scrape_archive(date: datetime, max_products: Optional[int] = None) -> List[Dict]:
    """
    Scrape products from a specific date in the Product Hunt archive.
    
    Args:
        date: Date to scrape (datetime object)
        max_products: Maximum number of products to scrape
    
    Returns:
        List of product dictionaries from the specified date
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        await setup_page(page)
        
        year = date.year
        month = date.month
        day = date.day
        
        archive_url = f"https://www.producthunt.com/leaderboard/daily/{year}/{month}/{day}"
        print(f"Scraping archive: {date.strftime('%Y-%m-%d')}")
        
        await page.goto(archive_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')
        
        products = []
        product_cards = soup.select('div[data-test^="post-item"]')
        
        if max_products:
            product_cards = product_cards[:max_products]
        
        for card in product_cards:
            try:
                name_elem = card.select_one('a[href^="/posts/"]')
                if not name_elem:
                    continue
                
                name = name_elem.text.strip()
                product_url = name_elem.get('href', '')
                full_url = f"https://www.producthunt.com{product_url}" if product_url.startswith('/') else product_url
                
                tagline_elem = card.select_one('[color="subdued"]')
                tagline = tagline_elem.text.strip() if tagline_elem else ''
                
                upvote_elem = card.select_one('button[aria-label*="upvote"]')
                upvotes = upvote_elem.text.strip() if upvote_elem else '0'
                
                products.append({
                    'name': name,
                    'tagline': tagline,
                    'upvotes': upvotes,
                    'url': full_url,
                    'date': date.strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                print(f"Error parsing archive product: {str(e)}")
                continue
        
        await browser.close()
        
        return products
