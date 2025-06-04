#!/usr/bin/env python3
"""
Inspect MercadoLibre HTML Structure
Analyze the actual HTML to find correct CSS selectors
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List

def inspect_mercadolibre_page():
    """Inspect the actual MercadoLibre real estate page structure"""
    
    # Test different URL patterns
    urls_to_test = [
        "https://inmuebles.mercadolibre.com.mx/venta",
        "https://listado.mercadolibre.com.mx/inmuebles/casas/venta",
        "https://listado.mercadolibre.com.mx/inmuebles/venta",
        "https://listado.mercadolibre.com.mx/inmuebles"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    for url in urls_to_test:
        print(f"\n🔍 INSPECTING: {url}")
        print("=" * 80)
        
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for common property listing patterns
            selectors_to_test = [
                # Common MercadoLibre selectors
                'div[class*="ui-search-result"]',
                'div[class*="search-result"]',
                'div[class*="item"]',
                'div[class*="listing"]',
                'div[class*="product"]',
                'article',
                'li[class*="result"]',
                'div[class*="card"]',
                
                # Title selectors
                'h2[class*="title"]',
                'h3[class*="title"]',
                'a[class*="title"]',
                
                # Price selectors
                'span[class*="price"]',
                'span[class*="money"]',
                'div[class*="price"]',
                
                # Link selectors
                'a[href*="MLM"]',
                'a[href*="/item"]',
                'a[href*="inmueble"]'
            ]
            
            print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"📊 Page size: {len(response.text)} characters")
            
            # Test each selector
            for selector in selectors_to_test:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    
                    # Show first element details
                    if len(elements) > 0:
                        first_elem = elements[0]
                        print(f"   📝 First element classes: {first_elem.get('class', [])}")
                        print(f"   📝 First element tag: {first_elem.name}")
                        
                        # If it's a link, show href
                        if first_elem.name == 'a' and first_elem.get('href'):
                            print(f"   🔗 First link href: {first_elem.get('href')[:100]}...")
                        
                        # Show text content (first 100 chars)
                        text = first_elem.get_text(strip=True)
                        if text:
                            print(f"   📄 First element text: {text[:100]}...")
                        
                        print()
            
            # Look for property IDs in the HTML
            property_links = soup.find_all('a', href=True)
            mlm_links = [link for link in property_links if 'MLM' in link.get('href', '')]
            
            if mlm_links:
                print(f"🎯 Found {len(mlm_links)} MLM property links:")
                for i, link in enumerate(mlm_links[:5]):  # Show first 5
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    print(f"   {i+1}. {href}")
                    print(f"      Text: {text[:80]}...")
                    print()
            
            # Look for JSON data in script tags
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and ('window.__PRELOADED_STATE__' in script.string or 'window.INITIAL_STATE' in script.string):
                    print("🎯 Found potential JSON data in script tag!")
                    print(f"   Script content preview: {script.string[:200]}...")
                    break
            
            print(f"✅ Successfully analyzed {url}")
            break  # If successful, don't try other URLs
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error accessing {url}: {e}")
            continue
        except Exception as e:
            print(f"❌ Error parsing {url}: {e}")
            continue
    
    print("\n" + "=" * 80)
    print("🎯 INSPECTION COMPLETE")

if __name__ == "__main__":
    inspect_mercadolibre_page() 