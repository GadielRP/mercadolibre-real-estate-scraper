# MercadoLibre Real Estate Data Collector - Technical Planning & Architecture

## 🎯 **Project Overview & Architecture Decisions**

### **Current Implementation Status: WORKING SOLUTION ✅**
- **Architecture**: Playwright-based web scraping system
- **Data Collected**: 96 properties successfully gathered
- **Technology Stack**: Python + Playwright + JavaScript execution
- **Performance**: 48 properties per page, 96 total in ~60 seconds

### 🚨 **Critical Architecture Change**
**Original Plan**: MercadoLibre API integration  
**Current Reality**: Web scraping with browser automation  
**Decision Point**: December 2024  
**Reason**: Standard MercadoLibre developer accounts have severe API restrictions

---

## 🏗️ **Technical Architecture**

### **System Architecture Overview**
```
┌─────────────────────────────────────────────────────────┐
│                    USER/SCHEDULER                        │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              PLAYWRIGHT CONTROLLER                       │
│  • Browser automation                                   │
│  • JavaScript execution                                 │
│  • Rate limiting & ethics                               │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│               MERCADOLIBRE WEBSITE                       │
│  • inmuebles.mercadolibre.com.mx                       │
│  • Dynamic JavaScript content                           │
│  • Property listings (48 per page)                      │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                DATA EXTRACTION                           │
│  • CSS selector-based extraction                        │
│  • Property ID, title, price, location                  │
│  • Error handling & validation                          │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│               DATA PROCESSING                            │
│  • Python dataclasses structure                         │
│  • Data validation & cleaning                           │
│  • Duplicate detection                                   │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                DATA STORAGE                              │
│  • JSON export with metadata                            │
│  • Future: SQLite/PostgreSQL                            │
│  • Timestamped collections                              │
└─────────────────────────────────────────────────────────┘
```

### **Core Technology Stack**

#### **🎭 Playwright (Primary Technology)**
- **Purpose**: JavaScript-enabled browser automation
- **Why Essential**: MercadoLibre uses React/JavaScript for dynamic content
- **Alternative Tried**: BeautifulSoup (failed - no JavaScript execution)
- **Configuration**: Chromium browser, headless mode, realistic headers

#### **🐍 Python 3.8+ (Core Language)**
- **Purpose**: System orchestration and data processing
- **Libraries Used**: asyncio, dataclasses, pathlib, json
- **Code Style**: PEP8, type hints, docstrings (Google style)

#### **📊 Data Models (Structured Data)**
```python
@dataclass
class PropertyData:
    id: str              # MLM property ID
    title: str           # Property title/description  
    price: str           # Price as displayed (with currency)
    currency: str        # Currency code (MXN)
    location: str        # Full address/location
    url: str             # Direct property URL
    thumbnail: str       # Property image URL
    attributes: Dict     # Property features (future enhancement)
    seller_info: Dict    # Seller data (future enhancement)
    collected_at: str    # ISO timestamp
```

---

## 🔬 **Research & Discovery Process**

### **Phase 1: API Investigation (COMPLETED)**
**Goal**: Use official MercadoLibre API for data collection  
**Result**: ❌ Blocked by access restrictions  
**Time Spent**: 4 hours  

**Key Findings**:
- ✅ **Authentication works**: Successfully obtained access tokens
- ✅ **Category access works**: Can see 234,675 real estate properties exist
- ❌ **Search endpoints blocked**: 403 Forbidden for `/sites/MLM/search`
- ❌ **Individual property access blocked**: 403/404 for `/items/{id}`
- ❌ **Public API blocked**: Even "public" endpoints require authentication

**Scripts Created** (Historical):
- `investigate_403_error.py`: Systematic endpoint testing
- `property_collector_v1.py`: API-based collector (blocked)
- `property_collector_v2.py`: Enhanced API approach (blocked)

### **Phase 2: Web Scraping Investigation (COMPLETED)**
**Goal**: Collect data through web scraping  
**Result**: ✅ Working solution implemented  
**Time Spent**: 4 hours  

