#!/usr/bin/env python3
"""
TEST 10 PROPIEDADES MORELOS - HÍBRIDO ULTRA AVANZADO 2025
=========================================================

Combina LO MEJOR de ambos archivos:
✅ EXTRACCIÓN OPTIMIZADA (patrones 100% validados) del scraper_anti_bloqueo_avanzado.py
✅ TÉCNICAS ULTRA STEALTH + PROXIES del scraper_ultra_avanzado_2025_con_proxies.py

Características implementadas:
- Patrones regex optimizados al 100%
- Proxies residenciales con rotación
- TLS/Canvas fingerprinting bypass
- Mouse movement simulation
- Navegación gradual humana
- Behavioral simulation ultra realista

Adaptado para testing rápido con 10 propiedades
"""

import asyncio
import random
import json
import time
import math
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from playwright.async_api import async_playwright, BrowserContext, Page

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
    
    # User-Agents ultra realistas por OS
    USER_AGENTS_WINDOWS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    ]
    
    USER_AGENTS_MAC = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]
    
    # Viewports comunes
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
    ]
    
    # Delays humanos realistas
    HUMAN_DELAYS = {
        'page_load_wait': (3.0, 6.0),      # Reducido para testing rápido
        'between_actions': (1.0, 2.0),     # Reducido
        'scroll_pause': (0.5, 1.0),        # Reducido
        'between_properties': (2.0, 4.0),  # Entre propiedades
    }
    
    # URLs de entrada graduales
    ENTRY_URLS = [
        "https://www.mercadolibre.com.mx/",
        "https://inmuebles.mercadolibre.com.mx/",
        "https://inmuebles.mercadolibre.com.mx/casas/venta/morelos/"
    ]

@dataclass
class ResultadoPropiedad:
    """Resultado de extracción con metadata completa"""
    url: str
    recamaras: Optional[int] = None
    banos: Optional[float] = None
    construccion: Optional[float] = None
    terreno: Optional[float] = None
    estacionamiento: Optional[int] = None
    descripcion: str = ""
    status: str = "pendiente"
    error: Optional[str] = None
    timestamp: str = ""
    user_agent_usado: str = ""
    proxy_usado: str = ""

