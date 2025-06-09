"""
Cliente API para MercadoLibre

Implementa consultas a la API oficial de MercadoLibre para búsqueda de inmuebles.
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import os
from loguru import logger

@dataclass
class SearchParams:
    """Parámetros de búsqueda para inmuebles"""
    category_id: str = "MLA1459"  # Inmuebles
    state_id: Optional[str] = None  # Estado/Provincia 
    city_id: Optional[str] = None   # Ciudad
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    operation_type: Optional[str] = None  # "rent" o "sale"
    property_type: Optional[str] = None   # "house", "apartment", etc.
    limit: int = 50
    offset: int = 0

class MercadoLibreAPIClient:
    """Cliente API para MercadoLibre"""
    
    BASE_URL = "https://api.mercadolibre.com"
    
    def __init__(self, access_token: str = None):
        """
        Initialize API client.
        
        Args:
            access_token (str): Token de acceso OAuth (opcional, se carga desde archivo)
        """
        self.access_token = access_token or self._load_access_token()
        self.session = requests.Session()
        
        # Rate limiting (MercadoLibre tiene límites)
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms entre requests
        
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            logger.info("🔑 Cliente API inicializado con token de acceso")
        else:
            logger.warning("⚠️ Cliente API sin token - solo consultas públicas disponibles")
    
    def _load_access_token(self) -> Optional[str]:
        """Load access token from file"""
        token_file = Path('ml_token.json')
        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                return token_data.get('access_token')
            except Exception as e:
                logger.warning(f"No se pudo cargar token: {e}")
        return None
    
    def _wait_rate_limit(self):
        """Respect rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with rate limiting and error handling.
        
        Args:
            endpoint (str): API endpoint
            params (Dict): Query parameters
            
        Returns:
            Dict: API response
        """
        self._wait_rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            logger.debug(f"🌐 API Request: {endpoint}")
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"✅ API Response: {len(str(data))} chars")
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error {response.status_code}: {e}")
            if response.status_code == 401:
                logger.error("🔑 Token de acceso inválido o expirado")
            elif response.status_code == 429:
                logger.error("⏰ Rate limit excedido - esperando...")
                time.sleep(60)  # Wait 1 minute
                return self._make_request(endpoint, params)
            raise
        except Exception as e:
            logger.error(f"❌ Error en request: {e}")
            raise
    
    def search_properties(self, search_params: SearchParams) -> Dict:
        """
        Buscar propiedades en MercadoLibre.
        
        Args:
            search_params (SearchParams): Parámetros de búsqueda
            
        Returns:
            Dict: Respuesta de la API con propiedades encontradas
        """
        logger.info(f"🔍 Buscando propiedades: {search_params}")
        
        # Construir parámetros de búsqueda
        params = {
            'category': search_params.category_id,
            'limit': search_params.limit,
            'offset': search_params.offset
        }
        
        # Filtros opcionales
        if search_params.state_id:
            params['state'] = search_params.state_id
        if search_params.city_id:
            params['city'] = search_params.city_id
        if search_params.price_min:
            params['price'] = f"{search_params.price_min}-"
        if search_params.price_max:
            if search_params.price_min:
                params['price'] = f"{search_params.price_min}-{search_params.price_max}"
            else:
                params['price'] = f"-{search_params.price_max}"
        
        # Realizar búsqueda
        response = self._make_request('/sites/MLA/search', params)
        
        logger.info(f"✅ Encontradas {response.get('paging', {}).get('total', 0)} propiedades")
        return response
    
    def get_property_details(self, item_id: str) -> Dict:
        """
        Obtener detalles completos de una propiedad.
        
        Args:
            item_id (str): ID del item en MercadoLibre
            
        Returns:
            Dict: Detalles completos de la propiedad
        """
        logger.debug(f"📋 Obteniendo detalles: {item_id}")
        
        response = self._make_request(f'/items/{item_id}')
        logger.debug(f"✅ Detalles obtenidos para {item_id}")
        return response
    
    def get_property_description(self, item_id: str) -> Dict:
        """
        Obtener descripción de una propiedad.
        
        Args:
            item_id (str): ID del item
            
        Returns:
            Dict: Descripción de la propiedad
        """
        logger.debug(f"📄 Obteniendo descripción: {item_id}")
        
        response = self._make_request(f'/items/{item_id}/description')
        logger.debug(f"✅ Descripción obtenida para {item_id}")
        return response
    
    def get_locations(self, query: str) -> List[Dict]:
        """
        Buscar ubicaciones (estados, ciudades).
        
        Args:
            query (str): Término de búsqueda
            
        Returns:
            List[Dict]: Lista de ubicaciones encontradas
        """
        logger.debug(f"📍 Buscando ubicaciones: {query}")
        
        params = {'q': query}
        response = self._make_request('/classified_locations/search', params)
        
        locations = response.get('results', [])
        logger.debug(f"✅ Encontradas {len(locations)} ubicaciones")
        return locations
    
    def get_categories(self) -> List[Dict]:
        """
        Obtener categorías disponibles.
        
        Returns:
            List[Dict]: Lista de categorías
        """
        logger.debug("📂 Obteniendo categorías")
        
        response = self._make_request('/sites/MLA/categories')
        logger.debug(f"✅ {len(response)} categorías obtenidas")
        return response

# Función de utilidad para testing
def test_api_client():
    """Test básico del cliente API"""
    
    print("🧪 TESTING MERCADOLIBRE API CLIENT")
    print("="*50)
    
    # Inicializar cliente
    client = MercadoLibreAPIClient()
    
    # Test 1: Buscar propiedades básico
    print("\n1️⃣ Búsqueda básica de propiedades...")
    search_params = SearchParams(limit=5)  # Solo 5 para testing
    
    try:
        results = client.search_properties(search_params)
        print(f"✅ {results['paging']['total']} propiedades encontradas")
        
        # Mostrar primeras propiedades
        for item in results['results'][:3]:
            print(f"   - {item['title'][:60]}...")
            print(f"     💰 ${item['price']:,} {item['currency_id']}")
            print(f"     📍 {item['location']['address_line']}")
            print()
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    # Test 2: Obtener detalles de una propiedad
    if 'results' in locals() and results['results']:
        item_id = results['results'][0]['id']
        print(f"\n2️⃣ Detalles de propiedad {item_id}...")
        
        try:
            details = client.get_property_details(item_id)
            print(f"✅ Detalles obtenidos")
            print(f"   - Título: {details['title']}")
            print(f"   - Precio: ${details['price']:,} {details['currency_id']}")
            
            # Atributos de la propiedad
            if 'attributes' in details:
                for attr in details['attributes'][:5]:  # Primeros 5 atributos
                    print(f"   - {attr['name']}: {attr.get('value_name', 'N/A')}")
                    
        except Exception as e:
            print(f"❌ Error obteniendo detalles: {e}")
    
    print("\n🎉 Testing completado!")

if __name__ == "__main__":
    test_api_client() 