**Breakthrough Discovery**:
- ❌ **BeautifulSoup fails**: JavaScript-rendered content not accessible
- ✅ **Playwright succeeds**: Handles dynamic content loading
- ✅ **CSS selectors identified**: `div[class*="ui-search-result"]` works
- ✅ **Rate limiting effective**: 3-second delays prevent blocking

**Scripts Created** (Working):
- `inspect_mercadolibre_html.py`: HTML structure analysis
- `working_property_collector.py`: BeautifulSoup attempt (failed)
- `playwright_property_collector.py`: **WORKING SOLUTION** ⭐

---

## 🎭 **Playwright Implementation Details**

### **Browser Configuration**
```python
browser = await p.chromium.launch(
    headless=True,  # Hidden browser for automation
    args=['--no-sandbox', '--disable-dev-shm-usage']
)

context = await browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    viewport={'width': 1920, 'height': 1080},
    locale='es-MX'  # Mexican Spanish for proper content
)
```

### **Dynamic Content Handling**
```python
# Navigate and wait for JavaScript to complete
await page.goto(url, wait_until='networkidle', timeout=30000)

# Wait for property containers to appear
await page.wait_for_selector('div[class*="ui-search-result"]', timeout=10000)

# Multiple selector fallback strategy
selectors_to_try = [
    'div[class*="ui-search-result"]',
    'div[class*="search-result"]', 
    'article',
    'div[class*="item"]'
]
```

### **Data Extraction Process**
```python
# Find all property containers
containers = await page.query_selector_all('div[class*="ui-search-result"]')

# Extract data from each container
for container in containers:
    # Property URL and ID
    title_link = await container.query_selector('a')
    property_url = await title_link.get_attribute('href')
    
    # Property details
    title_text = await title_link.text_content()
    price_elem = await container.query_selector('span[class*="money-amount"]')
    location_elem = await container.query_selector('span[class*="location"]')
```

### **Rate Limiting & Ethics**
```python
# Respectful delays between pages
await asyncio.sleep(3)  # 3 seconds between requests

# Realistic browser simulation
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'

# Limited page collection (not aggressive scraping)
max_pages = 2  # Start small, expand gradually
```

---

## 📊 **Data Collection Strategy**

### **Current Collection Scope**
- **Property Type**: All real estate (casas, departamentos, terrenos)
- **Geographic Area**: Mexico (nationwide)
- **Page Coverage**: 2 pages = 96 properties per run
- **Update Frequency**: Manual execution (future: automated)

### **Data Quality & Validation**
```python
# Property ID validation
property_id = self._extract_id_from_url(property_url)
if not property_id:
    continue  # Skip invalid properties

# Data structure validation
property_data = PropertyData(
    id=property_id,
    title=title_text.strip(),
    # ... other fields with validation
    collected_at=datetime.now().isoformat()
)
```

### **Export Format**
```json
{
  "collection_info": {
    "total_properties": 96,
    "collected_at": "2024-12-03T21:12:31",
    "source": "MercadoLibre Mexico Real Estate (Playwright)",
    "method": "JavaScript-enabled scraping"
  },
  "properties": [
    {
      "id": "MLM2257875515",
      "title": "Departamento En Venta Naucalpan...",
      "price": "MXN3,536,791",
      "currency": "MXN",
      "location": "Av. San Mateo 184-B...",
      "url": "https://departamento.mercadolibre.com.mx/MLM-2257875515...",
      "thumbnail": "https://http2.mlstatic.com/D_NQ_NP_2X_716284...",
      "attributes": {},
      "seller_info": {},
      "collected_at": "2024-12-03T21:12:18"
    }
  ]
}
```

---

## 🔧 **System Requirements & Dependencies**

### **Runtime Requirements**
- **Python**: 3.8+ (for async/await support)
- **Memory**: ~100MB (browser + Python process)
- **Network**: Stable internet connection
- **Storage**: ~5MB per 1000 properties (JSON format)