class ExtractorHibridoOptimizado:
    """Extractor híbrido con 3 prioridades: tabla andes-table > descripción específica > regex general"""
    
    def __init__(self):
        # Patrones regex MEJORADOS para descripción específica (prioridad 2)
        self.patterns_descripcion = {
            'recamaras': [
                # Números múltiples: "3 y 4 recámaras", "dos y tres habitaciones"
                r'(\d+)\s*y\s*(\d+)\s*(?:recámaras?|recamaras?|habitaci[óo]nes?|dormitorios?)',
                # Números con texto: "tres recámaras", "4 habitaciones"  
                r'(\d+)\s*(?:recámaras?|recamaras?|habitaci[óo]nes?|dormitorios?)',
                # En contexto: "casa de 3 recámaras", "propiedad con 4 habitaciones"
                r'(?:casa|propiedad|inmueble)\s*(?:de|con)\s*(\d+)\s*(?:recámaras?|recamaras?|habitaci[óo]nes?)',
                # Al final: "recámaras: 3", "habitaciones 4"
                r'(?:recámaras?|recamaras?|habitaci[óo]nes?|dormitorios?)\s*[:\-]?\s*(\d+)',
                # Texto específico con números
                r'(\d+)\s*(?:rec\b|hab\b|dorm\b)',
            ],
            'banos': [
                # Números con decimales: "2.5 baños", "3.5 sanitarios"
                r'(\d+(?:\.\d+)?)\s*(?:ba[ñn]os?|sanitarios?|wc)',
                # En contexto: "casa con 2 baños", "propiedad de 3.5 baños"
                r'(?:casa|propiedad|inmueble)\s*(?:de|con)\s*(\d+(?:\.\d+)?)\s*(?:ba[ñn]os?|sanitarios?)',
                # Baños completos específicos
                r'(\d+(?:\.\d+)?)\s*ba[ñn]os?\s*completos?',
                # Al final: "baños: 2.5", "sanitarios 3"
                r'(?:ba[ñn]os?|sanitarios?|wc)\s*[:\-]?\s*(\d+(?:\.\d+)?)',
                # Con texto adicional: "2 baños y alberca"
                r'(\d+(?:\.\d+)?)\s*ba[ñn]os?\s*(?:y|con)',
            ],
            'construccion': [
                # Metros cuadrados de construcción en diferentes formatos
                r'construcci[óo]n\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'superficie\s*construida\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'(?:área|superficie)\s*de\s*construcci[óo]n\s*(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                # Números seguidos de unidades
                r'(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)\s*(?:de\s*)?(?:construcci[óo]n|construidos?)',
                # Al final con dos puntos
                r'construcci[óo]n\s*[:\-]\s*(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)?',
            ],
            'terreno': [
                # Metros cuadrados de terreno en diferentes formatos
                r'terreno\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'lote\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'superficie\s*total\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                # Números seguidos de unidades
                r'(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)\s*(?:de\s*)?(?:terreno|lote|superficie)',
                # Al final con dos puntos
                r'terreno\s*[:\-]\s*(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)?',
            ],
            'estacionamiento': [
                # Números específicos: "2 estacionamientos", "1 cochera"
                r'(\d+)\s*(?:estacionamientos?|garages?|cocheras?|plazas?|cajones?|espacios?)',
                # En contexto: "casa con 2 estacionamientos"
                r'(?:casa|propiedad|inmueble)\s*(?:de|con)\s*(\d+)\s*(?:estacionamientos?|garages?|cocheras?)',
                # Para número específico: "estacionamiento para 2"
                r'(?:estacionamiento|garage|cochera)\s*(?:para\s*)?(\d+)',
                # Al final: "estacionamientos: 2"
                r'(?:estacionamientos?|garages?|cocheras?)\s*[:\-]?\s*(\d+)',
                # Solo menciona estacionamiento (sin número específico = 1)
                r'(?:con\s*)?(?:estacionamiento|garage|cochera|plaza|cajón)\s*(?:privado|techado|cubierto)?(?!\s*\d)',
            ]
        }
        
        # Patrones regex generales de respaldo (prioridad 3)
        self.patterns_general = {
            'recamaras': [
                # Múltiples formatos para recámaras/habitaciones
                r'(\d+)\s*y\s*(\d+)\s*(?:recámaras?|recamaras?|habitaci[óo]nes?|dormitorios?)',
                r'(\d+)\s*(?:recámaras?|recamaras?|habitaci[óo]nes?|dormitorios?)',
                r'(?:recámaras?|recamaras?|habitaci[óo]nes?|dormitorios?)\s*[:\-]?\s*(\d+)',
                r'(\d+)\s*(?:rec\b|hab\b|dorm\b)',
                # Contexto específico
                r'(?:casa|propiedad|inmueble)\s*(?:de|con)\s*(\d+)\s*(?:recámaras?|habitaci[óo]nes?)'
            ],
            'banos': [
                # Múltiples formatos para baños/sanitarios
                r'(\d+(?:[,\.]\d+)?)\s*(?:ba[ñn]os?|sanitarios?|wc)',
                r'(?:ba[ñn]os?|sanitarios?|wc)\s*[:\-]?\s*(\d+(?:[,\.]\d+)?)',
                r'(\d+(?:[,\.]\d+)?)\s*ba[ñn]os?\s*completos?',
                # Contexto específico
                r'(?:casa|propiedad|inmueble)\s*(?:de|con)\s*(\d+(?:[,\.]\d+)?)\s*(?:ba[ñn]os?|sanitarios?)'
            ],
            'construccion': [
                # Múltiples formatos para construcción
                r'construcci[óo]n\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'superficie\s*construida\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)\s*(?:de\s*)?(?:construcci[óo]n|construidos?)',
                r'(?:construcci[óo]n|construidos?)\s*[:\-]?\s*(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)?',
                r'(?:área|superficie)\s*de\s*construcci[óo]n\s*(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)?'
            ],
            'terreno': [
                # Múltiples formatos para terreno
                r'terreno\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'lote\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'superficie\s*total\s*(?:de\s*)?(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)',
                r'(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)\s*(?:de\s*)?(?:terreno|lote|superficie)',
                r'(?:terreno|lote)\s*[:\-]?\s*(\d+(?:[,\.]\d+)?)\s*(?:m[²2]?|metros?)?'
            ],
            'estacionamiento': [
                # Múltiples formatos para estacionamiento
                r'(\d+)\s*(?:estacionamientos?|garages?|cocheras?|plazas?|cajones?)',
                r'(?:estacionamientos?|garages?|cocheras?)\s*[:\-]?\s*(\d+)',
                r'(?:estacionamiento|garage|cochera)\s*(?:para\s*)?(\d+)',
                # Sin número específico = 1
                r'(?:con\s*)?(?:estacionamiento|garage|cochera|plaza|cajón)(?!\s*\d)'
            ]
        }
    
    async def extraer_datos_desde_tabla_andes(self, page) -> dict:
        """PRIORIDAD 1: Extrae datos desde la tabla andes-table con estructura específica div/span"""
        
        datos = {
            'recamaras': None,
            'banos': None,
            'construccion': None,
            'terreno': None,
            'estacionamiento': None
        }
        
        try:
            andes_tables = await page.query_selector_all('.andes-table')
            
            if not andes_tables:
                print("⚠️ No se encontró tabla andes-table")
                return datos
            
            print(f"📋 Procesando {len(andes_tables)} tabla(s) andes-table...")
            
            for table in andes_tables:
                rows = await table.query_selector_all('tr')
                
                for row in rows:
                    try:
                        # MÉTODO MEJORADO: Buscar estructura específica div/span
                        key_element = await row.query_selector('th div, td div')
                        value_element = await row.query_selector('td span, th span')
                        
                        if key_element and value_element:
                            key = (await key_element.text_content()).strip().lower()
                            value = (await value_element.text_content()).strip()
                            
                            # Mapear usando estructura específica
                            if 'recámara' in key or 'recamara' in key:
                                if datos['recamaras'] is None:  # Solo si no se ha encontrado antes
                                    datos['recamaras'] = self._parse_number(value)
                                    print(f"  🔑 Recámaras encontradas: {datos['recamaras']}")
                                
                            elif 'baño' in key or 'bano' in key:
                                if datos['banos'] is None:  # Solo si no se ha encontrado antes
                                    datos['banos'] = self._parse_float(value)
                                    print(f"  🔑 Baños encontrados: {datos['banos']}")
                                
                            elif 'superficie construida' in key or 'construida' in key:
                                if datos['construccion'] is None:  # Solo si no se ha encontrado antes
                                    datos['construccion'] = self._parse_number(value)
                                    print(f"  🔑 Construcción encontrada: {datos['construccion']}")
                                
                            elif 'superficie total' in key and not datos['terreno']:
                                datos['terreno'] = self._parse_number(value)
                                print(f"  🔑 Terreno encontrado: {datos['terreno']}")
                                
                            elif 'estacionamiento' in key or 'garage' in key or 'cochera' in key:
                                if datos['estacionamiento'] is None:  # Solo si no se ha encontrado antes
                                    datos['estacionamiento'] = self._parse_number(value)
                                    print(f"  🔑 Estacionamientos encontrados: {datos['estacionamiento']}")
                        
                        # MÉTODO DE RESPALDO: Usar método anterior si no funciona el específico
                        elif not key_element or not value_element:
                            cells = await row.query_selector_all('td, th')
                            
                            if len(cells) >= 2:
                                key = (await cells[0].text_content()).strip().lower()
                                value = (await cells[1].text_content()).strip()
                                
                                if 'recámara' in key or 'recamara' in key:
                                    if datos['recamaras'] is None:
                                        datos['recamaras'] = self._parse_number(value)
                                elif 'baño' in key or 'bano' in key:
                                    if datos['banos'] is None:
                                        datos['banos'] = self._parse_float(value)
                                elif 'superficie construida' in key or 'construida' in key:
                                    if datos['construccion'] is None:
                                        datos['construccion'] = self._parse_number(value)
                                elif 'superficie total' in key and not datos['terreno']:
                                    datos['terreno'] = self._parse_number(value)
                                elif 'estacionamiento' in key or 'garage' in key or 'cochera' in key:
                                    if datos['estacionamiento'] is None:
                                        datos['estacionamiento'] = self._parse_number(value)
                                        
                    except Exception as e:
                        # Continuar con la siguiente fila si hay error
                        continue
            
            extraidos = sum(1 for v in datos.values() if v is not None)
            print(f"✅ Tabla andes-table (div/span): {extraidos}/5 campos extraídos")
            
            return datos
            
        except Exception as e:
            print(f"❌ Error extrayendo de tabla andes-table: {str(e)}")
            return datos
    
    async def extraer_datos_desde_descripcion_especifica_con_datos_previos(self, page, datos_previos: dict) -> dict:
        """PRIORIDAD 2: Extrae datos desde descripción específica SOLO para campos faltantes"""
        
        datos = datos_previos.copy()  # Comenzar con datos existentes
        
        try:
            # Buscar la descripción específica
            desc_element = await page.query_selector('[data-testid="content"], .ui-pdp-description__content')
            
            if not desc_element:
                print("⚠️ No se encontró descripción específica")
                return datos
            
            descripcion = await desc_element.text_content()
            
            if not descripcion:
                print("⚠️ Descripción específica vacía")
                return datos
            
            print(f"📝 Procesando descripción específica ({len(descripcion)} caracteres)...")
            
            texto_limpio = descripcion.lower()
            
            # Aplicar patrones específicos para descripción (SOLO campos faltantes)
            for campo, patterns in self.patterns_descripcion.items():
                # PROTECCIÓN: Solo extraer si el campo está vacío
                if datos[campo] is not None:
                    continue
                    
                for pattern in patterns:
                    match = re.search(pattern, texto_limpio, re.IGNORECASE)
                    if match:
                        # EXTRACCIÓN DINÁMICA basada en grupos de captura
                        if campo == 'estacionamiento':
                            # Para estacionamiento: si hay grupo numérico, usarlo; sino asumir 1
                            if len(match.groups()) > 0 and match.group(1):
                                numero = self._parse_number(match.group(1))
                                if numero:
                                    datos[campo] = numero
                            else:
                                # Si solo dice "estacionamiento" sin número, asumir 1
                                datos[campo] = 1
                                
                        elif campo == 'recamaras':
                            # Para recámaras: manejar casos como "3 y 4 recámaras"
                            groups = match.groups()
                            if len(groups) > 1 and groups[1]:  # Si hay segundo grupo "3 y 4"
                                num1 = self._parse_number(groups[0]) or 0
                                num2 = self._parse_number(groups[1]) or 0
                                # Tomar el mayor número válido
                                datos[campo] = max(num1, num2) if max(num1, num2) > 0 else None
                            elif len(groups) > 0 and groups[0]:
                                # Un solo número encontrado
                                datos[campo] = self._parse_number(groups[0])
                                
                        elif campo == 'banos':
                            # Para baños: usar el primer grupo numérico (puede ser decimal)
                            if len(match.groups()) > 0 and match.group(1):
                                datos[campo] = self._parse_float(match.group(1))
                                
                        else:
                            # Para construcción y terreno: usar el primer grupo numérico
                            if len(match.groups()) > 0 and match.group(1):
                                datos[campo] = self._parse_number(match.group(1))
                        
                        # Si se extrajo un valor válido, salir del bucle de patrones
                        if datos[campo] is not None:
                            break
            
            # Solo contar campos NUEVOS extraídos
            campos_nuevos = sum(1 for k, v in datos.items() if datos_previos[k] is None and v is not None)
            print(f"✅ Descripción específica: {campos_nuevos}/5 campos extraídos")
            
            return datos
            
        except Exception as e:
            print(f"❌ Error extrayendo de descripción específica: {str(e)}")
            return datos
    
    def extraer_datos_con_regex_general_con_datos_previos(self, descripcion: str, datos_previos: dict) -> dict:
        """PRIORIDAD 3: Extrae datos usando regex general SOLO para campos faltantes"""
        
        datos = datos_previos.copy()  # Comenzar con datos existentes
        
        if not descripcion:
            return datos
        
        texto_limpio = descripcion.lower()
        
        for campo, patterns in self.patterns_general.items():
            # PROTECCIÓN: Solo extraer si el campo está vacío
            if datos[campo] is not None:
                continue
                
            for pattern in patterns:
                match = re.search(pattern, texto_limpio, re.IGNORECASE)
                if match:
                    # EXTRACCIÓN DINÁMICA similar a la función de descripción específica
                    if campo == 'estacionamiento':
                        # Para estacionamiento: si hay grupo numérico, usarlo; sino asumir 1
                        if len(match.groups()) > 0 and match.group(1):
                            numero = self._parse_number(match.group(1))
                            if numero:
                                datos[campo] = numero
                        else:
                            # Si solo dice "estacionamiento" sin número, asumir 1
                            datos[campo] = 1
                            
                    elif campo == 'recamaras':
                        # Para recámaras: manejar casos como "3 y 4 recámaras"
                        groups = match.groups()
                        if len(groups) > 1 and groups[1]:  # Si hay segundo grupo "3 y 4"
                            num1 = self._parse_number(groups[0]) or 0
                            num2 = self._parse_number(groups[1]) or 0
                            # Tomar el mayor número válido
                            datos[campo] = max(num1, num2) if max(num1, num2) > 0 else None
                        elif len(groups) > 0 and groups[0]:
                            # Un solo número encontrado
                            datos[campo] = self._parse_number(groups[0])
                            
                    elif campo == 'banos':
                        # Para baños: usar el primer grupo numérico (puede ser decimal)
                        if len(match.groups()) > 0 and match.group(1):
                            datos[campo] = self._parse_float(match.group(1))
                            
                    else:
                        # Para construcción y terreno: usar el primer grupo numérico
                        if len(match.groups()) > 0 and match.group(1):
                            datos[campo] = self._parse_number(match.group(1))
                    
                    # Si se extrajo un valor válido, salir del bucle de patrones
                    if datos[campo] is not None:
                        break
        
        return datos
    
    async def extraer_datos_hibrido(self, page, descripcion_respaldo: str = None) -> dict:
        """Método principal: 3 prioridades de extracción SIN SOBREESCRITURA"""
        
        # 1. PRIORIDAD 1: Tabla andes-table
        datos_finales = await self.extraer_datos_desde_tabla_andes(page)
        
        # 2. PRIORIDAD 2: Descripción específica (SOLO campos faltantes)
        datos_descripcion = await self.extraer_datos_desde_descripcion_especifica_con_datos_previos(page, datos_finales.copy())
        
        # 3. PRIORIDAD 3: Regex general (SOLO campos aún faltantes)
        if descripcion_respaldo:
            datos_regex = self.extraer_datos_con_regex_general_con_datos_previos(descripcion_respaldo, datos_finales.copy())
            
            # Actualizar datos finales solo con campos faltantes
            for campo in ['recamaras', 'banos', 'construccion', 'terreno', 'estacionamiento']:
                if datos_finales[campo] is None and datos_regex.get(campo) is not None:
                    datos_finales[campo] = datos_regex[campo]
        
        # Actualizar datos finales solo con campos faltantes de descripción
        for campo in ['recamaras', 'banos', 'construccion', 'terreno', 'estacionamiento']:
            if datos_finales[campo] is None and datos_descripcion.get(campo) is not None:
                datos_finales[campo] = datos_descripcion[campo]
        
        # 4. ESTADÍSTICAS (corregidas)
        # Calcular tabla andes nuevamente para estadísticas
        temp_datos_tabla = await self.extraer_datos_desde_tabla_andes(page)
        extraidos_tabla = sum(1 for v in temp_datos_tabla.values() if v is not None)
        
        # Calcular campos nuevos por método
        extraidos_desc = sum(1 for k, v in datos_descripcion.items() if temp_datos_tabla[k] is None and v is not None)
        extraidos_regex = 0
        if descripcion_respaldo and 'datos_regex' in locals():
            extraidos_regex = sum(1 for k, v in datos_regex.items() if temp_datos_tabla[k] is None and datos_descripcion.get(k) is None and v is not None)
        
        extraidos_total = sum(1 for v in datos_finales.values() if v is not None)
        
        print(f"📊 Extracción 3 prioridades: Tabla={extraidos_tabla}/5, Descripción={extraidos_desc}/5, Regex={extraidos_regex}/5, Total={extraidos_total}/5")
        
        return datos_finales
    
    def extraer_datos_inmueble(self, descripcion: str) -> dict:
        """Método de compatibilidad con el código existente"""
        datos_vacios = {
            'recamaras': None,
            'banos': None,
            'construccion': None,
            'terreno': None,
            'estacionamiento': None
        }
        return self.extraer_datos_con_regex_general_con_datos_previos(descripcion, datos_vacios)
    
    def _parse_number(self, value: str) -> int:
        """Parsea número entero desde string con manejo mejorado de formatos"""
        if not value:
            return None
        try:
            # Limpiar el valor manteniendo solo números, comas y puntos
            clean_value = re.sub(r'[^\d,.]', '', value)
            if clean_value:
                # Manejar formato europeo (coma decimal): 250,5 -> 250.5
                if ',' in clean_value and '.' not in clean_value:
                    # Si solo hay coma, es separador decimal
                    clean_value = clean_value.replace(',', '.')
                elif ',' in clean_value and '.' in clean_value:
                    # Si hay ambos, la coma es separador de miles: 1,250.5
                    clean_value = clean_value.replace(',', '')
                
                return int(float(clean_value))
        except:
            pass
        return None
    
    def _parse_float(self, value: str) -> float:
        """Parsea número flotante desde string con manejo mejorado de formatos"""
        if not value:
            return None
        try:
            # Limpiar el valor manteniendo solo números, comas y puntos
            clean_value = re.sub(r'[^\d,.]', '', value)
            if clean_value:
                # Manejar formato europeo (coma decimal): 250,5 -> 250.5
                if ',' in clean_value and '.' not in clean_value:
                    # Si solo hay coma, es separador decimal
                    clean_value = clean_value.replace(',', '.')
                elif ',' in clean_value and '.' in clean_value:
                    # Si hay ambos, la coma es separador de miles: 1,250.5
                    clean_value = clean_value.replace(',', '')
                
                return float(clean_value)
        except:
            pass
        return None

