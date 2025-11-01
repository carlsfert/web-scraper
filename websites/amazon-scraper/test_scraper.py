"""
Unit tests for Amazon scraper.

Run tests with:
    pytest tests/test_scraper.py
    
Run specific tests:
    pytest tests/test_scraper.py -k test_search
    pytest tests/test_scraper.py -k test_product_details
    pytest tests/test_scraper.py -k test_reviews
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from amazon_scraper import AmazonScraper
from utils import (
    clean_price,
    clean_rating,
    clean_review_count,
    extract_asin_from_url,
    validate_asin
)


@pytest.mark.asyncio
async def test_search_products():
    """Test searching for products."""
    async with AmazonScraper(domain='com', headless=True) as scraper:
        results = await scraper.search_products(
            query='python book',
            max_pages=1,
            max_results=3
        )
        
        assert len(results) > 0, "Should return at least one result"
        assert len(results) <= 3, "Should respect max_results limit"
        
        # Check first result structure
        product = results[0]
        assert 'asin' in product, "Product should have ASIN"
        assert 'title' in product, "Product should have title"
        assert 'price' in product, "Product should have price"
        assert 'rating' in product, "Product should have rating"
        assert 'url' in product, "Product should have URL"
        
        # Verify ASIN format
        assert len(product['asin']) == 10, "ASIN should be 10 characters"
        
        # Verify URL format
        assert 'amazon.com' in product['url'], "URL should be Amazon URL"
        assert product['asin'] in product['url'], "URL should contain ASIN"
        
        print(f"\n✓ Successfully scraped {len(results)} products")
        print(f"  Sample: {product['title'][:50]}...")


@pytest.mark.asyncio
async def test_get_product_details():
    """Test getting detailed product information."""
    async with AmazonScraper(domain='com', headless=True) as scraper:
        # First search for a product
        search_results = await scraper.search_products('laptop', max_results=1)
        assert len(search_results) > 0, "Need at least one product"
        
        asin = search_results[0]['asin']
        
        # Get product details
        product = await scraper.get_product_details(asin)
        
        # Check required fields
        assert 'asin' in product, "Product should have ASIN"
        assert 'title' in product, "Product should have title"
        assert 'price' in product, "Product should have price"
        assert 'description' in product, "Product should have description"
        assert 'images' in product, "Product should have images"
        assert 'url' in product, "Product should have URL"
        
        # Verify data types
        assert isinstance(product['title'], str), "Title should be string"
        assert isinstance(product['images'], list), "Images should be list"
        assert isinstance(product.get('categories', []), list), "Categories should be list"
        assert isinstance(product.get('specifications', {}), dict), "Specifications should be dict"
        
        # ASIN should match
        assert product['asin'] == asin, "ASIN should match requested ASIN"
        
        print(f"\n✓ Successfully scraped product details")
        print(f"  Title: {product['title'][:50]}...")
        print(f"  Price: {product['price']}")
        print(f"  Images: {len(product['images'])} found")


@pytest.mark.asyncio
async def test_get_product_reviews():
    """Test getting product reviews."""
    async with AmazonScraper(domain='com', headless=True) as scraper:
        # First search for a product
        search_results = await scraper.search_products('headphones', max_results=1)
        assert len(search_results) > 0, "Need at least one product"
        
        asin = search_results[0]['asin']
        
        # Get reviews
        reviews = await scraper.get_product_reviews(
            asin=asin,
            max_pages=1,
            max_reviews=3
        )
        
        if len(reviews) > 0:  # Some products might not have reviews
            assert len(reviews) <= 3, "Should respect max_reviews limit"
            
            # Check review structure
            review = reviews[0]
            assert 'rating' in review, "Review should have rating"
            assert 'title' in review, "Review should have title"
            assert 'text' in review, "Review should have text"
            assert 'reviewer' in review, "Review should have reviewer"
            assert 'date' in review, "Review should have date"
            assert 'verified_purchase' in review, "Review should have verified flag"
            assert 'asin' in review, "Review should have ASIN"
            
            # ASIN should match
            assert review['asin'] == asin, "Review ASIN should match product ASIN"
            
            print(f"\n✓ Successfully scraped {len(reviews)} reviews")
            print(f"  Sample: {review['title'][:50]}...")
        else:
            print(f"\n✓ Test passed (no reviews available for this product)")


def test_clean_price():
    """Test price cleaning utility."""
    assert clean_price("$29.99") == 29.99
    assert clean_price("£19.99") == 19.99
    assert clean_price("€15.50") == 15.50
    assert clean_price("$1,234.56") == 1234.56
    assert clean_price("") == 0.0
    assert clean_price("N/A") == 0.0
    print("\n✓ Price cleaning tests passed")


def test_clean_rating():
    """Test rating extraction."""
    assert clean_rating("4.5 out of 5 stars") == 4.5
    assert clean_rating("4.5") == 4.5
    assert clean_rating("3") == 3.0
    assert clean_rating("") == 0.0
    print("\n✓ Rating extraction tests passed")


def test_clean_review_count():
    """Test review count extraction."""
    assert clean_review_count("1,234 ratings") == 1234
    assert clean_review_count("123") == 123
    assert clean_review_count("") == 0
    print("\n✓ Review count extraction tests passed")


def test_extract_asin_from_url():
    """Test ASIN extraction from URLs."""
    url1 = "https://www.amazon.com/dp/B08N5WRWNW/"
    assert extract_asin_from_url(url1) == "B08N5WRWNW"
    
    url2 = "https://www.amazon.com/gp/product/B08N5WRWNW/"
    assert extract_asin_from_url(url2) == "B08N5WRWNW"
    
    url3 = "https://www.amazon.com/some-product/dp/B08N5WRWNW/ref=sr_1_1"
    assert extract_asin_from_url(url3) == "B08N5WRWNW"
    
    print("\n✓ ASIN extraction tests passed")


def test_validate_asin():
    """Test ASIN validation."""
    assert validate_asin("B08N5WRWNW") == True
    assert validate_asin("123456789") == False
    assert validate_asin("B08N5WRWNW1") == False
    assert validate_asin("b08n5wrwnw") == False
    assert validate_asin("") == False
    
    print("\n✓ ASIN validation tests passed")


@pytest.mark.asyncio
async def test_scraper_context_manager():
    """Test scraper can be used as context manager."""
    async with AmazonScraper(domain='com') as scraper:
        assert scraper.browser is not None, "Browser should be initialized"
    
    print("\n✓ Context manager test passed")


@pytest.mark.asyncio
async def test_multiple_domains():
    """Test scraper works with different Amazon domains."""
    domains_to_test = ['com', 'co.uk']
    
    for domain in domains_to_test:
        async with AmazonScraper(domain=domain, headless=True) as scraper:
            results = await scraper.search_products('book', max_results=1)
            
            if len(results) > 0:
                assert f'amazon.{domain}' in scraper.base_url
                print(f"✓ Successfully tested amazon.{domain}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
