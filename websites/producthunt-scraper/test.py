"""
Unit tests for Product Hunt scraper.

Run tests with:
    pytest test.py
    
Run specific tests:
    pytest test.py -k test_daily_scraping
    pytest test.py -k test_product_scraping
    pytest test.py -k test_search_scraping
    pytest test.py -k test_archive_scraping
"""

import pytest
from datetime import datetime, timedelta
from producthunt import (
    scrape_daily_products,
    scrape_product,
    scrape_search,
    scrape_archive
)


@pytest.mark.asyncio
async def test_daily_scraping():
    """
    Test scraping today's products from the homepage.
    """
    products = await scrape_daily_products(max_products=3)
    
    assert len(products) > 0, "Should scrape at least one product"
    assert len(products) <= 3, "Should respect max_products limit"
    
    # Check structure of first product
    product = products[0]
    assert 'name' in product, "Product should have a name"
    assert 'tagline' in product, "Product should have a tagline"
    assert 'upvotes' in product, "Product should have upvotes"
    assert 'url' in product, "Product should have a URL"
    
    # Verify data types
    assert isinstance(product['name'], str), "Name should be a string"
    assert isinstance(product['tagline'], str), "Tagline should be a string"
    assert isinstance(product['upvotes'], str), "Upvotes should be a string"
    assert isinstance(product['url'], str), "URL should be a string"
    
    # Verify URL format
    assert product['url'].startswith('https://www.producthunt.com/posts/'), \
        "URL should be a valid Product Hunt post URL"
    
    print(f"\n✓ Successfully scraped {len(products)} daily products")
    print(f"  Sample: {product['name']} - {product['upvotes']} upvotes")


@pytest.mark.asyncio
async def test_product_scraping():
    """
    Test scraping detailed product information.
    """
    # First get a product URL
    daily_products = await scrape_daily_products(max_products=1)
    assert len(daily_products) > 0, "Need at least one product to test"
    
    product_url = daily_products[0]['url']
    
    # Scrape the product details
    product = await scrape_product(product_url)
    
    # Check all expected fields
    assert 'name' in product, "Product should have a name"
    assert 'tagline' in product, "Product should have a tagline"
    assert 'description' in product, "Product should have a description"
    assert 'upvotes' in product, "Product should have upvotes"
    assert 'comments' in product, "Product should have comments count"
    assert 'makers' in product, "Product should have makers list"
    assert 'website' in product, "Product should have a website"
    assert 'topics' in product, "Product should have topics list"
    assert 'url' in product, "Product should have a URL"
    
    # Verify data types
    assert isinstance(product['name'], str), "Name should be a string"
    assert isinstance(product['makers'], list), "Makers should be a list"
    assert isinstance(product['topics'], list), "Topics should be a list"
    
    # Check maker structure if makers exist
    if product['makers']:
        maker = product['makers'][0]
        assert 'name' in maker, "Maker should have a name"
        assert 'profile_url' in maker, "Maker should have a profile URL"
    
    print(f"\n✓ Successfully scraped product details")
    print(f"  Name: {product['name']}")
    print(f"  Makers: {len(product['makers'])} makers")
    print(f"  Topics: {len(product['topics'])} topics")
    print(f"  Upvotes: {product['upvotes']}")
    print(f"  Comments: {product['comments']}")


@pytest.mark.asyncio
async def test_search_scraping():
    """
    Test searching for products.
    """
    search_query = "AI"
    results = await scrape_search(search_query, max_results=5)
    
    assert len(results) > 0, "Search should return at least one result"
    assert len(results) <= 5, "Should respect max_results limit"
    
    # Check structure
    result = results[0]
    assert 'name' in result, "Result should have a name"
    assert 'tagline' in result, "Result should have a tagline"
    assert 'upvotes' in result, "Result should have upvotes"
    assert 'url' in result, "Result should have a URL"
    assert 'search_query' in result, "Result should have search query"
    
    # Verify search query is stored
    assert result['search_query'] == search_query, \
        "Search query should match the one used"
    
    print(f"\n✓ Successfully searched for '{search_query}'")
    print(f"  Found {len(results)} results")
    print(f"  Sample: {result['name']}")


@pytest.mark.asyncio
async def test_archive_scraping():
    """
    Test scraping historical archive data.
    """
    # Scrape from 7 days ago
    archive_date = datetime.now() - timedelta(days=7)
    products = await scrape_archive(archive_date, max_products=3)
    
    assert len(products) > 0, "Archive should return at least one product"
    assert len(products) <= 3, "Should respect max_products limit"
    
    # Check structure
    product = products[0]
    assert 'name' in product, "Product should have a name"
    assert 'tagline' in product, "Product should have a tagline"
    assert 'upvotes' in product, "Product should have upvotes"
    assert 'url' in product, "Product should have a URL"
    assert 'date' in product, "Product should have a date"
    
    # Verify date format
    assert product['date'] == archive_date.strftime('%Y-%m-%d'), \
        "Date should match the requested archive date"
    
    print(f"\n✓ Successfully scraped archive from {archive_date.strftime('%Y-%m-%d')}")
    print(f"  Found {len(products)} products")
    print(f"  Sample: {product['name']} - {product['upvotes']} upvotes")


@pytest.mark.asyncio
async def test_data_consistency():
    """
    Test that scraped data is consistent and properly formatted.
    """
    products = await scrape_daily_products(max_products=2)
    
    for product in products:
        # URLs should be absolute
        assert product['url'].startswith('http'), \
            "URLs should be absolute (start with http)"
        
        # Names should not be empty
        assert len(product['name']) > 0, "Product names should not be empty"
        
        # Upvotes should be numeric string or '0'
        assert product['upvotes'].replace(',', '').replace('K', '').replace('.', '').isdigit() or \
               product['upvotes'] == '0', \
            "Upvotes should be numeric or '0'"
    
    print(f"\n✓ Data consistency checks passed for {len(products)} products")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
