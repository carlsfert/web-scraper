"""
Test suite for Trustpilot Scraper

Run tests with: pytest test.py
Run with coverage: pytest test.py --cov=trustpilot --cov-report=html
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from trustpilot import TrustpilotScraper, TrustpilotScraperMonitor


# Test fixtures
@pytest.fixture
def mock_html_response():
    """Mock HTML response with NEXT_DATA"""
    return '''
    <html>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "buildId": "test-build-id-123",
            "props": {
                "pageProps": {
                    "businessUnit": {
                        "displayName": "Test Company",
                        "trustScore": 4.5,
                        "numberOfReviews": {"total": 1000},
                        "isVerified": true,
                        "isClaimed": true,
                        "claimedDate": "2020-01-15T00:00:00Z"
                    },
                    "reviews": [
                        {
                            "id": "review-1",
                            "rating": 5,
                            "title": "Great service",
                            "text": "Amazing experience!",
                            "consumer": {"displayName": "John D."},
                            "labels": {"verification": {"isVerified": true}},
                            "dates": {
                                "publishedDate": "2024-10-15T12:00:00Z",
                                "experiencedDate": "2024-10-10T00:00:00Z"
                            }
                        }
                    ],
                    "businessUnits": {
                        "businesses": [
                            {
                                "displayName": "Company 1",
                                "score": 4.2
                            },
                            {
                                "displayName": "Company 2",
                                "score": 4.8
                            }
                        ]
                    }
                }
            }
        }
        </script>
    </html>
    '''


@pytest.fixture
def mock_api_response():
    """Mock API response for reviews"""
    return {
        "pageProps": {
            "reviews": [
                {
                    "id": "review-1",
                    "rating": 5,
                    "title": "Excellent",
                    "text": "Great product",
                    "consumer": {"displayName": "Alice", "id": "user-1"},
                    "labels": {"verification": {"isVerified": True}},
                    "dates": {
                        "publishedDate": "2024-11-01T10:00:00Z",
                        "experiencedDate": "2024-10-25T00:00:00Z"
                    },
                    "reply": None,
                    "likes": 5
                },
                {
                    "id": "review-2",
                    "rating": 1,
                    "title": "Poor",
                    "text": "Not good",
                    "consumer": {"displayName": "Bob", "id": "user-2"},
                    "labels": {"verification": {"isVerified": False}},
                    "dates": {
                        "publishedDate": "2024-11-01T11:00:00Z",
                        "experiencedDate": "2024-10-26T00:00:00Z"
                    },
                    "reply": {"message": "We're sorry to hear that"},
                    "likes": 2
                }
            ],
            "filters": {
                "pagination": {
                    "totalPages": 5
                }
            }
        }
    }


@pytest.fixture
def scraper():
    """Create a basic scraper instance"""
    return TrustpilotScraper(request_delay=(0.1, 0.2))


# Tests for TrustpilotScraperMonitor
class TestTrustpilotScraperMonitor:
    """Test the performance monitoring class"""
    
    def test_monitor_initialization(self):
        """Test monitor is initialized correctly"""
        monitor = TrustpilotScraperMonitor(window_size=50)
        assert monitor.total_requests == 0
        assert monitor.total_reviews == 0
        assert monitor.last_review_date is None
    
    @pytest.mark.asyncio
    async def test_track_successful_request(self):
        """Test tracking a successful request"""
        monitor = TrustpilotScraperMonitor()
        
        async def mock_func():
            return [{"dates": {"publishedDate": "2024-11-01T10:00:00Z"}}]
        
        result = await monitor.track_request(mock_func)
        
        assert len(result) == 1
        assert monitor.total_requests == 1
        assert monitor.total_reviews == 1
        assert len(monitor.success_rate) == 1
        assert monitor.success_rate[0] == 1
    
    @pytest.mark.asyncio
    async def test_track_failed_request(self):
        """Test tracking a failed request"""
        monitor = TrustpilotScraperMonitor()
        
        async def mock_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await monitor.track_request(mock_func)
        
        assert len(monitor.success_rate) == 1
        assert monitor.success_rate[0] == 0
    
    def test_get_stats(self):
        """Test getting statistics"""
        monitor = TrustpilotScraperMonitor()
        
        # No data yet
        stats = monitor.get_stats()
        assert stats["status"] == "no_data"
        
        # Add some data
        monitor.success_rate.append(1)
        monitor.success_rate.append(1)
        monitor.success_rate.append(0)
        monitor.response_times.append(1.5)
        monitor.response_times.append(2.0)
        monitor.response_times.append(3.0)
        monitor.total_requests = 3
        
        stats = monitor.get_stats()
        assert stats["success_rate"] == pytest.approx(0.667, rel=0.01)
        assert stats["avg_response_time"] == pytest.approx(2.167, rel=0.01)
        assert stats["total_requests"] == 3


# Tests for TrustpilotScraper
class TestTrustpilotScraper:
    """Test the main scraper class"""
    
    def test_scraper_initialization(self):
        """Test scraper is initialized with correct defaults"""
        scraper = TrustpilotScraper()
        assert scraper.max_workers == 5
        assert scraper.request_delay == (1.0, 3.0)
        assert scraper.timeout == 30
        assert scraper.max_retries == 3
        assert scraper.proxies is None
    
    def test_scraper_with_proxies(self):
        """Test scraper initialization with proxies"""
        proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        scraper = TrustpilotScraper(proxies=proxies)
        assert scraper.proxies is not None
        
        # Test proxy cycling
        proxy1 = next(scraper.proxies)
        proxy2 = next(scraper.proxies)
        proxy3 = next(scraper.proxies)
        assert proxy3 == proxy1  # Should cycle back
    
    def test_get_headers(self, scraper):
        """Test header generation"""
        headers = scraper._get_headers()
        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Referer' in headers
        assert headers['DNT'] == '1'
    
    def test_extract_next_data(self, scraper, mock_html_response):
        """Test extracting NEXT_DATA from HTML"""
        data = scraper._extract_next_data(mock_html_response)
        
        assert data['buildId'] == 'test-build-id-123'
        assert 'props' in data
        assert 'pageProps' in data['props']
        assert data['props']['pageProps']['businessUnit']['displayName'] == 'Test Company'
    
    def test_extract_next_data_missing(self, scraper):
        """Test extraction fails when NEXT_DATA is missing"""
        html = '<html><body>No data here</body></html>'
        
        with pytest.raises(ValueError, match="No __NEXT_DATA__ found"):
            scraper._extract_next_data(html)
    
    @pytest.mark.asyncio
    async def test_delay(self, scraper):
        """Test request delay"""
        scraper.request_delay = (0.1, 0.2)
        
        import time
        start = time.time()
        await scraper._delay()
        elapsed = time.time() - start
        
        assert 0.1 <= elapsed <= 0.3  # Allow small margin
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, scraper, mock_html_response):
        """Test successful HTTP request"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.text = mock_html_response
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            response = await scraper._make_request("https://example.com")
            assert response.text == mock_html_response
    
    @pytest.mark.asyncio
    async def test_make_request_retry(self, scraper):
        """Test request retry logic"""
        scraper.request_delay = (0.05, 0.1)
        scraper.max_retries = 2
        
        with patch('httpx.AsyncClient') as mock_client:
            # First two attempts fail, third succeeds
            mock_response_success = MagicMock()
            mock_response_success.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=[
                    httpx.TimeoutException("Timeout"),
                    httpx.HTTPError("Error"),
                    mock_response_success
                ]
            )
            
            response = await scraper._make_request("https://example.com")
            assert response == mock_response_success
    
    @pytest.mark.asyncio
    async def test_make_request_max_retries(self, scraper):
        """Test request fails after max retries"""
        scraper.request_delay = (0.05, 0.1)
        scraper.max_retries = 1
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )
            
            with pytest.raises(httpx.TimeoutException):
                await scraper._make_request("https://example.com")
    
    @pytest.mark.asyncio
    async def test_search_companies(self, scraper, mock_html_response):
        """Test company search functionality"""
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.text = mock_html_response
            mock_request.return_value = mock_response
            
            results = await scraper.search_companies("electronics", pages=2)
            
            assert len(results) == 4  # 2 companies per page, 2 pages
            assert results[0]['displayName'] == 'Company 1'
            assert mock_request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_scrape_company_profile(self, scraper, mock_html_response):
        """Test scraping company profile"""
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.text = mock_html_response
            mock_request.return_value = mock_response
            
            profile = await scraper.scrape_company_profile("test-company.com")
            
            assert profile['domain'] == 'test-company.com'
            assert profile['name'] == 'Test Company'
            assert profile['trust_score'] == 4.5
            assert profile['total_reviews'] == 1000
            assert profile['verified'] is True
            assert 'scraped_at' in profile
    
    @pytest.mark.asyncio
    async def test_scrape_company_reviews(self, scraper, mock_html_response, mock_api_response):
        """Test scraping company reviews"""
        with patch.object(scraper, '_make_request') as mock_request:
            # First call returns HTML with build ID
            mock_html = MagicMock()
            mock_html.text = mock_html_response
            
            # Second call returns API response
            mock_api = MagicMock()
            mock_api.json.return_value = mock_api_response
            
            mock_request.side_effect = [mock_html, mock_api]
            
            reviews = await scraper.scrape_company_reviews("test-company.com", max_pages=1)
            
            assert len(reviews) == 2
            assert reviews[0]['id'] == 'review-1'
            assert reviews[0]['rating'] == 5
            assert reviews[0]['company_domain'] == 'test-company.com'
            assert reviews[0]['verified'] is True
            assert reviews[1]['company_reply'] == "We're sorry to hear that"
    
    @pytest.mark.asyncio
    async def test_scrape_company_reviews_with_filters(self, scraper, mock_html_response, mock_api_response):
        """Test scraping reviews with filters"""
        with patch.object(scraper, '_make_request') as mock_request:
            mock_html = MagicMock()
            mock_html.text = mock_html_response
            
            mock_api = MagicMock()
            mock_api.json.return_value = mock_api_response
            
            mock_request.side_effect = [mock_html, mock_api]
            
            reviews = await scraper.scrape_company_reviews(
                "test-company.com",
                max_pages=1,
                stars="5",
                verified_only=True,
                sort="highest_rated"
            )
            
            assert len(reviews) == 2
            # Verify the request was made with correct parameters
            call_args = mock_request.call_args_list[1]
            params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('params')
            assert params['stars'] == '5'
            assert params['verified'] == 'true'
            assert params['sort'] == 'highest_rated'
    
    @pytest.mark.asyncio
    async def test_scrape_category(self, scraper, mock_html_response):
        """Test scraping category"""
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.text = mock_html_response
            mock_request.return_value = mock_response
            
            results = await scraper.scrape_category("electronics_technology", pages=1)
            
            assert len(results) == 2
            assert results[0]['displayName'] == 'Company 1'
    
    @pytest.mark.asyncio
    async def test_scrape_multiple_companies(self, scraper, mock_html_response, mock_api_response):
        """Test scraping multiple companies"""
        with patch.object(scraper, '_make_request') as mock_request:
            mock_html = MagicMock()
            mock_html.text = mock_html_response
            
            mock_api = MagicMock()
            mock_api.json.return_value = mock_api_response
            
            # Return alternating HTML and API responses
            mock_request.side_effect = [mock_html, mock_api, mock_html, mock_api]
            
            companies = ["company1.com", "company2.com"]
            results = await scraper.scrape_multiple_companies(companies, max_pages_per_company=1)
            
            assert len(results) == 2
            assert "company1.com" in results
            assert "company2.com" in results
            assert len(results["company1.com"]) == 2  # 2 reviews per company
    
    @pytest.mark.asyncio
    async def test_error_handling(self, scraper):
        """Test error handling in scraping methods"""
        with patch.object(scraper, '_make_request') as mock_request:
            mock_request.side_effect = Exception("Network error")
            
            with pytest.raises(Exception):
                await scraper.scrape_company_profile("test.com")


