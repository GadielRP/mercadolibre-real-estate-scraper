#!/usr/bin/env python3
"""
MERCADOLIBRE SCRAPER - TEST DE URL INDIVIDUAL
=============================================
Script para probar la extracción de una propiedad específica
Útil para debugging y validación de nuevas funcionalidades

FUNCIONALIDADES:
- Extracción de URL individual
- Logs detallados para debugging
- Reporte completo de la propiedad
- Validación de todos los campos
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

from navigation import NavigatorStealth
from extractors import ExtractorHibridoOptimizado
from models import ConfiguracionHibridaUltraAvanzada


class SingleURLTester:
    """Tester para URLs individuales"""
    
    def __init__(self):
        self.config = ConfiguracionHibridaUltraAvanzada()
        self.navigator = NavigatorStealth(self.config)
        self.extractor = ExtractorHibridoOptimizado()
    
    async def test_single_url(self, url: str, modo_completo: bool = False) -> dict:
        """
        Prueba la extracción de una URL individual
        
        Args:
            url: URL de la propiedad a probar
            modo_completo: Si True, incluye andes_table_raw para debugging avanzado
            
        Returns:
            dict: Datos extraídos de la propiedad
        """
        print(f"🧪 TESTING URL INDIVIDUAL")
        print("=" * 60)
        print(f"🔗 URL: {url}")
        print("=" * 60)
        
        async with async_playwright() as p:
            try:
                # Configurar browser
                browser = await self._setup_browser(p)
                context, page = await self._setup_session(browser)
                
                # Navegar a la URL
                print("🔗 Navegando a la propiedad...")
                success = await self.navigator.navigate_safely(page, url)
                
                if not success:
                    return {
                        'error': 'No se pudo navegar a la URL',
                        'status': 'failed_navigation'
                    }
                
                # Manejar popups
                await self.navigator.handle_popup_and_cookies(page)
                
                # Extraer datos
                modo_str = "completo (con andes_table_raw)" if modo_completo else "optimizado (sin andes_table_raw)"
                print(f"⚡ Iniciando extracción híbrida en modo {modo_str}...")
                datos = await self.extractor.extraer_datos_hibrido(
                    page, 
                    navigator=self.navigator,
                    incluir_andes_raw=modo_completo
                )
                
                # Agregar metadatos del test
                datos.update({
                    'test_url': url,
                    'test_timestamp': datetime.now().isoformat(),
                    'test_status': 'success'
                })
                
                print("✅ Extracción completada exitosamente")
                return datos
                
            except Exception as e:
                print(f"❌ Error durante la extracción: {e}")
                return {
                    'error': str(e),
                    'test_url': url,
                    'test_timestamp': datetime.now().isoformat(),
                    'test_status': 'failed_extraction'
                }
            
            finally:
                try:
                    await browser.close()
                except:
                    pass
    
    async def _setup_browser(self, p):
        """Configura browser con medidas antibloqueo"""
        print("🔧 Configurando browser...")
        
        browser_args = [
            "--no-first-run",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-dev-shm-usage",
            "--no-sandbox"
        ]
        
        browser = await p.chromium.launch(
            headless=True,
            args=browser_args
        )
        
        print("✅ Browser configurado")
        return browser
    
    async def _setup_session(self, browser):
        """Configura nueva sesión con bypass"""
        print("🛡️ Configurando sesión...")
        
        # User agent y viewport
        user_agent = self.navigator.get_random_user_agent()
        viewport = self.navigator.get_random_viewport()
        
        # Crear contexto
        context = await browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale='es-MX',
            timezone_id='America/Mexico_City'
        )
        
        # Aplicar bypass
        await self.navigator.setup_stealth_context(context, user_agent)
        
        # Crear página
        page = await context.new_page()
        await self.navigator.setup_stealth_page(page)
        
        print("✅ Sesión configurada")
        return context, page
    
    def generar_reporte(self, datos: dict) -> str:
        """Genera reporte detallado de la extracción"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_single_url_{timestamp}.json"
        
        # Guardar archivo JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📊 REPORTE DE EXTRACCIÓN")
        print("=" * 60)
        
        if datos.get('test_status') == 'success':
            # Contar campos extraídos
            campos_basicos = ['recamaras', 'banos', 'construccion', 'terreno', 'estacionamiento', 
                            'precio', 'moneda', 'direccion', 'tipo_propiedad', 'tipo_operacion', 'vendedor']
            
            campos_extraidos = sum(1 for campo in campos_basicos if datos.get(campo))
            
            print(f"✅ Status: ÉXITO")
            print(f"📋 Campos básicos extraídos: {campos_extraidos}/{len(campos_basicos)}")
            print(f"🏠 Tipo: {datos.get('tipo_propiedad', 'N/A')} en {datos.get('tipo_operacion', 'N/A')}")
            print(f"💰 Precio: {datos.get('precio', 'N/A')} {datos.get('moneda', 'N/A')}")
            print(f"👤 Vendedor: {datos.get('vendedor', 'N/A')}")
            print(f"📍 Dirección: {datos.get('direccion', 'N/A')}")
            
            # Mostrar categorías extraídas
            categorias = [key for key in datos.keys() if isinstance(datos[key], dict) and 
                         key not in ['andes_table_raw']]
            if categorias:
                print(f"📦 Categorías extraídas: {len(categorias)}")
                for cat in categorias:
                    items = len(datos[cat]) if isinstance(datos[cat], dict) else 0
                    print(f"   - {cat}: {items} campos")
            
        else:
            print(f"❌ Status: ERROR")
            print(f"❌ Error: {datos.get('error', 'Desconocido')}")
        
        print(f"\n📁 Reporte guardado: {filename}")
        return filename


