#!/usr/bin/env python3
"""
EXTRACTORES DE DATOS - SCRAPER MERCADOLIBRE
==========================================

Lógica de extracción híbrida de datos de propiedades.
Solo funciones realmente usadas, modularizado para <500 líneas.
"""

import re
import asyncio
from datetime import datetime
from typing import Dict, Optional
from playwright.async_api import Page


class ExtractorHibridoOptimizado:
    """Extractor híbrido optimizado para MercadoLibre"""
    
    def __init__(self):
        """Inicializa extractor"""
        pass
    
    async def extraer_andes_table_completa_json(self, page, navigator=None) -> dict:
        """Extrae tablas andes como JSON estructurado con expansión automática"""
        
        print("🔄 Iniciando extracción completa de tablas andes...")
        
        andes_data = {
            "categorias": {},
            "metadata": {
                "total_categorias": 0,
                "total_campos": 0,
                "fecha_extraccion": datetime.now().isoformat()
            }
        }
        
        try:
            # 🎯 EXPANDIR CARACTERÍSTICAS usando NavigatorStealth si está disponible
            if navigator and hasattr(navigator, 'click_expand_characteristics_button'):
                expansion_success = await navigator.click_expand_characteristics_button(page)
                if expansion_success:
                    print("✅ Expansión de características exitosa")
                else:
                    print("⚠️ No se pudo expandir características, continuando...")
            else:
                # Fallback: método original de expansión
                print("🔍 Usando método de expansión fallback...")
                await self._expand_characteristics_fallback(page)
            
            await page.wait_for_timeout(1000)
            
            # 🎯 BUSCAR CONTENEDOR PRINCIPAL DE ESPECIFICACIONES TÉCNICAS
            main_container = await page.query_selector('.ui-pdp-container__row.ui-pdp-container__row--technical-specifications')
            
            if not main_container:
                print("⚠️ No se encontró contenedor principal de especificaciones técnicas")
                return andes_data
            
            print("✅ Contenedor principal encontrado")
            
            # 📦 EXTRAER CATEGORÍAS USANDO ESTRUCTURA CORRECTA
            category_tables = await main_container.query_selector_all('.ui-vpp-striped-specs__table')
            
            if not category_tables:
                print("⚠️ No se encontraron tablas de categorías (.ui-vpp-striped-specs__table)")
                return andes_data
            
            print(f"✅ Encontradas {len(category_tables)} categorías")
            
            total_categories = 0
            total_fields = 0
            
            for category_table in category_tables:
                try:
                    # 🏷️ EXTRAER TÍTULO DE CATEGORÍA
                    category_name = "categoria_sin_nombre"
                    
                    # Buscar título de categoría (puede estar en h3, h4, o elementos con clases específicas)
                    title_selectors = [
                        'h3', 'h4', 'h2',
                        '.ui-vpp-striped-specs__header',
                        '[class*="header"]',
                        '[class*="title"]'
                    ]
                    
                    for selector in title_selectors:
                        title_element = await category_table.query_selector(selector)
                        if title_element:
                            title_text = await title_element.text_content()
                            if title_text and len(title_text.strip()) > 0:
                                category_name = title_text.strip().lower().replace(' ', '_').replace('ñ', 'n').replace(':', '').replace('-', '_')
                                break
                    
                    # Si no encontró título, usar índice
                    if category_name == "categoria_sin_nombre":
                        category_name = f"categoria_{total_categories + 1}"
                    
                    print(f"   📋 Procesando categoría: '{category_name}'")
                    
                    # 📊 EXTRAER FILAS DE DATOS
                    category_data = {}
                    
                    # Buscar todas las filas de la tabla
                    rows = await category_table.query_selector_all('tr')
                    
                    for row in rows:
                        try:
                            # Buscar th y td según la estructura descrita
                            th_element = await row.query_selector('th')
                            td_element = await row.query_selector('td')
                            
                            if th_element and td_element:
                                # Extraer nombre del campo (th + div)
                                field_name_div = await th_element.query_selector('div')
                                if field_name_div:
                                    field_name = await field_name_div.text_content()
                                else:
                                    field_name = await th_element.text_content()
                                
                                # Extraer valor del campo (td + span)
                                field_value_span = await td_element.query_selector('span')
                                if field_value_span:
                                    field_value = await field_value_span.text_content()
                                else:
                                    field_value = await td_element.text_content()
                                
                                # Limpiar y validar
                                if field_name and field_value:
                                    field_name_clean = field_name.strip()
                                    field_value_clean = field_value.strip()
                                    
                                    if (field_name_clean and field_value_clean and 
                                        field_name_clean != field_value_clean and 
                                        len(field_name_clean) > 1):
                                        
                                        category_data[field_name_clean] = field_value_clean
                                        
                        except Exception as row_error:
                            # Si falla la estructura específica, intentar método genérico
                            try:
                                cells = await row.query_selector_all('th, td')
                                if len(cells) >= 2:
                                    key = await cells[0].text_content()
                                    value = await cells[1].text_content()
                                    
                                    if key and value:
                                        key_clean = key.strip()
                                        value_clean = value.strip()
                                        
                                        if (key_clean and value_clean and 
                                            key_clean != value_clean and 
                                            len(key_clean) > 1):
                                            category_data[key_clean] = value_clean
                            except:
                                continue
                    
                    # 💾 GUARDAR CATEGORÍA SI TIENE DATOS
                    if category_data:
                        andes_data["categorias"][category_name] = category_data
                        total_categories += 1
                        total_fields += len(category_data)
                        print(f"     ✅ {len(category_data)} campos extraídos")
                    else:
                        print(f"     ⚠️ No se encontraron datos en esta categoría")
                        
                except Exception as category_error:
                    print(f"     ❌ Error procesando categoría: {category_error}")
                    continue
            
            andes_data["metadata"]["total_categorias"] = total_categories
            andes_data["metadata"]["total_campos"] = total_fields
            
            print(f"✅ Extracción completa: {total_categories} categorías, {total_fields} campos")
            
            return andes_data
            
        except Exception as e:
            print(f"❌ Error en extracción: {e}")
            andes_data["error"] = str(e)
        
        return andes_data

    async def extraer_datos_desde_tabla_andes(self, page) -> dict:
        """Extrae datos estructurados desde tabla andes"""
        
        datos = {
            'recamaras': None,
            'banos': None,
            'construccion': None,
            'terreno': None,
            'estacionamiento': None,
            'precio': None,
            'moneda': None,
            'direccion': None,
            'tipo_propiedad': None,
            'tipo_operacion': None
        }
        
        try:
            andes_tables = await page.query_selector_all('.andes-table')
            
            if not andes_tables:
                return datos
            
            await self._extraer_precio_y_moneda(page, datos)
            await self._extraer_tipo_propiedad_y_operacion(page, datos)
            await self._extraer_direccion(page, datos)
            
            for table in andes_tables:
                rows = await table.query_selector_all('tr')
                
                for row in rows:
                    try:
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
                            elif 'superficie total' in key:
                                if datos['terreno'] is None:
                                    datos['terreno'] = self._parse_number(value)
                            elif 'estacionamiento' in key or 'garage' in key:
                                if datos['estacionamiento'] is None:
                                    datos['estacionamiento'] = self._parse_number(value)
                    except:
                        continue
            
            return datos
            
        except Exception as e:
            print(f"❌ Error extrayendo tabla andes: {e}")
            return datos

    async def extraer_datos_hibrido(self, page, descripcion_respaldo: str = None, navigator=None, incluir_andes_raw=True) -> dict:
        """
        Extracción híbrida completa con bypass integrado
        
        Args:
            page: Página de Playwright
            descripcion_respaldo: Descripción de respaldo (opcional)
            navigator: NavigatorStealth para expansión de características
            incluir_andes_raw: Si False, omite andes_table_raw para mayor velocidad
        """
        print("🚀 EXTRACCIÓN HÍBRIDA ULTRA AVANZADA 2025")
        print("=" * 60)
        
        inicio_tiempo = datetime.now()
        datos = {}
        
        try:
            # ✅ 1. METADATOS UNIVERSALES
            print("📋 Extrayendo metadatos universales...")
            await self._extraer_metadatos_universales(page, datos)
            
            # ✅ 2. CAMPOS ESTRUCTURADOS
            print("🔢 Extrayendo campos estructurados...")
            await self._extraer_precio_y_moneda(page, datos)
            await self._extraer_tipo_propiedad_y_operacion(page, datos) 
            await self._extraer_direccion(page, datos)
            
            # Extraer campos de tabla básica
            datos_tabla = await self.extraer_datos_desde_tabla_andes(page)
            datos.update(datos_tabla)
            
            # Parsear ubicación completa
            if datos.get('direccion'):
                ubicacion = await self._parsear_ubicacion_completa(datos['direccion'])
                datos.update(ubicacion)
            
            # ✅ 3. EXTRACCIÓN DE CATEGORÍAS DINÁMICAS 
            print("📦 Extrayendo categorías dinámicas...")
            
            # USAR SIEMPRE la función que funciona perfectamente
            andes_raw = await self.extraer_andes_table_completa_json(page, navigator)
            
            # Organizar JSON dinámico (SIEMPRE)
            categorias_json = await self._organizar_datos_json_por_categoria(andes_raw)
            
            # ✅ AGREGAR TODAS las categorías dinámicas que se encontraron (SIEMPRE)
            if categorias_json:
                for categoria_nombre, categoria_datos in categorias_json.items():
                    if categoria_datos and len(categoria_datos) > 0:
                        datos[categoria_nombre] = categoria_datos
                        print(f"   📦 Categoría añadida: '{categoria_nombre}' con {len(categoria_datos)} campos")
            
            # ✅ CONDICIONAL: Solo guardar andes_table_raw si se solicita
            if incluir_andes_raw:
                datos['andes_table_raw'] = andes_raw if andes_raw.get('categorias') else None
                print(f"   📋 andes_table_raw incluido para respaldo completo")
            else:
                print(f"   ⚡ andes_table_raw omitido para optimización de velocidad")
            
            # ✅ 4. TIEMPO Y ESTADÍSTICAS
            tiempo_total = (datetime.now() - inicio_tiempo).total_seconds()
            datos['tiempo_total'] = tiempo_total
            
            modo = "completo" if incluir_andes_raw else "optimizado"
            total_campos = len([k for k, v in datos.items() if v is not None and v != ""])
            
            print(f"⚡ Extracción híbrida {modo} completada en {tiempo_total:.1f}s")
            print(f"📊 Campos extraídos: {total_campos}")
            
            return datos
            
        except Exception as e:
            print(f"❌ Error en extracción híbrida: {e}")
            tiempo_total = (datetime.now() - inicio_tiempo).total_seconds()
            return {
                'error': str(e),
                'tiempo_total': tiempo_total,
                'status': 'error'
            }

    def _parse_number(self, value: str) -> Optional[int]:
        """Parsea número entero"""
        if not value:
            return None
        try:
            clean_value = re.sub(r'[^\d,.]', '', value)
            if clean_value:
                if ',' in clean_value and '.' not in clean_value:
                    clean_value = clean_value.replace(',', '.')
                elif ',' in clean_value and '.' in clean_value:
                    clean_value = clean_value.replace(',', '')
                return int(float(clean_value))
        except:
            pass
        return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Parsea número flotante"""
        if not value:
            return None
        try:
            clean_value = re.sub(r'[^\d,.]', '', value)
            if clean_value:
                if ',' in clean_value and '.' not in clean_value:
                    clean_value = clean_value.replace(',', '.')
                elif ',' in clean_value and '.' in clean_value:
                    clean_value = clean_value.replace(',', '')
                return float(clean_value)
        except:
            pass
        return None

    async def _extraer_precio_y_moneda(self, page, datos):
        """Extrae precio y moneda"""
        try:
            price_selectors = ['.price-tag-fraction', '.andes-money-amount__fraction', '.ui-pdp-price__fraction']
            
            for selector in price_selectors:
                try:
                    price_element = await page.query_selector(selector)
                    if price_element:
                        price_text = await price_element.text_content()
                        if price_text and price_text.strip():
                            precio_limpio = price_text.strip().replace(',', '').replace('.', '').replace('$', '')
                            if precio_limpio.isdigit():
                                datos['precio'] = float(precio_limpio)
                                break
                except:
                    continue
            
            if datos['precio'] and not datos['moneda']:
                datos['moneda'] = 'MXN'
                
        except Exception as e:
            print(f"⚠️ Error extrayendo precio: {e}")

    async def _extraer_tipo_propiedad_y_operacion(self, page, datos):
        """Extrae tipo de propiedad y operación"""
        try:
            title_element = await page.query_selector('h1')
            if title_element:
                title_text = await title_element.text_content()
                if title_text:
                    title_lower = title_text.lower()
                    
                    if 'casa' in title_lower:
                        datos['tipo_propiedad'] = 'casa'
                    elif 'departamento' in title_lower:
                        datos['tipo_propiedad'] = 'departamento'
                    elif 'terreno' in title_lower:
                        datos['tipo_propiedad'] = 'terreno'
                    
                    if 'venta' in title_lower:
                        datos['tipo_operacion'] = 'venta'
                    elif 'renta' in title_lower:
                        datos['tipo_operacion'] = 'renta'
            
            if not datos['tipo_propiedad']:
                datos['tipo_propiedad'] = 'casa'
            if not datos['tipo_operacion']:
                datos['tipo_operacion'] = 'venta'
                
        except Exception as e:
            print(f"⚠️ Error extrayendo tipo: {e}")
    
    async def _extraer_direccion(self, page, datos):
        """Extrae dirección usando múltiples estrategias mejoradas"""
        try:
            print("🔍 Iniciando extracción mejorada de dirección...")
            
            # ===== ESTRATEGIA 1: Selector original =====
            try:
                print("   📍 Estrategia 1: Selector específico original...")
                address_elements = await page.query_selector_all('p.ui-pdp-color--BLACK.ui-pdp-size--SMALL.ui-pdp-family--REGULAR.ui-pdp-media__title')
                
                for address_element in address_elements:
                    address_text = await address_element.text_content()
                    if address_text and self._es_probable_direccion(address_text.strip()):
                        datos['direccion'] = address_text.strip()
                        print(f"  📍 Dirección encontrada (E1): {datos['direccion']}")
                        return
                        
            except Exception as e:
                print(f"     ⚠️ Error en estrategia 1: {e}")

            # ===== ESTRATEGIA 2: Selectores más generales =====
            try:
                print("   📍 Estrategia 2: Selectores generales...")
                
                selectors = [
                    'p[class*="ui-pdp"]',
                    'span[class*="ui-pdp"]',
                    '.ui-pdp-container p',
                    '.ui-pdp-media__title',
                    'p.ui-pdp-color--BLACK'
                ]
                
                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    
                    for element in elements:
                        text = await element.text_content()
                        if text and self._es_probable_direccion(text.strip()):
                            datos['direccion'] = text.strip()
                            print(f"  📍 Dirección encontrada (E2): {datos['direccion']}")
                            return
                            
            except Exception as e:
                print(f"     ⚠️ Error en estrategia 2: {e}")

            # ===== ESTRATEGIA 3: Buscar en todo el texto visible =====
            try:
                print("   📍 Estrategia 3: Búsqueda en texto completo...")
                
                page_text = await page.evaluate("() => document.body.innerText")
                
                if page_text:
                    lines = page_text.split('\n')
                    
                    for line in lines:
                        line_clean = line.strip()
                        if self._es_probable_direccion(line_clean):
                            datos['direccion'] = line_clean
                            print(f"  📍 Dirección encontrada (E3): {datos['direccion']}")
                            return
                        
            except Exception as e:
                print(f"     ⚠️ Error en estrategia 3: {e}")

            print("  ❌ No se pudo extraer dirección con ninguna estrategia")
                        
        except Exception as e:
            print(f"⚠️ Error extrayendo dirección: {e}")

    def _es_probable_direccion(self, text: str) -> bool:
        """Determina si un texto es probablemente una dirección"""
        if not text or len(text.strip()) < 15:
            return False
            
        text_lower = text.lower().strip()
        
        # ❌ FILTROS ESTRICTOS - No debe contener:
        filtros_prohibidos = [
            'mercado libre', 'mercadolibre', 'ml', 'mlm-', 'contraseña', 'pin', 
            'whatsapp', 'email', 'características', 'publicación', 'precio', 'venta', 
            'compra', 'casa', 'inmueble', 'metros cuadrados', 'm²', 'm2', 'recámara', 
            'baño', 'estacionamiento', 'terreno', 'construcción', 'superficie', 'pisos'
        ]
        
        if any(filtro in text_lower for filtro in filtros_prohibidos):
            return False
        
        # ❌ No aceptar textos que son principalmente números
        if len([c for c in text if c.isdigit()]) > len(text) * 0.5:
            return False
            
        # ❌ No aceptar textos muy cortos sin estructura
        if len(text.split()) < 3:
            return False
        
        # ✅ INDICADORES POSITIVOS de vías
        indicadores_via = [
            'colonia', 'col.', 'calle', 'c.', 'avenida', 'av.', 'privada', 'priv.',
            'boulevard', 'blvd', 'fraccionamiento', 'fracc', 'calzada', 'calz.',
            'andador', 'circuito', 'paseo', 'plaza', 'glorieta'
        ]
        
        # ✅ INDICADORES DE UBICACIÓN
        indicadores_ubicacion = [
            'cuernavaca', 'morelos', 'cdmx', 'ciudad de méxico', 'méxico', 'estado de méxico',
            'nezahualcóyotl', 'nezahualcoyotl', 'tecámac', 'tecamac', 'atizapán', 'atizapan',
            'coyoacán', 'coyoacan', 'zapopan', 'guadalajara', 'mérida', 'merida', 'yucatán',
            'metropolitana', 'villa del real', 'mayorazgos', 'distrito federal', 'alvaro obregón'
        ]
        
        # Debe tener AL MENOS un indicador de vía O ubicación
        tiene_indicador_via = any(indicador in text_lower for indicador in indicadores_via)
        tiene_ubicacion = any(ubicacion in text_lower for ubicacion in indicadores_ubicacion)
        
        # ✅ ESTRUCTURA de dirección (flexible)
        tiene_estructura = (
            (',' in text and len(text.split(',')) >= 2) or  # Separadores de dirección
            any(char.isdigit() for char in text) or  # Algún número
            'minutos' in text_lower  # Referencias de distancia
        )
        
        # ✅ DECISIÓN FINAL: Debe cumplir criterios básicos
        es_direccion = (tiene_indicador_via or tiene_ubicacion) and tiene_estructura
        
        return es_direccion

    async def _extraer_metadatos_universales(self, page, datos):
        """Extrae metadatos universales"""
        try:
            # ML ID
            current_url = page.url
            ml_id_match = re.search(r'(MLM-[\d]+)', current_url)
            if ml_id_match:
                datos['ml_id'] = ml_id_match.group(1)
            
            # Título
            title_element = await page.query_selector('h1')
            if title_element:
                title_text = await title_element.inner_text()
                if title_text and len(title_text.strip()) > 5:
                    datos['titulo'] = title_text.strip()
            
            # Descripción
            desc_element = await page.query_selector('[data-testid="content"]')
            if desc_element:
                desc_text = await desc_element.inner_text()
                if desc_text and len(desc_text.strip()) > 20:
                    datos['descripcion'] = desc_text.strip()
            
            datos['url'] = current_url
            
        except Exception as e:
            print(f"❌ Error extrayendo metadatos: {e}")

    async def _parsear_ubicacion_completa(self, direccion_raw: str) -> dict:
        """Parsea dirección en componentes - ENFOQUE SIMPLE por últimos elementos"""
        ubicacion = {
            'pais': 'México',
            'estado': None,
            'ciudad': None
        }
        
        if not direccion_raw:
            return ubicacion
            
        try:
            print(f"   🔍 Parseando ubicación: '{direccion_raw}'")
            
            # ✅ LIMPIEZA PREVIA del string
            direccion_limpia = direccion_raw.strip()
            
            # Remover caracteres extraños y normalizar
            direccion_limpia = direccion_limpia.replace('  ', ' ')  # Espacios dobles
            direccion_limpia = direccion_limpia.replace(' ,', ',')  # Espacios antes de comas
            direccion_limpia = direccion_limpia.replace(', ', ',')  # Normalizar separadores
            
            # ✅ SEPARAR POR COMAS
            partes = [parte.strip() for parte in direccion_limpia.split(',') if parte.strip()]
            
            if len(partes) >= 2:
                # ✅ ENFOQUE SIMPLE: Últimos dos elementos
                estado_raw = partes[-1].strip()  # Último elemento = estado
                ciudad_raw = partes[-2].strip()  # Penúltimo elemento = ciudad
                
                # ✅ MAPEO SIMPLE DE ESTADOS (solo normalización)
                estado_normalizado = self._normalizar_estado(estado_raw)
                
                # ✅ ASIGNAR RESULTADOS
                ubicacion['estado'] = estado_normalizado
                ubicacion['ciudad'] = ciudad_raw.title()  # Capitalizar primera letra
                
                print(f"     ✅ Estado: {ubicacion['estado']}")
                print(f"     ✅ Ciudad: {ubicacion['ciudad']}")
                
            elif len(partes) == 1:
                # Solo un elemento - probablemente sea estado
                estado_raw = partes[0].strip()
                estado_normalizado = self._normalizar_estado(estado_raw)
                ubicacion['estado'] = estado_normalizado
                print(f"     ✅ Solo estado: {ubicacion['estado']}")
            else:
                print(f"     ⚠️ No se pudieron extraer elementos válidos")
                    
        except Exception as e:
            print(f"❌ Error parseando ubicación: {e}")
            
        return ubicacion

    def _normalizar_estado(self, estado_raw: str) -> str:
        """Normaliza nombre de estado con mapeo simple"""
        estado_lower = estado_raw.lower().strip()
        
        # ✅ MAPEO SIMPLE solo para casos comunes
        normalizaciones = {
            'distrito federal': 'Ciudad de México',
            'df': 'Ciudad de México',
            'cdmx': 'Ciudad de México',
            'ciudad de méxico': 'Ciudad de México',
            'estado de méxico': 'Estado de México',
            'mexico': 'Estado de México',
            'edomex': 'Estado de México',
            'morelos': 'Morelos',
            'estado de morelos': 'Morelos',
            'yucatan': 'Yucatán',
            'yucatán': 'Yucatán',
            'queretaro': 'Querétaro',
            'querétaro': 'Querétaro',
            'jalisco': 'Jalisco',
            'sinaloa': 'Sinaloa'
        }
        
        return normalizaciones.get(estado_lower, estado_raw.title())

    async def _organizar_datos_json_por_categoria(self, andes_raw: dict) -> dict:
        """Organiza datos JSON de forma COMPLETAMENTE DINÁMICA basado en lo que realmente encuentre"""
        categorias_dinamicas = {}
        
        try:
            if not andes_raw or 'categorias' not in andes_raw:
                print("⚠️ No hay datos andes_raw para organizar")
                return categorias_dinamicas
            
            print(f"📦 Organizando {len(andes_raw['categorias'])} categorías encontradas...")
            
            # ✅ MÉTODO DINÁMICO: Usar exactamente las categorías que encuentre
            for categoria_nombre, categoria_data in andes_raw['categorias'].items():
                if isinstance(categoria_data, dict) and len(categoria_data) > 0:
                    
                    # Normalizar nombre de categoría para JSON
                    categoria_limpia = categoria_nombre.lower().strip()
                    categoria_limpia = categoria_limpia.replace(' ', '_').replace('ñ', 'n').replace(':', '').replace('-', '_')
                    
                    # Asegurar que no esté vacía
                    if not categoria_limpia or categoria_limpia in ['categoria_1', 'categoria_2']:
                        categoria_limpia = f"categoria_{len(categorias_dinamicas) + 1}"
                    
                    # Guardar EXACTAMENTE lo que encuentre
                    categorias_dinamicas[categoria_limpia] = categoria_data.copy()
                    
                    print(f"   ✅ Categoría '{categoria_limpia}': {len(categoria_data)} campos")
                    
                    # Mostrar algunos ejemplos de campos
                    ejemplos = list(categoria_data.keys())[:3]
                    print(f"      📋 Ejemplos: {ejemplos}")
            
            print(f"✅ Total categorías dinámicas creadas: {len(categorias_dinamicas)}")
            
            return categorias_dinamicas
            
        except Exception as e:
            print(f"❌ Error organizando categorías dinámicas: {e}")
            return categorias_dinamicas

    async def _expand_characteristics_fallback(self, page) -> bool:
        """Método fallback para expandir características cuando no hay NavigatorStealth"""
        try:
            print("🔍 Método fallback: Detectando tipo de interfaz...")
            
            # Verificar si muestra "Características del producto" vs "Características del inmueble"
            product_interface = await page.query_selector('text="Características del producto"')
            inmueble_interface = await page.query_selector('text="Características del inmueble"')
            
            if product_interface:
                print("✅ Interfaz de PRODUCTO detectada - Tablas ya expandidas")
                return True
            elif inmueble_interface:
                print("🔑 Interfaz de INMUEBLE detectada - Buscando botón de expansión...")
                
                # Buscar botón de expansión
                expand_button = await page.query_selector('button:has-text("Ver todas las características")')
                
                if not expand_button:
                    expand_buttons = await page.query_selector_all('.ui-pdp-collapsable__action.ui-vpp-highlighted-specs__striped-collapsed__action')
                    if expand_buttons:
                        for button in expand_buttons:
                            button_text = await button.text_content()
                            if button_text and 'características' in button_text.lower():
                                expand_button = button
                                break
                
                if expand_button:
                    try:
                        is_visible = await expand_button.is_visible()
                        button_text = await expand_button.text_content() or "Sin texto"
                        
                        if is_visible:
                            print(f"🖱️ Fallback: Haciendo click en: '{button_text}'")
                            await expand_button.click()
                            await page.wait_for_timeout(3000)
                            print("✅ Fallback: Tablas expandidas correctamente")
                            return True
                    except Exception as e:
                        print(f"⚠️ Fallback: Error haciendo click: {e}")
                        return False
                else:
                    print("⚠️ Fallback: No se encontró botón de expansión en interfaz inmueble")
                    return False
            else:
                print("🔍 Fallback: Interfaz no identificada, procediendo directamente...")
                return True
                
        except Exception as e:
            print(f"❌ Error en método fallback: {e}")
            return False

    async def _extraer_categorias_estructuradas(self, page) -> dict:
        """Extrae categorías estructuradas sin el andes_table_raw completo"""
        categorias = {}
        
        try:
            # Buscar tablas de categorías
            tablas = await page.query_selector_all('.ui-vpp-striped-specs__table')
            
            if not tablas:
                print("   ⚠️ No se encontraron tablas de categorías")
                return categorias
            
            print(f"   🔍 Procesando {len(tablas)} tablas encontradas...")
            
            for i, tabla in enumerate(tablas):
                categoria_nombre = f"categoria_{i+1}"
                categoria_datos = {}
                
                try:
                    # Buscar título de categoría
                    titulo_element = await tabla.query_selector('h3, h4')
                    if titulo_element:
                        titulo_text = await titulo_element.text_content()
                        if titulo_text and titulo_text.strip():
                            categoria_nombre = titulo_text.strip().lower()
                    
                    # Extraer filas de datos
                    filas = await tabla.query_selector_all('tr')
                    
                    for fila in filas:
                        # Extraer campo (th > div)
                        campo_element = await fila.query_selector('th div')
                        if campo_element:
                            campo_text = await campo_element.text_content()
                            
                            # Extraer valor (td > span)
                            valor_element = await fila.query_selector('td span')
                            if valor_element:
                                valor_text = await valor_element.text_content()
                                
                                if campo_text and valor_text:
                                    campo_limpio = campo_text.strip()
                                    valor_limpio = valor_text.strip()
                                    
                                    if campo_limpio and valor_limpio:
                                        categoria_datos[campo_limpio] = valor_limpio
                    
                    if categoria_datos:
                        categorias[categoria_nombre] = categoria_datos
                        print(f"   ✅ Categoría '{categoria_nombre}': {len(categoria_datos)} campos")
                    
                except Exception as e:
                    print(f"   ⚠️ Error procesando tabla {i}: {e}")
                    continue
            
            return categorias
            
        except Exception as e:
            print(f"❌ Error extrayendo categorías estructuradas: {e}")
            return categorias

    async def _organizar_categorias_json_optimizado(self, categorias_raw: dict) -> dict:
        """Organiza categorías en formato JSON optimizado"""
        categorias_finales = {}
        
        try:
            # Mapeo de nombres de categorías conocidas
            mapeo_categorias = {
                'principales': ['principales', 'caracteristicas principales', 'caracteristicas_principales'],
                'servicios': ['servicios', 'servicio'],
                'ambientes': ['ambientes', 'ambiente'],
                'seguridad': ['seguridad', 'proteccion'],
                'comodidades_y_equipamiento': ['comodidades', 'equipamiento', 'comodidades y equipamiento']
            }
            
            # Procesar cada categoría encontrada
            for categoria_original, datos in categorias_raw.items():
                if not isinstance(datos, dict) or not datos:
                    continue
                
                categoria_normalizada = categoria_original.lower().strip()
                categoria_final = None
                
                # Buscar mapeo conocido
                for categoria_estandar, variantes in mapeo_categorias.items():
                    for variante in variantes:
                        if variante in categoria_normalizada:
                            categoria_final = categoria_estandar
                            break
                    if categoria_final:
                        break
                
                # Si no encuentra mapeo, usar nombre normalizado
                if not categoria_final:
                    categoria_final = categoria_normalizada.replace(' ', '_').replace('ñ', 'n')
                
                # Evitar duplicados combinando datos
                if categoria_final in categorias_finales:
                    categorias_finales[categoria_final].update(datos)
                else:
                    categorias_finales[categoria_final] = datos.copy()
            
            print(f"   📦 Categorías organizadas: {len(categorias_finales)}")
            return categorias_finales
            
        except Exception as e:
            print(f"❌ Error organizando categorías: {e}")
            return False 