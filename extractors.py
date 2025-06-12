#!/usr/bin/env python3
"""
EXTRACTORES DE DATOS - SCRAPER MERCADOLIBRE
==========================================

Lógica de extracción híbrida de datos de propiedades.
Refactorizado con funciones utilitarias modulares.
"""

import re
import asyncio
from datetime import datetime
from typing import Dict, Optional
from playwright.async_api import Page

# Importar funciones utilitarias refactorizadas
from utils import parse_numeric
from direccion_utils import es_probable_direccion, parsear_ubicacion_completa


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
            
            # ✅ 2. CAMPOS ESTRUCTURADOS BÁSICOS
            print("🔢 Extrayendo campos estructurados...")
            await self._extraer_precio_y_moneda(page, datos)
            await self._extraer_tipo_propiedad_y_operacion(page, datos)
            await self._extraer_vendedor(page, datos)
            await self._extraer_direccion(page, datos)
            
            # Parsear ubicación completa
            if datos.get('direccion'):
                ubicacion = parsear_ubicacion_completa(datos['direccion'])
                datos.update(ubicacion)
            
            # ✅ 3. EXTRACCIÓN DE CATEGORÍAS DINÁMICAS 
            print("📦 Extrayendo categorías dinámicas...")
            
            if incluir_andes_raw:
                # Modo completo: extraer todo el raw data (más lento)
                print("   🔄 Modo completo: extrayendo andes_table_raw completo...")
                andes_raw = await self.extraer_andes_table_completa_json(page, navigator)
                categorias_json = await self._organizar_categorias_json_optimizado(andes_raw.get('categorias', {}))
                datos['andes_table_raw'] = andes_raw if andes_raw.get('categorias') else None
                print(f"   📋 andes_table_raw incluido para respaldo completo")
            else:
                # Modo optimizado: solo categorías estructuradas (más rápido)
                print("   ⚡ Modo optimizado: extrayendo solo categorías necesarias...")
                categorias_raw = await self._extraer_categorias_optimizado(page, navigator)
                categorias_json = await self._organizar_categorias_json_optimizado(categorias_raw)
                print(f"   ⚡ andes_table_raw omitido para optimización de velocidad")
            
            # ✅ AGREGAR TODAS las categorías dinámicas que se encontraron
            if categorias_json:
                for categoria_nombre, categoria_datos in categorias_json.items():
                    if categoria_datos and len(categoria_datos) > 0:
                        datos[categoria_nombre] = categoria_datos
                        print(f"   📦 Categoría añadida: '{categoria_nombre}' con {len(categoria_datos)} campos")
            
            # ✅ 4. EXTRAER CAMPOS BÁSICOS ESTRUCTURADOS desde categorías principales
            # IMPORTANTE: Los agregamos justo después de las categorías para mejor organización
            print("🔢 Extrayendo campos básicos desde categorías...")
            await self._extraer_campos_basicos_desde_categorias(datos)
            
            # ✅ 5. REORGANIZAR DATOS: Mover campos básicos al inicio para mejor legibilidad
            datos_reorganizados = {}
            
            # Primero: Metadatos universales
            campos_metadatos = ['ml_id', 'titulo', 'descripcion', 'direccion', 'pais', 'estado', 'ciudad']
            for campo in campos_metadatos:
                if campo in datos:
                    datos_reorganizados[campo] = datos[campo]
            
            # Segundo: Campos estructurados básicos
            campos_estructurados = ['precio', 'tipo_propiedad', 'tipo_operacion', 'vendedor', 'recamaras', 'banos', 'construccion', 'terreno', 'estacionamiento', 'moneda']
            for campo in campos_estructurados:
                if campo in datos:
                    datos_reorganizados[campo] = datos[campo]
            
            # Tercero: Categorías dinámicas (principales, servicios, ambientes, etc.)
            for key, value in datos.items():
                if key not in campos_metadatos and key not in campos_estructurados and key not in ['tiempo_total', 'andes_table_raw']:
                    datos_reorganizados[key] = value
            
            # Cuarto: andes_table_raw (si existe)
            if 'andes_table_raw' in datos:
                datos_reorganizados['andes_table_raw'] = datos['andes_table_raw']
            
            # Finalmente: metadatos del sistema
            if 'tiempo_total' in datos:
                datos_reorganizados['tiempo_total'] = datos['tiempo_total']
            
            # ✅ 6. TIEMPO Y ESTADÍSTICAS
            tiempo_total = (datetime.now() - inicio_tiempo).total_seconds()
            datos_reorganizados['tiempo_total'] = tiempo_total
            
            modo = "completo" if incluir_andes_raw else "optimizado"
            total_campos = len([k for k, v in datos_reorganizados.items() if v is not None and v != ""])
            
            print(f"⚡ Extracción híbrida {modo} completada en {tiempo_total:.1f}s")
            print(f"📊 Campos extraídos: {total_campos}")
            
            return datos_reorganizados
            
        except Exception as e:
            print(f"❌ Error en extracción híbrida: {e}")
            tiempo_total = (datetime.now() - inicio_tiempo).total_seconds()
            return {
                'error': str(e),
                'tiempo_total': tiempo_total,
                'status': 'error'
            }

    # Funciones numéricas movidas a utils.py

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
        """
        Extrae tipo de propiedad y operación desde el div ui-pdp-header__subtitle
        Estructura: <div class="ui-pdp-header__subtitle"><span class="ui-pdp-subtitle">Casa en Venta</span></div>
        """
        # ✅ INICIALIZAR CAMPOS PRIMERO (fix del bug identificado)
        datos['tipo_propiedad'] = None
        datos['tipo_operacion'] = None
        
        try:
            print("🏷️ Extrayendo tipo de propiedad y operación desde subtitle...")
            
            # ===== ESTRATEGIA 1: Selector específico del subtitle =====
            subtitle_selectors = [
                '.ui-pdp-subtitle',                              # 1. Simple y directo
                '.ui-pdp-header__subtitle .ui-pdp-subtitle',     # 2. Específico por contexto  
                '.ui-pdp-header__subtitle span',                 # 3. Por tipo de elemento
                'span.ui-pdp-subtitle'                           # 4. Por elemento + clase
            ]
            
            subtitle_text = None
            
            for selector in subtitle_selectors:
                try:
                    subtitle_element = await page.query_selector(selector)
                    if subtitle_element:
                        subtitle_text = await subtitle_element.text_content()
                        if subtitle_text and len(subtitle_text.strip()) > 3:
                            subtitle_text = subtitle_text.strip()
                            print(f"  🎯 Subtitle encontrado con '{selector}': '{subtitle_text}'")
                            break
                except Exception as e:
                    print(f"     ⚠️ Error con selector {selector}: {e}")
                    continue
            
            # ===== PARSEAR TIPO DE PROPIEDAD Y OPERACIÓN =====
            if subtitle_text:
                subtitle_lower = subtitle_text.lower()
                
                # Normalizar tipo de propiedad
                if any(word in subtitle_lower for word in ['casa', 'casas']):
                    datos['tipo_propiedad'] = 'casa'
                elif any(word in subtitle_lower for word in ['departamento', 'departamentos', 'depto', 'dpto']):
                    datos['tipo_propiedad'] = 'departamento'
                elif any(word in subtitle_lower for word in ['terreno', 'terrenos', 'lote', 'lotes']):
                    datos['tipo_propiedad'] = 'terreno'
                elif any(word in subtitle_lower for word in ['local', 'oficina', 'bodega']):
                    datos['tipo_propiedad'] = 'comercial'
                
                # Normalizar tipo de operación
                if any(word in subtitle_lower for word in ['venta', 'ventas', 'remate']):
                    datos['tipo_operacion'] = 'venta'
                elif any(word in subtitle_lower for word in ['renta', 'rentas', 'alquiler', 'alquila']):
                    datos['tipo_operacion'] = 'renta'
                elif any(word in subtitle_lower for word in ['traspaso', 'cesion']):
                    datos['tipo_operacion'] = 'traspaso'
                
                print(f"  ✅ Extraído desde subtitle: tipo_propiedad='{datos['tipo_propiedad']}', tipo_operacion='{datos['tipo_operacion']}'")
            
            # ===== ESTRATEGIA FALLBACK: Buscar en título si subtitle falló =====
            if not datos['tipo_propiedad'] or not datos['tipo_operacion']:
                print("  🔄 Aplicando estrategia fallback desde título...")
                
                try:
                    title_element = await page.query_selector('h1')
                    if title_element:
                        title_text = await title_element.text_content()
                        if title_text:
                            title_lower = title_text.lower()
                            
                            # Solo completar campos faltantes
                            if not datos['tipo_propiedad']:
                                if any(word in title_lower for word in ['casa', 'casas']):
                                    datos['tipo_propiedad'] = 'casa'
                                elif any(word in title_lower for word in ['departamento', 'departamentos', 'depto']):
                                    datos['tipo_propiedad'] = 'departamento'
                                elif any(word in title_lower for word in ['terreno', 'terrenos']):
                                    datos['tipo_propiedad'] = 'terreno'
                            
                            if not datos['tipo_operacion']:
                                if any(word in title_lower for word in ['venta', 'ventas', 'remate']):
                                    datos['tipo_operacion'] = 'venta'
                                elif any(word in title_lower for word in ['renta', 'rentas', 'alquiler']):
                                    datos['tipo_operacion'] = 'renta'
                            
                            print(f"  🔄 Fallback desde título: tipo_propiedad='{datos['tipo_propiedad']}', tipo_operacion='{datos['tipo_operacion']}'")
                            
                except Exception as e:
                    print(f"     ⚠️ Error en fallback desde título: {e}")
            
            # ===== VALORES POR DEFECTO FINALES =====
            if not datos['tipo_propiedad']:
                datos['tipo_propiedad'] = 'N/A'  # Default más común
                print("  🔧 Aplicando default: tipo_propiedad='casa'")
            
            if not datos['tipo_operacion']:
                datos['tipo_operacion'] = 'N/A'  # Default más común
                print("  🔧 Aplicando default: tipo_operacion='venta'")
            
            print(f"🏷️ ✅ Tipos finales: '{datos['tipo_propiedad']}' en '{datos['tipo_operacion']}'")
            
        except Exception as e:
            print(f"❌ Error extrayendo tipos de propiedad y operación: {e}")
            # FALLBACKS DE EMERGENCIA garantizados
            datos['tipo_propiedad'] = datos.get('tipo_propiedad') or 'casa'
            datos['tipo_operacion'] = datos.get('tipo_operacion') or 'venta'
            print(f"🆘 Fallbacks de emergencia aplicados: '{datos['tipo_propiedad']}' en '{datos['tipo_operacion']}'")

    async def _extraer_vendedor(self, page, datos):
        """
        Extrae información del vendedor desde el div ui-vip-profile-info__info-container
        Estructura: <div class="ui-vip-profile-info__info-container">
                       <div class="ui-vip-profile-info__info-link">
                           <h3 class="ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--REGULAR">Savbienesraices</h3>
                       </div>
                    </div>
        """
        # ✅ INICIALIZAR CAMPO PRIMERO
        datos['vendedor'] = None
        
        try:
            print("👤 Extrayendo información del vendedor...")
            
            # ===== ESTRATEGIA 1: Selectores CSS cascada para el vendedor =====
            vendedor_selectors = [
                '.ui-vip-profile-info__info-container .ui-vip-profile-info__info-link h3',  # 1. Selector completo específico
                '.ui-vip-profile-info__info-container h3',                                  # 2. Selector directo al h3
                '.ui-vip-profile-info__info-link h3',                                       # 3. Desde el link directo
                'h3.ui-pdp-color--BLACK.ui-pdp-size--XSMALL.ui-pdp-family--REGULAR'        # 4. Por clases específicas del h3
            ]
            
            vendedor_text = None
            
            for selector in vendedor_selectors:
                try:
                    vendedor_element = await page.query_selector(selector)
                    if vendedor_element:
                        vendedor_text = await vendedor_element.text_content()
                        if vendedor_text and len(vendedor_text.strip()) > 1:
                            vendedor_text = vendedor_text.strip()
                            print(f"  🎯 Vendedor encontrado con '{selector}': '{vendedor_text}'")
                            break
                except Exception as e:
                    print(f"     ⚠️ Error con selector {selector}: {e}")
                    continue
            
            # ===== ASIGNAR RESULTADO =====
            if vendedor_text:
                datos['vendedor'] = vendedor_text
                print(f"  ✅ Vendedor extraído: '{datos['vendedor']}'")
            else:
                print("  ⚠️ No se pudo extraer información del vendedor")
                datos['vendedor'] = "No disponible"
                
        except Exception as e:
            print(f"⚠️ Error extrayendo vendedor: {e}")
            # Garantizar valor por defecto en caso de error
            datos['vendedor'] = "Error en extracción"

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
                    if address_text and es_probable_direccion(address_text.strip()):
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
                        if text and es_probable_direccion(text.strip()):
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
                        if es_probable_direccion(line_clean):
                            datos['direccion'] = line_clean
                            print(f"  📍 Dirección encontrada (E3): {datos['direccion']}")
                            return
                        
            except Exception as e:
                print(f"     ⚠️ Error en estrategia 3: {e}")

            print("  ❌ No se pudo extraer dirección con ninguna estrategia")
                        
        except Exception as e:
            print(f"⚠️ Error extrayendo dirección: {e}")

    # Funciones de dirección movidas a direccion_utils.py

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

    # Funciones _parsear_ubicacion_completa y _normalizar_estado movidas a direccion_utils.py

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

    async def _extraer_campos_basicos_desde_categorias(self, datos):
        """Extrae campos básicos estructurados desde categorías principales"""
        try:
            # Inicializar campos básicos si no existen
            if 'recamaras' not in datos:
                datos['recamaras'] = None
            if 'banos' not in datos:
                datos['banos'] = None
            if 'construccion' not in datos:
                datos['construccion'] = None
            if 'terreno' not in datos:
                datos['terreno'] = None
            if 'estacionamiento' not in datos:
                datos['estacionamiento'] = None
            if 'moneda' not in datos:
                datos['moneda'] = 'MXN'  # Default para México
            
            # Buscar campos en categoría 'principales'
            if 'principales' in datos and isinstance(datos['principales'], dict):
                principales = datos['principales']
                
                # Recámaras
                for key, value in principales.items():
                    key_lower = key.lower()
                    if 'recámara' in key_lower or 'recamara' in key_lower:
                        datos['recamaras'] = parse_numeric(value)
                        print(f"   ✅ Recámaras encontradas: {datos['recamaras']}")
                        break
                
                # Baños
                for key, value in principales.items():
                    key_lower = key.lower()
                    if 'baño' in key_lower or 'bano' in key_lower:
                        datos['banos'] = parse_numeric(value)
                        print(f"   ✅ Baños encontrados: {datos['banos']}")
                        break
                
                # Superficie construida
                for key, value in principales.items():
                    key_lower = key.lower()
                    if 'superficie construida' in key_lower or 'construida' in key_lower:
                        datos['construccion'] = parse_numeric(value)
                        print(f"   ✅ Construcción encontrada: {datos['construccion']} m²")
                        break
                
                # Superficie total/terreno
                for key, value in principales.items():
                    key_lower = key.lower()
                    if 'superficie total' in key_lower or 'terreno' in key_lower:
                        datos['terreno'] = parse_numeric(value)
                        print(f"   ✅ Terreno encontrado: {datos['terreno']} m²")
                        break
                
                # Estacionamiento
                for key, value in principales.items():
                    key_lower = key.lower()
                    if 'estacionamiento' in key_lower or 'garage' in key_lower or 'cochera' in key_lower:
                        datos['estacionamiento'] = parse_numeric(value)
                        print(f"   ✅ Estacionamiento encontrado: {datos['estacionamiento']}")
                        break
            
            # Si no hay precio pero hay moneda, eliminar moneda
            if not datos.get('precio') and datos.get('moneda'):
                datos['moneda'] = None
                
        except Exception as e:
            print(f"⚠️ Error extrayendo campos básicos: {e}")

    async def _extraer_categorias_optimizado(self, page, navigator=None) -> dict:
        """Extrae SOLO categorías de forma optimizada sin metadatos completos"""
        try:
            print("   🚀 Extracción ultra-ligera de categorías...")
            
            # Expansión rápida
            if navigator and hasattr(navigator, 'click_expand_characteristics_button'):
                await navigator.click_expand_characteristics_button(page)
            else:
                await self._expand_characteristics_fallback(page)
            
            await page.wait_for_timeout(500)  # Reducido de 1000ms
            
            # Buscar contenedor principal
            main_container = await page.query_selector('.ui-pdp-container__row.ui-pdp-container__row--technical-specifications')
            if not main_container:
                return {}
            
            # Extraer solo categorías sin metadatos
            category_tables = await main_container.query_selector_all('.ui-vpp-striped-specs__table')
            if not category_tables:
                return {}
            
            categorias = {}
            
            for i, tabla in enumerate(category_tables):
                try:
                    # Nombre de categoría simplificado
                    categoria_nombre = f"categoria_{i+1}"
                    
                    # Buscar título rápido
                    for selector in ['h3', 'h4', '.ui-vpp-striped-specs__header']:
                        titulo_element = await tabla.query_selector(selector)
                        if titulo_element:
                            titulo_text = await titulo_element.text_content()
                            if titulo_text and len(titulo_text.strip()) > 0:
                                categoria_nombre = titulo_text.strip().lower().replace(' ', '_').replace('ñ', 'n').replace(':', '').replace('-', '_')
                                break
                    
                    # Extraer datos de filas (simplificado)
                    categoria_data = {}
                    filas = await tabla.query_selector_all('tr')
                    
                    for fila in filas:
                        try:
                            cells = await fila.query_selector_all('th, td')
                            if len(cells) >= 2:
                                key = await cells[0].text_content()
                                value = await cells[1].text_content()
                                
                                if key and value:
                                    key_clean = key.strip()
                                    value_clean = value.strip()
                                    
                                    if (key_clean and value_clean and 
                                        key_clean != value_clean and 
                                        len(key_clean) > 1):
                                        categoria_data[key_clean] = value_clean
                        except:
                            continue
                    
                    if categoria_data:
                        categorias[categoria_nombre] = categoria_data
                
                except Exception as e:
                    continue
            
            print(f"   ⚡ {len(categorias)} categorías extraídas (modo optimizado)")
            return categorias
            
        except Exception as e:
            print(f"⚠️ Error en extracción optimizada: {e}")
            return {} 