# Integration tests
class TestIntegration:
    """Integration tests (these may make real requests if not mocked)"""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Integration test - uncomment to test with real API")
    async def test_real_search(self):
        """Test real search (requires internet connection)"""
        scraper = TrustpilotScraper(request_delay=(2, 3))
        results = await scraper.search_companies("amazon", pages=1)
        assert len(results) > 0
        assert any('amazon' in r.get('displayName', '').lower() for r in results)
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Integration test - uncomment to test with real API")
    async def test_real_company_profile(self):
        """Test real company profile scraping"""
        scraper = TrustpilotScraper(request_delay=(2, 3))
        profile = await scraper.scrape_company_profile("amazon.com")
        assert profile['name']
        assert profile['trust_score'] > 0
        assert profile['total_reviews'] > 0


# Test utilities
def test_imports():
    """Test all required imports are available"""
    import httpx
    import parsel
    import aiofiles
    assert httpx
    assert parsel
    assert aiofiles


def test_module_exports():
    """Test module exports correct classes"""
    from trustpilot import TrustpilotScraper, TrustpilotScraperMonitor
    assert TrustpilotScraper
    assert TrustpilotScraperMonitor


if __name__ == "__main__":
    # Run tests with: python test.py
    pytest.main([__file__, "-v", "--tb=short"])