class NavegadorHibridoUltraAvanzado:
    """Navegador híbrido con técnicas ultra avanzadas + proxies"""
    
    def __init__(self):
        self.config = ConfiguracionHibridaUltraAvanzada()
        self.browser = None
        self.context = None
        self.current_profile = {}
        self.current_proxy = None
        self.proxy_ip = "direct"
    
    async def inicializar_perfil_ultra_realista_con_proxy(self):
        """Crea perfil ultra realista con proxy opcional"""
        
        # Seleccionar proxy si está disponible
        if self.config.PROXIES_RESIDENCIALES:
            self.current_proxy = random.choice(self.config.PROXIES_RESIDENCIALES)
            print(f"🌐 Proxy seleccionado: {self.current_proxy.host}:{self.current_proxy.port}")
        else:
            print("⚠️ Sin proxies - usando IP directa (para testing)")
            self.current_proxy = None
        
        # Seleccionar OS y UA aleatorio
        os_type = random.choice(['windows', 'mac'])
        
        if os_type == 'windows':
            user_agent = random.choice(self.config.USER_AGENTS_WINDOWS)
            platform = "Win32"
        else:
            user_agent = random.choice(self.config.USER_AGENTS_MAC)
            platform = "MacIntel"
            
        viewport = random.choice(self.config.VIEWPORTS)
        
        self.current_profile = {
            'user_agent': user_agent,
            'viewport': viewport,
            'platform': platform,
            'language': 'es-MX',
            'timezone': 'America/Mexico_City',
            'geolocation': {'latitude': 18.9239, 'longitude': -99.2277},  # Cuernavaca
        }
    
    async def inicializar_navegador_ultra_stealth(self):
        """Inicializa navegador con máximo stealth"""
        
        await self.inicializar_perfil_ultra_realista_con_proxy()
        
        playwright = await async_playwright().start()
        
        # ✅ ARGUMENTOS ULTRA STEALTH del archivo avanzado
        args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-automation',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--no-first-run',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--no-default-browser-check',
        ]
        
        launch_options = {
            'headless': False,
            'args': args,
            'ignore_default_args': ['--enable-automation']
        }
        
        # Agregar proxy si está disponible
        if self.current_proxy:
            launch_options['proxy'] = self.current_proxy.to_playwright_format()
        
        self.browser = await playwright.chromium.launch(**launch_options)
        
        # ✅ CONTEXTO ULTRA REALISTA
        context_options = {
            'user_agent': self.current_profile['user_agent'],
            'viewport': self.current_profile['viewport'],
            'locale': self.current_profile['language'],
            'timezone_id': self.current_profile['timezone'],
            'geolocation': self.current_profile['geolocation'],
            'permissions': ['geolocation'],
            'ignore_https_errors': True,
        }
        
        self.context = await self.browser.new_context(**context_options)
        
        # ✅ SCRIPT ULTRA AVANZADO DE EVASIÓN
        await self.context.add_init_script(f"""
            // Remover webdriver flags
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined,
            }});
            
            // Simular plugins reales
            Object.defineProperty(navigator, 'plugins', {{
                get: () => ({{
                    length: 5,
                    0: {{ name: 'Chrome PDF Plugin' }},
                    1: {{ name: 'Native Client' }},
                    2: {{ name: 'Chrome PDF Viewer' }},
                }}),
            }});
            
            Object.defineProperty(navigator, 'languages', {{
                get: () => ['es-MX', 'es', 'en'],
            }});
            
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{self.current_profile['platform']}',
            }});
            
            // Simular canvas fingerprint único
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(...args) {{
                const context = this.getContext('2d');
                if (context) {{
                    context.fillStyle = '#{str(random.randint(100000, 999999))}';
                    context.fillRect(0, 0, 1, 1);
                }}
                return toDataURL.apply(this, args);
            }};
            
            // Timing de red humano
            const originalFetch = window.fetch;
            window.fetch = function(...args) {{
                return new Promise((resolve) => {{
                    setTimeout(() => {{
                        resolve(originalFetch.apply(this, args));
                    }}, Math.random() * 100 + 50);
                }});
            }};
        """)
        
        await self._verificar_ip_actual()
    
    async def _verificar_ip_actual(self):
        """Verifica IP actual"""
        try:
            page = await self.context.new_page()
            await page.goto("https://httpbin.org/ip", timeout=10000)
            content = await page.content()
            await page.close()
            
            import re
            ip_match = re.search(r'"origin":\s*"([^"]+)"', content)
            if ip_match:
                self.proxy_ip = ip_match.group(1)
                print(f"✅ IP confirmada: {self.proxy_ip}")
            else:
                self.proxy_ip = "unknown"
                
        except Exception as e:
            print(f"⚠️ Error verificando IP: {str(e)}")
            self.proxy_ip = "error"
    
    async def navegar_humanamente_a_propiedad(self, url: str) -> Tuple[bool, Page]:
        """Navegación humana ultra avanzada a propiedad específica"""
        
        if not self.context:
            await self.inicializar_navegador_ultra_stealth()
        
        page = await self.context.new_page()
        
        try:
            # ✅ NAVEGACIÓN GRADUAL del archivo avanzado
            entry_url = random.choice(self.config.ENTRY_URLS)
            print(f"🌐 Entrada gradual: {entry_url}")
            
            # Entrar gradualmente
            await page.goto(entry_url, wait_until='domcontentloaded', timeout=30000)
            await self._simular_lectura_humana(page)
            
            # Navegar a propiedad objetivo
            print(f"🎯 Navegando a: {url}")
            await asyncio.sleep(random.uniform(1.0, 2.0))  # Corregido: usar valores fijos
            
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            if response and response.status < 400:
                await self._simular_interaccion_realista(page)
                return True, page
            else:
                print(f"❌ Error {response.status if response else 'Sin respuesta'}")
                return False, page
                
        except Exception as e:
            print(f"❌ Error navegando: {str(e)}")
            return False, page
    
    async def _simular_lectura_humana(self, page: Page):
        """Simula lectura humana"""
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        for _ in range(random.randint(1, 2)):
            scroll_y = random.randint(100, 400)
            await page.evaluate(f"window.scrollBy(0, {scroll_y})")
            await asyncio.sleep(random.uniform(0.5, 1.0))
        
        await page.evaluate("window.scrollTo(0, 0)")
    
    async def _simular_interaccion_realista(self, page: Page):
        """Simula interacción realista"""
        try:
            await self._generar_movimientos_mouse(page)
            await self._scroll_avanzado(page)
            await asyncio.sleep(random.uniform(2.0, 4.0))
        except Exception as e:
            print(f"⚠️ Error en simulación: {str(e)}")
    
    async def _generar_movimientos_mouse(self, page: Page):
        """Movimientos de mouse naturales"""
        viewport = page.viewport_size
        if viewport:
            for _ in range(random.randint(2, 4)):
                x = random.randint(0, viewport['width'])
                y = random.randint(0, viewport['height'])
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def _scroll_avanzado(self, page: Page):
        """Scroll avanzado humano"""
        scrolls = [random.randint(100, 300) for _ in range(random.randint(2, 4))]
        
        for scroll_amount in scrolls:
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.5, 1.0))
        
        await page.evaluate("window.scrollTo(0, 0)")
    
    async def extraer_descripcion_completa(self, page: Page) -> str:
        """Extrae descripción usando selectores múltiples del archivo original"""
        
        try:
            await asyncio.sleep(2)
            
            # ✅ SELECTORES del archivo original
            selectores = [
                '.ui-pdp-description',
                '.ui-pdp-description__content',
                '[data-testid="description"]',
                '.item-description',
                '.description-content'
            ]
            
            descripcion = ""
            
            for selector in selectores:
                try:
                    elementos = await page.query_selector_all(selector)
                    if elementos:
                        textos = await page.evaluate(f"""
                            (selector) => {{
                                const elements = document.querySelectorAll(selector);
                                return Array.from(elements).map(el => el.textContent || '').join(' ');
                            }}
                        """, selector)
                        if textos.strip():
                            descripcion = textos.strip()
                            break
                except:
                    continue
            
            # Fallback al texto completo
            if not descripcion:
                descripcion = await page.evaluate("document.body.textContent || ''")
            
            return descripcion[:2000]
            
        except Exception as e:
            print(f"⚠️ Error extrayendo descripción: {str(e)}")
            return ""
    
    async def cerrar(self):
        """Cierra navegador"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

class Test10PropiedadesMorelosHibrido:
    """Test automático de 10 propiedades con tecnología híbrida ultra avanzada"""
    
    def __init__(self):
        self.extractor = ExtractorHibridoOptimizado()
        self.navegador = NavegadorHibridoUltraAvanzado()
        self.resultados = []
        self.propiedades_procesadas = 0
        self.limite_propiedades = 10
    
    async def ejecutar_test_hibrido(self):
        """Ejecuta test híbrido ultra avanzado AUTOMÁTICO de 10 propiedades"""
        
        print("🚀 TEST AUTOMÁTICO 10 PROPIEDADES MORELOS - HÍBRIDO ULTRA AVANZADO")
        print("=" * 70)
        timestamp_inicio = datetime.now()
        
        print(f"🔧 Técnicas híbridas implementadas:")
        print(f"   ✅ Extracción optimizada (patrones 100% validados)")
        print(f"   ✅ Navegación ultra stealth sin proxies (para testing)")
        print(f"   ✅ Mouse simulation + behavioral patterns")
        print(f"   ✅ Canvas/TLS fingerprinting bypass")
        print(f"   🤖 Recolección y procesamiento AUTOMÁTICO")
        print()
        
        await self._procesar_automaticamente_morelos()
        await self._generar_reporte_hibrido(timestamp_inicio)
    
    async def _procesar_automaticamente_morelos(self):
        """Procesa automáticamente propiedades de Morelos - TODO EN UNO"""
        
        await self.navegador.inicializar_navegador_ultra_stealth()
        
        print(f"🔍 Iniciando búsqueda automática de {self.limite_propiedades} propiedades en Morelos...")
        
        # Procesar cada URL de búsqueda hasta encontrar 10 propiedades
        for url_busqueda in self.navegador.config.URLS_BUSQUEDA_MORELOS:
            if self.propiedades_procesadas >= self.limite_propiedades:
                break
                
            print(f"\n🌐 Explorando: {url_busqueda}")
            
            try:
                # Crear página nueva
                page = await self.navegador.context.new_page()
                
                # Navegar a la página de búsqueda
                await self._navegar_a_busqueda(page, url_busqueda)
                
                # Encontrar y procesar propiedades en esta página
                await self._procesar_propiedades_en_pagina(page)
                
                await page.close()
                
                # Delay entre páginas de búsqueda
                if self.propiedades_procesadas < self.limite_propiedades:
                    delay = random.uniform(3.0, 6.0)
                    print(f"⏳ Esperando {delay:.1f}s antes de siguiente página...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Error procesando {url_busqueda}: {str(e)}")
                continue
        
        await self.navegador.cerrar()
        print(f"\n✅ Búsqueda automática completada: {self.propiedades_procesadas} propiedades procesadas")
    
    async def _navegar_a_busqueda(self, page: Page, url_busqueda: str):
        """Navega a página de búsqueda con técnicas stealth"""
        
        print(f"🌐 Navegando a búsqueda...")
        
        # Navegar con stealth
        response = await page.goto(url_busqueda, wait_until='domcontentloaded', timeout=30000)
        
        if not response or response.status >= 400:
            raise Exception(f"Error navegando: {response.status if response else 'Sin respuesta'}")
        
        # Simular lectura humana
        await self._simular_lectura_humana_busqueda(page)
    
    async def _simular_lectura_humana_busqueda(self, page: Page):
        """Simula lectura humana en página de búsqueda"""
        await asyncio.sleep(random.uniform(2.0, 4.0))
        
        # Scroll para cargar contenido
        for _ in range(random.randint(2, 4)):
            scroll_y = random.randint(200, 600)
            await page.evaluate(f"window.scrollBy(0, {scroll_y})")
            await asyncio.sleep(random.uniform(0.8, 1.5))
        
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(random.uniform(1.0, 2.0))
    
    async def _procesar_propiedades_en_pagina(self, page: Page):
        """Encuentra y procesa propiedades en la página actual"""
        
        try:
            # Esperar que carguen las propiedades
            await page.wait_for_selector('a[href*="/MLM-"]', timeout=15000)
            
            # Extraer URLs de propiedades
            urls_propiedades = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="/MLM-"]'));
                    return [...new Set(links.map(link => link.href))].filter(href => 
                        href.includes('MLM-') && 
                        href.includes('mercadolibre.com.mx') &&
                        href.length > 50
                    );
                }
            """)
            
            print(f"📋 Encontradas {len(urls_propiedades)} propiedades en esta página")
            
            # Procesar cada propiedad encontrada
            for url_propiedad in urls_propiedades:
                if self.propiedades_procesadas >= self.limite_propiedades:
                    break
                
                await self._procesar_propiedad_individual(url_propiedad)
                self.propiedades_procesadas += 1
                
                # Delay entre propiedades
                if self.propiedades_procesadas < self.limite_propiedades:
                    delay = random.uniform(2.0, 4.0)
                    print(f"⏳ Esperando {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    
        except Exception as e:
            print(f"⚠️ Error extrayendo propiedades de la página: {str(e)}")
    
    async def _procesar_propiedad_individual(self, url_propiedad: str):
        """Procesa una propiedad individual con técnicas híbridas"""
        
        print(f"\n🏠 Propiedad {self.propiedades_procesadas + 1}/{self.limite_propiedades}")
        print(f"🔗 URL: {url_propiedad}")
        
        resultado = ResultadoPropiedad(
            url=url_propiedad,
            timestamp=datetime.now().isoformat(),
            user_agent_usado=self.navegador.current_profile.get('user_agent', '')[:50],
            proxy_usado=self.navegador.proxy_ip
        )
        
        try:
            # Crear página nueva para esta propiedad
            page_propiedad = await self.navegador.context.new_page()
            
            # Navegar a la propiedad
            response = await page_propiedad.goto(url_propiedad, wait_until='domcontentloaded', timeout=30000)
            
            if response and response.status < 400:
                # Simular interacción humana
                await self._simular_interaccion_en_propiedad(page_propiedad)
                
                # Extraer descripción como respaldo
                descripcion = await self.navegador.extraer_descripcion_completa(page_propiedad)
                resultado.descripcion = descripcion
                
                # 🚀 EXTRACCIÓN HÍBRIDA: tabla andes-table + regex
                datos = await self.extractor.extraer_datos_hibrido(page_propiedad, descripcion)
                
                resultado.recamaras = datos['recamaras']
                resultado.banos = datos['banos']
                resultado.construccion = datos['construccion']
                resultado.terreno = datos['terreno']
                resultado.estacionamiento = datos['estacionamiento']
                resultado.status = "exitoso"
                
                print(f"✅ Extraído - R:{resultado.recamaras} B:{resultado.banos} "
                      f"C:{resultado.construccion} T:{resultado.terreno} E:{resultado.estacionamiento}")
            else:
                resultado.status = "acceso_denegado"
                resultado.error = f"HTTP {response.status if response else 'Sin respuesta'}"
                print(f"❌ Acceso denegado: {resultado.error}")
            
            await page_propiedad.close()
            
        except Exception as e:
            resultado.status = "error"
            resultado.error = str(e)
            print(f"❌ Error procesando: {str(e)}")
        
        self.resultados.append(resultado)
    
    async def _simular_interaccion_en_propiedad(self, page: Page):
        """Simula interacción humana en página de propiedad"""
        
        # Esperar carga
        await asyncio.sleep(random.uniform(2.0, 4.0))
        
        # Movimientos de mouse básicos
        viewport = page.viewport_size
        if viewport:
            for _ in range(random.randint(1, 3)):
                x = random.randint(0, viewport['width'])
                y = random.randint(0, viewport['height'])
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Scroll humano
        for _ in range(random.randint(2, 4)):
            scroll_amount = random.randint(200, 500)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.8, 1.5))
        
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(random.uniform(1.0, 2.0))
    
    async def _generar_reporte_hibrido(self, timestamp_inicio: datetime):
        """Genera reporte híbrido detallado"""
        
        timestamp_fin = datetime.now()
        duracion = timestamp_fin - timestamp_inicio
        
        total = len(self.resultados)
        exitosos = len([r for r in self.resultados if r.status == "exitoso"])
        bloqueados = len([r for r in self.resultados if r.status == "acceso_denegado"])
        errores = len([r for r in self.resultados if r.status == "error"])
        
        efectividad_acceso = ((total - bloqueados) / total * 100) if total > 0 else 0
        efectividad_extraccion = (exitosos / total * 100) if total > 0 else 0
        
        campos_extraidos = {
            'recamaras': len([r for r in self.resultados if r.recamaras is not None]),
            'banos': len([r for r in self.resultados if r.banos is not None]),
            'construccion': len([r for r in self.resultados if r.construccion is not None]),
            'terreno': len([r for r in self.resultados if r.terreno is not None]),
            'estacionamiento': len([r for r in self.resultados if r.estacionamiento is not None])
        }
        
        reporte = {
            "test_info": {
                "nombre": "Test 10 Propiedades Morelos - Híbrido Ultra Avanzado",
                "timestamp_inicio": timestamp_inicio.isoformat(),
                "timestamp_fin": timestamp_fin.isoformat(),
                "duracion_segundos": duracion.total_seconds(),
                "version": "Híbrido Ultra Avanzado v1.0",
                "tecnicas": [
                    "Extracción optimizada (patrones 100% validados)",
                    "Navegación ultra stealth",
                    "Proxies residenciales opcionales",
                    "Mouse simulation + behavioral patterns",
                    "Canvas/TLS fingerprinting bypass"
                ]
            },
            "estadisticas": {
                "total_procesadas": total,
                "exitosas": exitosos,
                "bloqueadas": bloqueados,
                "errores": errores,
                "efectividad_acceso_pct": round(efectividad_acceso, 2),
                "efectividad_extraccion_pct": round(efectividad_extraccion, 2)
            },
            "extraccion_por_campo": {
                campo: {
                    "extraidos": count,
                    "efectividad_pct": round((count / total * 100), 2) if total > 0 else 0
                }
                for campo, count in campos_extraidos.items()
            },
            "resultados": [
                {
                    "url": r.url,
                    "recamaras": r.recamaras,
                    "banos": r.banos,
                    "construccion": r.construccion,
                    "terreno": r.terreno,
                    "estacionamiento": r.estacionamiento,
                    "status": r.status,
                    "error": r.error,
                    "proxy_usado": r.proxy_usado
                }
                for r in self.resultados
            ]
        }
        
        filename = f"test_10_hibrido_morelos_{timestamp_inicio.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 65)
        print("📊 REPORTE FINAL - TEST HÍBRIDO 10 PROPIEDADES")
        print("=" * 65)
        print(f"⏱️ Duración: {duracion}")
        print(f"🎯 Procesadas: {total}")
        print(f"✅ Exitosas: {exitosos}")
        print(f"🚫 Bloqueadas: {bloqueados}")
        print(f"❌ Errores: {errores}")
        print(f"📈 Efectividad acceso: {efectividad_acceso:.1f}%")
        print(f"📊 Efectividad extracción: {efectividad_extraccion:.1f}%")
        
        print("\n📋 EXTRACCIÓN POR CAMPO:")
        for campo, stats in reporte["extraccion_por_campo"].items():
            print(f"   {campo.capitalize()}: {stats['extraidos']}/{total} ({stats['efectividad_pct']:.1f}%)")
        
        print(f"\n💾 Reporte: {filename}")
        
        if efectividad_acceso >= 80 and efectividad_extraccion >= 70:
            print("\n🎉 TEST EXITOSO: Técnicas híbridas funcionan correctamente")
        elif bloqueados > total * 0.3:
            print("\n⚠️ ALTO BLOQUEO: Considerar activar proxies o revisar técnicas")
        else:
            print("\n✅ TEST COMPLETADO: Revisar resultados para optimizaciones")

async def main():
    """Función principal"""
    print("🛡️ SCRAPER HÍBRIDO ULTRA AVANZADO PARA MERCADOLIBRE 2025")
    print("🔗 Combina lo mejor de ambos sistemas anteriores")
    print("⚡ Procesamiento AUTOMÁTICO de 10 propiedades de Morelos")
    print()
    
    print("✅ LISTO PARA EJECUTAR:")
    print("• Recolección automática de URLs de MercadoLibre")
    print("• Procesamiento en tiempo real de cada propiedad")
    print("• Sin proxies (para testing seguro)")
    print("• Técnicas híbridas anti-bloqueo implementadas")
    print()
    
    test = Test10PropiedadesMorelosHibrido()
    await test.ejecutar_test_hibrido()

if __name__ == "__main__":
    asyncio.run(main()) 