def validar_url(url: str) -> bool:
    """Valida que la URL sea de MercadoLibre México"""
    dominios_validos = [
        'mercadolibre.com.mx',
        'articulo.mercadolibre.com.mx',
        'casa.mercadolibre.com.mx',
        'inmuebles.mercadolibre.com.mx'
    ]
    
    return any(dominio in url for dominio in dominios_validos)


async def main():
    """Función principal del tester"""
    print("🧪 MERCADOLIBRE SCRAPER - TEST DE URL INDIVIDUAL")
    print("=" * 60)
    
    while True:
        # Solicitar URL
        url = input("\n🔗 Ingrese la URL de la propiedad a probar (o 'exit' para salir): ").strip()
        
        if url.lower() in ['exit', 'salir', 'q', 'quit']:
            print("👋 ¡Hasta luego!")
            break
        
        if not url:
            print("❌ Por favor ingrese una URL válida")
            continue
        
        if not validar_url(url):
            print("❌ La URL debe ser de MercadoLibre México")
            continue
        
        # Preguntar modo de extracción
        print("\n🔧 MODO DE EXTRACCIÓN:")
        print("1. 🚀 Optimizado (recomendado) - Sin andes_table_raw (de donde se extraen las categorias flexibles), más rápido")
        print("2. 🔍 Completo - Con andes_table_raw (de donde se extraen las categorias flexibles) para debugging avanzado")
        
        while True:
            modo_input = input("Seleccione modo (1/2) [1]: ").strip()
            if modo_input == "" or modo_input == "1":
                modo_completo = False
                break
            elif modo_input == "2":
                modo_completo = True
                break
            else:
                print("❌ Opción inválida. Ingrese 1 o 2")
        
        # Ejecutar test
        tester = SingleURLTester()
        try:
            datos = await tester.test_single_url(url, modo_completo)
            filename = tester.generar_reporte(datos)
            
            # Preguntar si quiere ver el JSON completo
            ver_json = input("\n📄 ¿Ver JSON completo? (y/n): ").strip().lower()
            if ver_json in ['y', 'yes', 'si', 's']:
                print("\n" + "=" * 60)
                print("📄 JSON COMPLETO")
                print("=" * 60)
                print(json.dumps(datos, ensure_ascii=False, indent=2))
            
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        # Preguntar si quiere continuar
        continuar = input("\n🔄 ¿Probar otra URL? (y/n): ").strip().lower()
        if continuar not in ['y', 'yes', 'si', 's']:
            print("👋 ¡Hasta luego!")
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Programa terminado por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}") 