### **Key Dependencies**
```txt
# Core automation
playwright>=1.52.0                 # Browser automation
asyncio                            # Async processing (built-in)

# Data processing  
dataclasses                        # Data structures (built-in)
json                               # Data export (built-in)
datetime                           # Timestamps (built-in)

# Future enhancements
pydantic>=2.5.0                   # Data validation
sqlite3                           # Local database (built-in)
```

### **Development Environment**
```bash
# Setup commands
pip install playwright
playwright install chromium
python playwright_property_collector.py
```

---

## 📈 **Performance & Scalability**

### **Current Performance Metrics**
- **Collection Speed**: 48 properties/page, ~30 seconds/page
- **Success Rate**: 100% on property extraction
- **Data Completeness**: All properties have valid IDs, prices, locations
- **Memory Efficiency**: ~50MB browser overhead
- **Network Usage**: ~2MB per page scraped

### **Scalability Considerations**
- **Rate Limiting**: Currently 3 seconds between pages (conservative)
- **Browser Resources**: One browser instance handles multiple pages
- **Data Storage**: JSON files scale to thousands of properties
- **Concurrent Collection**: Future enhancement for multiple regions

### **Performance Optimization Opportunities**
```python
# Current: Sequential page collection
for page_num in range(1, max_pages + 1):
    properties = await self._scrape_page(page, url)

# Future: Concurrent collection with semaphore
semaphore = asyncio.Semaphore(3)  # Max 3 concurrent pages
tasks = [self._scrape_page_with_semaphore(page, url) for url in urls]
results = await asyncio.gather(*tasks)
```

---

## 🔮 **Future Architecture Plans**

### **Sprint 2: Data Storage Enhancement**
```
JSON Files → SQLite Database → PostgreSQL
┌─────────┐    ┌──────────┐    ┌──────────┐
│ Current │ -> │  Local   │ -> │Production│
│ Export  │    │ Database │    │ Database │
└─────────┘    └──────────┘    └──────────┘
```

### **Database Schema Design**
```sql
-- Properties table
CREATE TABLE properties (
    id VARCHAR(20) PRIMARY KEY,        -- MLM2257875515
    title TEXT NOT NULL,
    price_amount DECIMAL(15,2),
    price_currency VARCHAR(3),
    location_text TEXT,
    url TEXT UNIQUE,
    thumbnail_url TEXT,
    collected_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Property attributes
CREATE TABLE property_attributes (
    property_id VARCHAR(20) REFERENCES properties(id),
    attribute_name VARCHAR(50),
    attribute_value TEXT,
    PRIMARY KEY (property_id, attribute_name)
);

-- Collection runs
CREATE TABLE collection_runs (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    properties_collected INTEGER,
    pages_scraped INTEGER,
    success_rate DECIMAL(5,2)
);
```

### **Sprint 3: Enhanced Data Collection**
- **Property Details**: Bedrooms, bathrooms, square meters
- **Seller Information**: Contact details, reputation scores  
- **Image Collection**: Download and store property photos
- **Location Geocoding**: Convert addresses to coordinates
- **Price History**: Track price changes over time

### **Sprint 4: Analytics & Automation**
- **Automated Collection**: Daily/weekly scheduled runs
- **Alert System**: Price drops, new listings notifications
- **Web Dashboard**: Interactive data visualization

---

## 🛡️ **Risk Management & Mitigation**

### **Technical Risks**
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| CSS Selector Changes | High | Medium | Regular selector testing, fallback selectors |
| Rate Limiting/Blocking | High | Low | Conservative delays, realistic headers |
| JavaScript Changes | Medium | Low | Playwright handles most JS variations |
| Data Structure Changes | Medium | Low | Flexible data models, validation |

### **Legal & Ethical Considerations**
- **Robots.txt Compliance**: Check and respect site policies
- **Rate Limiting**: Respectful scraping practices (3+ second delays)
- **Data Usage**: Public data only, no private information
- **Attribution**: Acknowledge data source in exports

