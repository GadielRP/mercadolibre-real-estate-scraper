#!/usr/bin/env python3
"""
MODELOS Y CONFIGURACIONES - SCRAPER MERCADOLIBRE
==============================================

Dataclasses y configuraciones para el sistema híbrido de scraping.
Separado para cumplir con reglas de modularidad (<500 líneas).
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ProxyConfig:
    """Configuración de proxy con detalles de autenticación"""
    host: str
    port: int
    username: str = ""
    password: str = ""
    protocol: str = "http"
    location: str = ""
    
    def to_playwright_format(self) -> Dict[str, str]:
        """Convierte a formato de Playwright"""
        proxy_dict = {
            "server": f"{self.protocol}://{self.host}:{self.port}"
        }
        if self.username and self.password:
            proxy_dict["username"] = self.username
            proxy_dict["password"] = self.password
        return proxy_dict


@dataclass
class ConfiguracionHibridaUltraAvanzada:
    """Configuración híbrida ultra avanzada"""
    
    # ✅ PROXIES DESHABILITADOS para testing sin romper el programa
    PROXIES_RESIDENCIALES = [
        # Lista vacía para testing directo sin proxies
        # Cuando tengas proxies reales, agregar aquí:
        # ProxyConfig("mx-proxy1.realservice.com", 8080, "user1", "pass1", "http", "MX"),
    ]
    
    # URLs base para recolección automática de propiedades en Morelos
    URLS_BUSQUEDA_MORELOS = [
        "https://inmuebles.mercadolibre.com.mx/casas/venta/morelos/",
        "https://inmuebles.mercadolibre.com.mx/venta/morelos/casas/",
        "https://listado.mercadolibre.com.mx/inmuebles/casas/venta/morelos/",
        "https://inmuebles.mercadolibre.com.mx/casas/venta/cuernavaca/",
        "https://inmuebles.mercadolibre.com.mx/casas/venta/jiutepec/",
    ]
    
    # ✅ User-Agents DESKTOP específicos (2025 actualizados)
    USER_AGENTS_WINDOWS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    ]
    
    USER_AGENTS_MAC = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]
    
    # ✅ Viewports DESKTOP para evitar vista móvil/tablet
    VIEWPORTS = [
        {"width": 1920, "height": 1080},  # ✅ MAYOR prioridad - Full HD
        {"width": 2560, "height": 1440},  # ✅ AGREGADO - 2K 
        {"width": 1600, "height": 900},   # ✅ AGREGADO - Wider
        {"width": 1536, "height": 864},   # ✅ MANTENIDO
        # {"width": 1366, "height": 768},   # ❌ REMOVIDO - muy pequeño
        # {"width": 1440, "height": 900},   # ❌ REMOVIDO - problemático
    ]
    
    # Delays humanos optimizados para velocidad
    HUMAN_DELAYS = {
        'page_load_wait': (1.5, 3.0),      # Reducido de (3.0, 6.0)
        'between_actions': (0.5, 1.0),     # Reducido de (1.0, 2.0)
        'scroll_pause': (0.3, 0.6),        # Reducido de (0.5, 1.0)
        'between_properties': (1.0, 2.0),  # Reducido de (2.0, 4.0)
    }
    
    # URLs de entrada graduales
    ENTRY_URLS = [
        "https://www.mercadolibre.com.mx/",
        "https://inmuebles.mercadolibre.com.mx/",
        "https://inmuebles.mercadolibre.com.mx/casas/venta/morelos/"
    ]


@dataclass
class ResultadoPropiedad:
    """Resultado de extracción con metadata completa - ENFOQUE HÍBRIDO 2025"""
    url: str
    
    # ✅ CAMPOS UNIVERSALES ESTRUCTURADOS (para consultas SQL eficientes)
    recamaras: Optional[int] = None
    banos: Optional[float] = None
    construccion: Optional[float] = None  # superficie_construida 
    terreno: Optional[float] = None       # superficie_total
    estacionamiento: Optional[int] = None
    precio: Optional[float] = None
    moneda: Optional[str] = None
    direccion: Optional[str] = None
    tipo_propiedad: Optional[str] = None
    tipo_operacion: Optional[str] = None
    
    # 🆕 CAMPOS ADICIONALES UNIVERSALES PARA DB
    ml_id: Optional[str] = None
    titulo: Optional[str] = None
    descripcion: str = ""
    pais: Optional[str] = 'México'
    estado: Optional[str] = None
    ciudad: Optional[str] = None
    
    # 🔄 CAMPOS JSON FLEXIBLES (máxima flexibilidad)
    caracteristicas_principales: Optional[dict] = None  # Antigüedad, orientación, mantenimiento, etc.
    servicios: Optional[dict] = None                    # Internet, A/C, gas, cisterna, etc.
    ambientes: Optional[dict] = None                    # Alberca, jardín, terraza, jacuzzi, etc.
    seguridad: Optional[dict] = None                    # Alarma, seguridad, portón eléctrico, etc.
    comodidades: Optional[dict] = None                  # Gimnasio, área de juegos, etc.
    
    # ✅ DATOS RAW COMPLETOS (backup total)
    andes_table_raw: Optional[dict] = None              # Tabla andes completa como JSON
    
    # ✅ METADATOS DEL SISTEMA
    status: str = "pendiente"
    error: Optional[str] = None
    timestamp: str = ""
    user_agent_usado: str = ""
    proxy_usado: str = "" 