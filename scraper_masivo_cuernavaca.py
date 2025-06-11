#!/usr/bin/env python3
"""
SCRAPER MASIVO MERCADOLIBRE - CUERNAVACA
========================================

Scraper final con medidas antibloqueo completas para extraer
una página completa de propiedades en Cuernavaca.

CARACTERÍSTICAS:
- Medidas antibloqueo robustas
- Rate limiting inteligente
- Rotación de sesiones
- Circuit breaker
- Detección de bloqueos
- Extracción híbrida optimizada
"""

import asyncio
import time
import random
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict

# Importar módulos modularizados
from models import ConfiguracionHibridaUltraAvanzada
from navigation import NavigatorStealth
from extractors import ExtractorHibridoOptimizado
from test_runner import TestRunner


class ScraperMasivoCuernavaca:
    """Scraper masivo para inmuebles en Cuernavaca con medidas antibloqueo"""
    
    def __init__(self):
        self.config = ConfiguracionHibridaUltraAvanzada()
        self.navigator = NavigatorStealth(self.config)
        self.extractor = ExtractorHibridoOptimizado()
        self.test_runner = TestRunner()
        
        # Estadísticas de sesión
        self.session_stats = {
            'total_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'consecutive_failures': 0,
            'session_start_time': time.time(),
            'requests_in_session': 0,
            'blocking_detected': False
        }
    
    async def scrape_cuernavaca_full_page(self, max_properties: int = 50) -> Dict:
        """
        Scraping masivo de página completa de Cuernavaca
        
        Args:
            max_properties: Máximo número de propiedades a procesar
            
        Returns:
            Dict con resultados y estadísticas
        """
        print("🚀 SCRAPER MASIVO CUERNAVACA - PÁGINA COMPLETA")
        print("=" * 60)
        print(f"🎯 Objetivo: {max_properties} propiedades máximo")
        print(f"📅 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        resultados_finales = []
        urls_procesadas = set()
        
        try:
            async with async_playwright() as p:
                # Configuración inicial del browser
                browser = await self._setup_browser(p)
                context, page = await self._setup_session(browser)
                
                try:
                    # 1. CALENTAMIENTO MEJORADO
                    warming_success = await self.navigator.enhanced_session_warming(page)
                    if not warming_success:
                        print("⚠️ Calentamiento falló - continuando con precaución...")
                    
                    # 2. OBTENER URLs DE PROPIEDADES
                    urls_cuernavaca = await self._get_cuernavaca_urls(page, max_properties)
                    
                    if not urls_cuernavaca:
                        print("❌ No se encontraron URLs de propiedades")
                        return await self._generate_final_report(resultados_finales, "No URLs encontradas")
                    
                    print(f"✅ {len(urls_cuernavaca)} URLs encontradas para procesar")
                    
                    # 3. PROCESAMIENTO MASIVO CON MEDIDAS ANTIBLOQUEO
                    for i, url in enumerate(urls_cuernavaca, 1):
                        if url in urls_procesadas:
                            print(f"⏭️ URL {i} ya procesada - saltando")
                            continue
                            
                        print(f"\n🏠 PROPIEDAD {i}/{len(urls_cuernavaca)}")
                        print(f"URL: {url}")
                        print("-" * 50)
                        
                        # Verificar circuit breaker
                        should_break = await self.navigator.circuit_breaker_check(
                            self.session_stats['consecutive_failures'],
                            self.session_stats['total_processed']
                        )
                        
                        if should_break:
                            print("🚨 Circuit breaker activado - pausando")
                            self.session_stats['consecutive_failures'] = 0  # Reset
                        
                        # Control de rate limiting
                        await self.navigator.rate_limit_control(
                            self.session_stats['requests_in_session'],
                            self.session_stats['session_start_time']
                        )
                        
                        # Verificar si necesita rotación de sesión
                        session_duration = time.time() - self.session_stats['session_start_time']
                        should_rotate = await self.navigator.should_rotate_session(
                            self.session_stats['requests_in_session'],
                            session_duration
                        )
                        
                        if should_rotate:
                            print("🔄 Rotando sesión...")
                            await context.close()
                            context, page = await self._setup_session(browser)
                            self._reset_session_stats()
                        
                        # Procesar propiedad individual
                        resultado = await self._process_single_property(page, url, i)
                        resultados_finales.append(resultado)
                        urls_procesadas.add(url)
                        
                        # Actualizar estadísticas
                        self._update_session_stats(resultado)
                        
                        # Detectar bloqueos
                        blocking_detected = await self.navigator.detect_blocking_patterns(page)
                        if any(blocking_detected.values()):
                            print("🚨 Patrones de bloqueo detectados - activando medidas defensivas")
                            await asyncio.sleep(random.uniform(10, 30))
                        
                        # Progreso
                        self._show_progress(i, len(urls_cuernavaca))
                
                finally:
                    await browser.close()
        
        except Exception as e:
            print(f"❌ Error crítico en scraping masivo: {e}")
            
        # Generar reporte final
        return await self._generate_final_report(resultados_finales, "Completado")
    
    async def _setup_browser(self, p):
        """Configura browser con medidas antibloqueo"""
        print("🔧 Configurando browser con medidas antibloqueo...")
        
        # Browser args para evasión
        browser_args = [
            "--no-first-run",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-web-security",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection"
        ]
        
        browser = await p.chromium.launch(
            headless=True,
            args=browser_args
        )
        
        print("✅ Browser configurado")
        return browser
    
    async def _setup_session(self, browser):
        """Configura nueva sesión con bypass completo"""
        print("🛡️ Configurando nueva sesión...")
        
        # User agent y viewport aleatorios
        user_agent = self.navigator.get_random_user_agent()
        viewport = self.navigator.get_random_viewport()
        
        # 🔗 PROXY ALEATORIO (si están configurados)
        proxy = self.navigator.get_random_proxy()
        proxy_config = None
        proxy_info = "Sin proxy (IP directa)"
        
        if proxy:
            proxy_config = proxy.to_playwright_format()
            proxy_info = f"Proxy: {proxy.host}:{proxy.port} ({proxy.location})"
            print(f"🔗 Usando {proxy_info}")
        
        # Crear contexto con o sin proxy
        context_args = {
            'user_agent': user_agent,
            'viewport': viewport,
            'locale': 'es-MX',
            'timezone_id': 'America/Mexico_City'
        }
        
        if proxy_config:
            context_args['proxy'] = proxy_config
        
        context = await browser.new_context(**context_args)
        
        # Aplicar bypass
        await self.navigator.setup_stealth_context(context, user_agent)
        
        # Crear página
        page = await context.new_page()
        await self.navigator.setup_stealth_page(page)
        
        print(f"✅ Sesión configurada - UA: {user_agent[:50]}...")
        print(f"🌐 Red: {proxy_info}")
        
        return context, page
    
    async def _get_cuernavaca_urls(self, page, max_properties: int) -> List[str]:
        """Obtiene URLs de propiedades en Cuernavaca"""
        print("🔍 Obteniendo URLs de propiedades en Cuernavaca...")
        
        # URL de búsqueda específica para Cuernavaca
        search_url = "https://inmuebles.mercadolibre.com.mx/casas/venta/cuernavaca/"
        
        success = await self.navigator.navigate_safely(page, search_url)
        if not success:
            print("❌ No se pudo acceder a la página de búsqueda")
            return []
        
        # Manejar popups
        await self.navigator.handle_popup_and_cookies(page)
        
        # Extraer URLs
        urls = await self.navigator.extract_property_urls_from_listing(page, max_properties)
        
        return urls
    
    async def _process_single_property(self, page, url: str, property_number: int) -> Dict:
        """Procesa una propiedad individual con extracción híbrida"""
        resultado = {
            'url': url,
            'property_number': property_number,
            'status': 'pendiente',
            'timestamp': datetime.now().isoformat(),
            'processing_time_seconds': 0,
            'error': None
        }
        
        start_time = time.time()
        
        try:
            # Navegar a la propiedad
            success = await self.navigator.navigate_safely(page, url)
            if not success:
                resultado['status'] = 'error_navigation'
                resultado['error'] = 'No se pudo navegar a la URL'
                return resultado
            
            # Manejar popups
            await self.navigator.handle_popup_and_cookies(page)
            
            # Extracción híbrida optimizada (sin andes_table_raw para velocidad)
            datos_extraidos = await self.extractor.extraer_datos_hibrido(
                page, 
                navigator=self.navigator,
                incluir_andes_raw=False  # Optimización para velocidad
            )
            
            # Agregar metadatos
            datos_extraidos.update({
                'url': url,
                'property_number': property_number,
                'status': 'exitoso',
                'timestamp': resultado['timestamp']
            })
            
            resultado.update(datos_extraidos)
            
            print(f"✅ Propiedad {property_number} procesada exitosamente")
            
        except Exception as e:
            print(f"❌ Error procesando propiedad {property_number}: {e}")
            resultado['status'] = 'error_extraction'
            resultado['error'] = str(e)
        
        finally:
            resultado['processing_time_seconds'] = round(time.time() - start_time, 2)
        
        return resultado
    
    def _update_session_stats(self, resultado: Dict) -> None:
        """Actualiza estadísticas de sesión"""
        self.session_stats['total_processed'] += 1
        self.session_stats['requests_in_session'] += 1
        
        if resultado['status'] == 'exitoso':
            self.session_stats['successful_extractions'] += 1
            self.session_stats['consecutive_failures'] = 0  # Reset failures
        else:
            self.session_stats['failed_extractions'] += 1
            self.session_stats['consecutive_failures'] += 1
    
    def _reset_session_stats(self) -> None:
        """Resetea estadísticas de sesión para nueva sesión"""
        self.session_stats['session_start_time'] = time.time()
        self.session_stats['requests_in_session'] = 0
    
    def _show_progress(self, current: int, total: int) -> None:
        """Muestra progreso del scraping"""
        percentage = (current / total) * 100
        success_rate = (self.session_stats['successful_extractions'] / self.session_stats['total_processed'] * 100) if self.session_stats['total_processed'] > 0 else 0
        
        print(f"\n📊 PROGRESO: {current}/{total} ({percentage:.1f}%)")
        print(f"✅ Exitosas: {self.session_stats['successful_extractions']}")
        print(f"❌ Falladas: {self.session_stats['failed_extractions']}")
        print(f"📈 Tasa éxito: {success_rate:.1f}%")
    
    async def _generate_final_report(self, resultados: List[Dict], status: str) -> Dict:
        """Genera reporte final del scraping masivo"""
        print("\n" + "=" * 60)
        print("📊 GENERANDO REPORTE FINAL")
        print("=" * 60)
        
        # Generar archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scraping_masivo_cuernavaca_{timestamp}.json"
        
        # Usar test_runner para generar reporte completo
        reporte = self.test_runner.generar_reporte_hibrido(resultados, filename)
        
        # Estadísticas adicionales del scraping masivo
        total_time = time.time() - self.session_stats['session_start_time']
        
        reporte['scraping_masivo_stats'] = {
            'duracion_total_minutos': round(total_time / 60, 2),
            'propiedades_objetivo': len(resultados),
            'propiedades_exitosas': self.session_stats['successful_extractions'],
            'propiedades_fallidas': self.session_stats['failed_extractions'],
            'tasa_exito_final': round(self.session_stats['successful_extractions'] / len(resultados) * 100, 2) if resultados else 0,
            'promedio_tiempo_por_propiedad': round(total_time / len(resultados), 2) if resultados else 0,
            'status_final': status
        }
        
        print(f"✅ Reporte guardado: {filename}")
        return reporte


async def main():
    """Función principal para ejecutar scraping masivo"""
    print("🚀 INICIANDO SCRAPER MASIVO CUERNAVACA")
    print("=" * 60)
    
    # Configuración
    max_properties = input("Ingresa número máximo de propiedades a scrapear (default: 20): ").strip()
    if not max_properties or not max_properties.isdigit():
        max_properties = 20
    else:
        max_properties = int(max_properties)
    
    print(f"🎯 Configurado para máximo {max_properties} propiedades")
    
    # Ejecutar scraping
    scraper = ScraperMasivoCuernavaca()
    resultado_final = await scraper.scrape_cuernavaca_full_page(max_properties)
    
    print("\n🎉 SCRAPING MASIVO COMPLETADO")
    print("=" * 60)
    
    return resultado_final


if __name__ == "__main__":
    asyncio.run(main()) 