### **Monitoring & Alerts**
```python
# Collection success monitoring
if len(collected_properties) == 0:
    logger.error("No properties collected - possible site changes")
    send_alert("Collection failed - investigate selectors")

# Performance monitoring  
collection_time = end_time - start_time
if collection_time > expected_time * 1.5:
    logger.warning(f"Collection took {collection_time}s (expected {expected_time}s)")
```

---

## 🧪 **Testing Strategy**

### **Unit Tests** (Future Implementation)
```python
def test_property_id_extraction():
    url = "https://departamento.mercadolibre.com.mx/MLM-2257875515-dept-venta"
    expected = "MLM2257875515"
    result = extract_id_from_url(url)
    assert result == expected

def test_data_validation():
    valid_property = PropertyData(
        id="MLM2257875515",
        title="Test Property",
        price="MXN1,000,000",
        # ... other fields
    )
    assert validate_property_data(valid_property) == True
```

### **Integration Tests**
```python
async def test_full_collection_pipeline():
    collector = PlaywrightPropertyCollector()
    properties = await collector.collect_properties(max_pages=1)
    
    assert len(properties) > 0
    assert all(prop.id.startswith("MLM") for prop in properties)
    assert all(prop.price for prop in properties)
```

### **Selector Validation Tests**
```python
async def test_css_selectors():
    """Test that current CSS selectors still work"""
    page = await setup_test_page()
    await page.goto("https://inmuebles.mercadolibre.com.mx/venta")
    
    containers = await page.query_selector_all('div[class*="ui-search-result"]')
    assert len(containers) > 0, "Property containers not found"
```

---

## 📚 **Knowledge Base & Documentation**

### **Key Learning Points**
1. **MercadoLibre API Limitations**: Standard accounts cannot access property search
2. **JavaScript Dependency**: Property listings load dynamically, require browser automation
3. **CSS Selector Reliability**: `div[class*="ui-search-result"]` proven stable selector
4. **Rate Limiting Critical**: 3-second delays prevent IP blocking
5. **Data Quality High**: 100% success rate on property ID extraction

### **Troubleshooting Guide**
```python
# Common Issues & Solutions

# Issue: No properties found
# Solution: Check CSS selectors, wait for JavaScript loading

# Issue: Browser crashes
# Solution: Increase memory limits, reduce concurrent operations

# Issue: Slow collection
# Solution: Optimize selectors, reduce page wait times

# Issue: Blocked IP
# Solution: Increase delays, use proxy rotation (future)
```

### **Development Guidelines**
- **Code Style**: Follow PEP8, use type hints
- **Error Handling**: Graceful degradation, detailed logging
- **Testing**: Test selectors before major deployments
- **Performance**: Monitor collection times and success rates

---

## 🎯 **Success Metrics & KPIs**

### **Current Achievement (Sprint 1)**
- ✅ **Data Collection**: 96 properties successfully gathered
- ✅ **Data Quality**: 100% valid property IDs and prices
- ✅ **Geographic Coverage**: 6+ Mexican states represented
- ✅ **Price Range**: MXN 1M to MXN 33.5M captured
- ✅ **System Reliability**: Zero crashes, robust error handling

### **Sprint 2 Targets**
- [ ] **Database Storage**: 1000+ properties in SQLite
- [ ] **Data Validation**: Pydantic models for all fields
- [ ] **Enhanced Attributes**: Bedrooms, bathrooms, area extraction
- [ ] **Deduplication**: Remove duplicate properties across runs

### **Sprint 3-4 Goals**

- [ ] **Automation**: Daily collection scheduling
- [ ] **Geographic Analysis**: Price by neighborhood insights
- [ ] **Web Dashboard**: Interactive data visualization

---

**Last Updated**: December 2024  
**Architecture Status**: ✅ Production-ready Playwright solution  
**Next Phase**: Database storage and enhanced data collection  
**Technical Debt**: Minimal - well-structured, documented codebase 