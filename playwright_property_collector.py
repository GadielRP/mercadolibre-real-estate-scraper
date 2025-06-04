#!/usr/bin/env python3
"""
Playwright MercadoLibre Property Collector
Handles JavaScript-rendered content using Playwright
"""

import asyncio
import json
import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser

@dataclass
class PropertyData:
    """Property data structure"""
    id: str
    title: str
    price: str
    currency: str
    location: str
    url: str
    thumbnail: str
    attributes: Dict[str, str]
    seller_info: Dict[str, str]
    collected_at: str

class PlaywrightPropertyCollector:
    """Property collector using Playwright for JavaScript-rendered content"""
    
    def __init__(self):
        self.base_url = "https://inmuebles.mercadolibre.com.mx"
        self.collected_properties: List[PropertyData] = []
        
    async def collect_properties(self, search_type: str = "venta", max_pages: int = 2) -> List[PropertyData]:
        """
        Collect properties using Playwright
        
        Args:
            search_type: "venta" (sale) or "renta" (rent)
            max_pages: Maximum pages to scrape
        """
        print(f"🏠 Starting Playwright property collection: {search_type}")
        print(f"🎯 Target: {max_pages} pages")
        print("=" * 60)
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,  # Set to False to see the browser
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            # Create context with realistic settings
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='es-MX'
            )
            
            page = await context.new_page()
            properties = []
            
            try:
                for page_num in range(1, max_pages + 1):
                    print(f"\n📄 Scraping page {page_num}...")
                    
                    # Construct URL with pagination
                    if page_num == 1:
                        url = f"{self.base_url}/{search_type}"
                    else:
                        offset = (page_num - 1) * 48
                        url = f"{self.base_url}/{search_type}_Desde_{offset + 1}"
                    
                    page_properties = await self._scrape_page(page, url)
                    properties.extend(page_properties)
                    
                    print(f"   ✅ Collected {len(page_properties)} properties from page {page_num}")
                    print(f"   📊 Total so far: {len(properties)} properties")
                    
                    # Rate limiting
                    await asyncio.sleep(3)
                    
                    # Stop if no properties found
                    if len(page_properties) == 0:
                        print(f"   ⚠️ No properties found on page {page_num}, stopping...")
                        break
                        
            finally:
                await browser.close()
        
        self.collected_properties = properties
        print(f"\n🎉 Collection complete! Total: {len(properties)} properties")
        return properties
    
    async def _scrape_page(self, page: Page, url: str) -> List[PropertyData]:
        """Scrape a single page using Playwright"""
        try:
            print(f"   🌐 Navigating to: {url}")
            
            # Navigate to page
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for property listings to load
            print(f"   ⏳ Waiting for property listings to load...")
            
            # Try multiple selectors to find property containers
            selectors_to_try = [
                'div[class*="ui-search-result"]',
                'div[class*="search-result"]',
                'article',
                'div[class*="item"]',
                '.ui-search-results .ui-search-result',
                '[data-testid*="result"]'
            ]
            
            property_containers = []
            for selector in selectors_to_try:
                try:
                    await page.wait_for_selector(selector, timeout=10000)
                    containers = await page.query_selector_all(selector)
                    if containers:
                        property_containers = containers
                        print(f"   🔍 Found {len(containers)} containers with selector: {selector}")
                        break
                except:
                    continue
            
            if not property_containers:
                # Try waiting a bit more and check page content
                await asyncio.sleep(5)
                page_content = await page.content()
                print(f"   📄 Page content length: {len(page_content)} characters")
                
                # Check if we can find any property-related content
                if "inmueble" in page_content.lower() or "propiedad" in page_content.lower():
                    print(f"   🔍 Found property-related content, but no containers with known selectors")
                    # Try to extract from page content directly
                    return await self._extract_from_page_content(page)
                else:
                    print(f"   ❌ No property content found on page")
                    return []
            
            # Extract properties from containers
            properties = []
            for container in property_containers:
                property_data = await self._extract_property_from_element(page, container)
                if property_data:
                    properties.append(property_data)
            
            return properties
            
        except Exception as e:
            print(f"   ❌ Error scraping page: {e}")
            return []
    
    async def _extract_property_from_element(self, page: Page, element) -> Optional[PropertyData]:
        """Extract property data from a Playwright element"""
        try:
            # Extract property URL and ID
            title_link = await element.query_selector('a')
            if not title_link:
                return None
            
            property_url = await title_link.get_attribute('href') or ""
            property_id = self._extract_id_from_url(property_url)
            
            # Extract title
            title_text = await title_link.text_content() or ""
            
            # Extract price
            price_elem = await element.query_selector('span[class*="money-amount"]')
            price = await price_elem.text_content() if price_elem else "0"
            
            # Extract currency
            currency_elem = await element.query_selector('span[class*="currency"]')
            currency = await currency_elem.text_content() if currency_elem else "MXN"
            
            # Extract location
            location_elem = await element.query_selector('span[class*="location"], span[class*="group__element"]')
            location = await location_elem.text_content() if location_elem else ""
            
            # Extract thumbnail
            img_elem = await element.query_selector('img')
            thumbnail = await img_elem.get_attribute('src') if img_elem else ""
            
            # Create property data
            property_data = PropertyData(
                id=property_id,
                title=title_text.strip(),
                price=price.strip(),
                currency=currency.strip(),
                location=location.strip(),
                url=property_url,
                thumbnail=thumbnail,
                attributes={},
                seller_info={},
                collected_at=datetime.now().isoformat()
            )
            
            return property_data
            
        except Exception as e:
            print(f"     ⚠️ Error extracting property: {e}")
            return None
    
    async def _extract_from_page_content(self, page: Page) -> List[PropertyData]:
        """Extract properties directly from page content when containers aren't found"""
        try:
            print(f"   🔍 Attempting to extract from page content...")
            
            # Look for property links in the page
            links = await page.query_selector_all('a[href*="MLM"]')
            properties = []
            
            for link in links:
                href = await link.get_attribute('href') or ""
                if '/MLM-' in href and ('casa' in href or 'departamento' in href or 'inmueble' in href):
                    text = await link.text_content() or ""
                    
                    property_data = PropertyData(
                        id=self._extract_id_from_url(href),
                        title=text.strip(),
                        price="0",
                        currency="MXN",
                        location="",
                        url=href,
                        thumbnail="",
                        attributes={},
                        seller_info={},
                        collected_at=datetime.now().isoformat()
                    )
                    
                    if property_data.id:  # Only add if we found a valid ID
                        properties.append(property_data)
            
            # Remove duplicates
            unique_properties = []
            seen_ids = set()
            for prop in properties:
                if prop.id not in seen_ids:
                    unique_properties.append(prop)
                    seen_ids.add(prop.id)
            
            print(f"   📝 Extracted {len(unique_properties)} properties from page content")
            return unique_properties
            
        except Exception as e:
            print(f"   ❌ Error extracting from page content: {e}")
            return []
    
    def _extract_id_from_url(self, url: str) -> str:
        """Extract property ID from MercadoLibre URL"""
        match = re.search(r'/MLM-(\d+)-', url)
        if match:
            return f"MLM{match.group(1)}"
        return ""
    
    def save_to_json(self, filename: str = None) -> str:
        """Save collected properties to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mercadolibre_properties_playwright_{timestamp}.json"
        
        # Convert dataclasses to dictionaries
        properties_dict = [asdict(prop) for prop in self.collected_properties]
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        filepath = data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'collection_info': {
                    'total_properties': len(self.collected_properties),
                    'collected_at': datetime.now().isoformat(),
                    'source': 'MercadoLibre Mexico Real Estate (Playwright)',
                    'method': 'JavaScript-enabled scraping'
                },
                'properties': properties_dict
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Data saved to: {filepath}")
        return str(filepath)
    
    def print_summary(self):
        """Print collection summary"""
        if not self.collected_properties:
            print("❌ No properties collected")
            return
        
        print(f"\n📊 COLLECTION SUMMARY")
        print("=" * 50)
        print(f"Total Properties: {len(self.collected_properties)}")
        
        # Show sample properties
        print(f"\n📋 SAMPLE PROPERTIES:")
        for i, prop in enumerate(self.collected_properties[:5]):
            print(f"\n{i+1}. {prop.title[:60]}...")
            print(f"   💰 Price: {prop.currency} {prop.price}")
            print(f"   📍 Location: {prop.location}")
            print(f"   🆔 ID: {prop.id}")
            print(f"   🔗 URL: {prop.url[:80]}...")

async def main():
    """Main execution function"""
    print("🏠 Playwright MercadoLibre Property Collector")
    print("Handles JavaScript-rendered content")
    print("=" * 60)
    
    collector = PlaywrightPropertyCollector()
    
    # Collect properties
    properties = await collector.collect_properties(search_type="venta", max_pages=2)
    
    if properties:
        # Print summary
        collector.print_summary()
        
        # Save to JSON
        filepath = collector.save_to_json()
        
        print(f"\n✅ SUCCESS! Collected {len(properties)} properties")
        print(f"📁 Data saved to: {filepath}")
    else:
        print("❌ No properties collected. The site might have changed or be blocking automated access.")

if __name__ == "__main__":
    asyncio.run(main()) 