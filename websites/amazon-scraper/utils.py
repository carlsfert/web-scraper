"""
Utility functions for Amazon scraper.
"""

import json
import csv
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def clean_price(price_str: str) -> float:
    """
    Extract numeric price value from price string.
    
    Args:
        price_str: Price string like "$29.99" or "£19.99"
        
    Returns:
        Float value of price, or 0.0 if parsing fails
    """
    if not price_str:
        return 0.0
    
    # Remove currency symbols and extract number
    cleaned = re.sub(r'[^\d.,]', '', price_str)
    cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def clean_rating(rating_str: str) -> float:
    """
    Extract numeric rating value.
    
    Args:
        rating_str: Rating string like "4.5 out of 5 stars"
        
    Returns:
        Float value of rating
    """
    if not rating_str:
        return 0.0
    
    match = re.search(r'([\d.]+)', rating_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0


def clean_review_count(count_str: str) -> int:
    """
    Extract numeric review count.
    
    Args:
        count_str: Count string like "1,234 ratings"
        
    Returns:
        Integer count value
    """
    if not count_str:
        return 0
    
    cleaned = re.sub(r'[^\d]', '', count_str)
    
    try:
        return int(cleaned)
    except ValueError:
        return 0


def extract_asin_from_url(url: str) -> str:
    """
    Extract ASIN from Amazon product URL.
    
    Args:
        url: Amazon product URL
        
    Returns:
        ASIN string
    """
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    
    match = re.search(r'/gp/product/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    
    return ''


def save_to_json(data: Any, filename: str, output_dir: str = 'outputs'):
    """
    Save data to JSON file.
    
    Args:
        data: Data to save (dict or list)
        filename: Output filename
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filepath = output_path / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved to: {filepath}")


def save_to_csv(data: List[Dict], filename: str, output_dir: str = 'outputs'):
    """
    Save data to CSV file.
    
    Args:
        data: List of dictionaries to save
        filename: Output filename
        output_dir: Output directory
    """
    if not data:
        print("No data to save")
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filepath = output_path / filename
    
    # Get all unique keys from all dictionaries
    fieldnames = set()
    for item in data:
        fieldnames.update(item.keys())
    fieldnames = sorted(fieldnames)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data:
            # Convert lists and dicts to JSON strings for CSV
            row = {}
            for key, value in item.items():
                if isinstance(value, (list, dict)):
                    row[key] = json.dumps(value)
                else:
                    row[key] = value
            writer.writerow(row)
    
    print(f"✓ Saved to: {filepath}")


def generate_filename(prefix: str, extension: str = 'json') -> str:
    """
    Generate filename with timestamp.
    
    Args:
        prefix: Filename prefix
        extension: File extension
        
    Returns:
        Generated filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"


def format_product_for_display(product: Dict) -> str:
    """
    Format product data for console display.
    
    Args:
        product: Product dictionary
        
    Returns:
        Formatted string
    """
    lines = [
        "=" * 80,
        f"Title: {product.get('title', 'N/A')}",
        f"ASIN: {product.get('asin', 'N/A')}",
        f"Price: {product.get('price', 'N/A')}",
        f"Rating: {product.get('rating', 'N/A')} ({product.get('reviews_count', '0')} reviews)",
        f"URL: {product.get('url', 'N/A')}",
    ]
    
    if 'brand' in product:
        lines.insert(2, f"Brand: {product['brand']}")
    
    if 'availability' in product:
        lines.append(f"Availability: {product['availability']}")
    
    return '\n'.join(lines)


def format_review_for_display(review: Dict) -> str:
    """
    Format review data for console display.
    
    Args:
        review: Review dictionary
        
    Returns:
        Formatted string
    """
    lines = [
        "-" * 80,
        f"Rating: {'⭐' * int(float(review.get('rating', 0)))}",
        f"Title: {review.get('title', 'N/A')}",
        f"Reviewer: {review.get('reviewer', 'N/A')}",
        f"Date: {review.get('date', 'N/A')}",
        f"Verified: {'Yes' if review.get('verified_purchase') else 'No'}",
        f"\n{review.get('text', '')[:200]}..."
    ]
    
    return '\n'.join(lines)


def validate_asin(asin: str) -> bool:
    """
    Validate Amazon ASIN format.
    
    Args:
        asin: ASIN string to validate
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^[A-Z0-9]{10}$', asin))


def get_domain_from_url(url: str) -> str:
    """
    Extract Amazon domain from URL.
    
    Args:
        url: Amazon URL
        
    Returns:
        Domain (e.g., 'com', 'co.uk')
    """
    match = re.search(r'amazon\.([a-z.]+)', url)
    if match:
        return match.group(1)
    return 'com'


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks.
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_results(*result_lists: List[List[Dict]]) -> List[Dict]:
    """
    Merge multiple result lists, removing duplicates by ASIN.
    
    Args:
        result_lists: Variable number of result lists
        
    Returns:
        Merged list with unique items
    """
    seen_asins = set()
    merged = []
    
    for result_list in result_lists:
        for item in result_list:
            asin = item.get('asin', '')
            if asin and asin not in seen_asins:
                seen_asins.add(asin)
                merged.append(item)
    
    return merged
