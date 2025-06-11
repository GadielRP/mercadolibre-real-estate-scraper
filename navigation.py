#!/usr/bin/env python3
"""
NAVEGACIÓN Y STEALTH - SCRAPER MERCADOLIBRE
==========================================

Funciones de navegación, stealth y configuración de browser.
Modularizado para cumplir reglas de <500 líneas.
"""

import random
import asyncio
from typing import Optional, Dict
from playwright.async_api import BrowserContext, Page
from models import ConfiguracionHibridaUltraAvanzada, ProxyConfig


class NavigatorStealth:
    """Navegador con características stealth y anti-detección"""
    
    def __init__(self, config: ConfiguracionHibridaUltraAvanzada):
        """Inicializa navigator con configuración"""
        self.config = config
        
    def get_random_user_agent(self) -> str:
        """Obtiene user agent aleatorio"""
        try:
            all_agents = self.config.USER_AGENTS_WINDOWS + self.config.USER_AGENTS_MAC
            return random.choice(all_agents)
        except:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def get_random_viewport(self) -> Dict[str, int]:
        """Obtiene viewport aleatorio"""
        try:
            return random.choice(self.config.VIEWPORTS)
        except:
            return {"width": 1920, "height": 1080}
    
    def get_random_proxy(self) -> Optional[ProxyConfig]:
        """Obtiene proxy aleatorio (si están disponibles)"""
        if not self.config.PROXIES_RESIDENCIALES:
            return None
        return random.choice(self.config.PROXIES_RESIDENCIALES)
    
    async def setup_stealth_context(self, context: BrowserContext, user_agent: str) -> None:
        """Configura contexto con bypass de MercadoLibre VALIDADO 100% EFECTIVO"""
        try:
            # 🎯 BYPASS MERCADOLIBRE - SOLUCIÓN VALIDADA
            print("🛡️ Aplicando bypass MercadoLibre validado...")
            
            # ✅ COOKIES ESPECÍFICAS para forzar interfaz desktop
            await context.add_cookies([
                {
                    'name': '_d2id',
                    'value': 'desktop-browser-session',
                    'domain': '.mercadolibre.com.mx',
                    'path': '/',
                    'secure': True,
                    'httpOnly': False
                },
                {
                    'name': 'deviceType',
                    'value': 'desktop',
                    'domain': '.mercadolibre.com.mx',
                    'path': '/',
                    'secure': True,
                    'httpOnly': False
                }
            ])
            
            # ✅ HEADERS DESKTOP específicos con referrer crítico
            await context.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'es-MX,es-419;q=0.9,es;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Referer': 'https://listado.mercadolibre.com.mx/',  # ✅ CRÍTICO - simula navegación desde listado
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',  # ✅ CRÍTICO - FORZAR NO MÓVIL
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-bitness': '"64"',
            })
            
            # ✅ JAVASCRIPT INIT SCRIPT para configuración desktop
            await context.add_init_script("""
                // 🎯 BYPASS MERCADOLIBRE - Configuración desktop específica
                
                // Local Storage crítico para MercadoLibre
                localStorage.setItem('deviceType', 'desktop');
                localStorage.setItem('viewport', 'desktop');
                localStorage.setItem('isMobile', 'false');
                localStorage.setItem('userAgent', 'desktop');
                
                // Ocultar webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Propiedades de pantalla desktop
                Object.defineProperty(screen, 'width', {
                    get: () => 1920,
                });
                Object.defineProperty(screen, 'height', {
                    get: () => 1080,
                });
                Object.defineProperty(screen, 'availWidth', {
                    get: () => 1920,
                });
                Object.defineProperty(screen, 'availHeight', {
                    get: () => 1040,
                });
                
                // Device pixel ratio desktop
                Object.defineProperty(window, 'devicePixelRatio', {
                    get: () => 1,
                });
                
                // Window dimensions
                Object.defineProperty(window, 'innerWidth', {
                    get: () => 1920,
                });
                Object.defineProperty(window, 'innerHeight', {
                    get: () => 1040,
                });
                Object.defineProperty(window, 'outerWidth', {
                    get: () => 1920,
                });
                Object.defineProperty(window, 'outerHeight', {
                    get: () => 1080,
                });
                
                // Override touch detection
                Object.defineProperty(navigator, 'maxTouchPoints', {
                    get: () => 0,
                });
                
                // CSS para forzar layout desktop
                const style = document.createElement('style');
                style.textContent = `
                    /* Forzar vista desktop */
                    @media screen {
                        .ui-pdp-container, 
                        .ui-pdp-specs__container {
                            max-width: none !important;
                            width: 100% !important;
                        }
                        
                        /* Mostrar todas las especificaciones expandidas */
                        .ui-pdp-specs__table,
                        .andes-table {
                            display: block !important;
                            opacity: 1 !important;
                        }
                    }
                `;
                
                // Agregar CSS cuando el DOM esté listo
                if (document.head) {
                    document.head.appendChild(style);
                } else {
                    document.addEventListener('DOMContentLoaded', () => {
                        if (document.head) {
                            document.head.appendChild(style);
                        }
                    });
                }
            """)
            
            print(f"✅ Bypass MercadoLibre configurado con UA: {user_agent[:50]}...")
            
        except Exception as e:
            print(f"⚠️ Error configurando bypass context: {e}")
    
    async def setup_stealth_page(self, page: Page) -> None:
        """Configura página con configuraciones adicionales de bypass"""
        try:
            # ✅ Configurar viewport desktop
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # ✅ Configurar contexto como desktop
            await page.evaluate("""
                // Configurar flags adicionales post-carga
                if (typeof window !== 'undefined') {
                    window._isMobile = false;
                    window._isDesktop = true;
                    window._deviceType = 'desktop';
                }
            """)
            
            print("✅ Configuración de bypass página aplicada")
            
        except Exception as e:
            print(f"⚠️ Error configurando bypass page: {e}")

    async def click_expand_characteristics_button(self, page: Page) -> bool:
        """
        Busca y hace click en el botón 'Ver todas las características' para expandir las tablas
        Returns True si encontró y clickeó el botón, False si no
        """
        try:
            print("🔍 Buscando botón 'Ver todas las características'...")
            
            # Esperar un momento para que la página cargue completamente
            await page.wait_for_timeout(2000)
            
            # Verificar qué tipo de interfaz estamos viendo
            product_interface = await page.query_selector('text="Características del producto"')
            inmueble_interface = await page.query_selector('text="Características del inmueble"')
            
            if product_interface:
                print("✅ Interfaz de PRODUCTO detectada - Tablas ya expandidas")
                return True
            elif inmueble_interface:
                print("🔑 Interfaz de INMUEBLE detectada - Buscando botón de expansión...")
            else:
                print("🔍 Interfaz no identificada claramente, buscando botón...")
            
            # Buscar el botón específico con múltiples estrategias
            expand_button = None
            
            # Estrategia 1: Buscar por texto exacto
            expand_button = await page.query_selector('button:has-text("Ver todas las características")')
            
            # Estrategia 2: Buscar por clase específica
            if not expand_button:
                expand_buttons = await page.query_selector_all('.ui-pdp-collapsable__action.ui-vpp-highlighted-specs__striped-collapsed__action')
                for button in expand_buttons:
                    button_text = await button.text_content()
                    if button_text and 'características' in button_text.lower():
                        expand_button = button
                        break
            
            # Estrategia 3: Buscar botones de colapso/expansión
            if not expand_button:
                expand_buttons = await page.query_selector_all('button[class*="collapsable"], button[class*="collapse"]')
                for button in expand_buttons:
                    button_text = await button.text_content()
                    if button_text and ('características' in button_text.lower() or 'ver todas' in button_text.lower()):
                        expand_button = button
                        break
            
            # Estrategia 4: Buscar cualquier botón con texto relacionado
            if not expand_button:
                all_buttons = await page.query_selector_all('button')
                for button in all_buttons:
                    button_text = await button.text_content()
                    if button_text and ('ver todas' in button_text.lower() and 'características' in button_text.lower()):
                        expand_button = button
                        break
            
            # Si encontramos el botón, hacer click
            if expand_button:
                try:
                    is_visible = await expand_button.is_visible()
                    button_text = await expand_button.text_content() or "Sin texto"
                    
                    if is_visible:
                        print(f"🖱️ Haciendo click en botón: '{button_text.strip()}'")
                        await expand_button.click()
                        
                        # Esperar a que las tablas se expandan
                        await page.wait_for_timeout(3000)
                        
                        # Verificar que las tablas se expandieron
                        tables = await page.query_selector_all('.andes-table')
                        if tables:
                            print(f"✅ Botón clickeado exitosamente - {len(tables)} tablas encontradas")
                            return True
                        else:
                            print("⚠️ Botón clickeado pero no se encontraron tablas")
                            return False
                    else:
                        print(f"⚠️ Botón encontrado pero no visible: '{button_text.strip()}'")
                        return False
                        
                except Exception as e:
                    print(f"⚠️ Error haciendo click en el botón: {e}")
                    return False
            else:
                print("🔍 No se encontró botón de expansión - las tablas pueden estar ya expandidas")
                
                # Verificar si hay tablas disponibles sin necesidad de expansión
                tables = await page.query_selector_all('.andes-table')
                if tables:
                    print(f"✅ {len(tables)} tablas encontradas sin necesidad de expansión")
                    return True
                else:
                    print("❌ No se encontraron tablas ni botón de expansión")
                    return False
            
        except Exception as e:
            print(f"❌ Error en click_expand_characteristics_button: {e}")
            return False
    
    async def human_delay(self, delay_type: str = 'between_actions') -> None:
        """Genera delays humanos realistas"""
        try:
            delay_range = self.config.HUMAN_DELAYS.get(delay_type, (1.0, 2.0))
            delay = random.uniform(delay_range[0], delay_range[1])
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"⚠️ Error en human delay: {e}")
            await asyncio.sleep(1.0)  # Fallback
    
    async def scroll_naturally(self, page: Page) -> None:
        """Realiza scroll natural humano"""
        try:
            # Obtener altura de la página
            page_height = await page.evaluate("document.body.scrollHeight")
            viewport_height = await page.evaluate("window.innerHeight")
            
            # Scroll gradual
            scroll_positions = []
            current_pos = 0
            while current_pos < page_height:
                scroll_step = random.randint(200, 600)
                current_pos += scroll_step
                if current_pos > page_height:
                    current_pos = page_height
                scroll_positions.append(current_pos)
            
            # Ejecutar scrolls con delays
            for position in scroll_positions:
                await page.evaluate(f"window.scrollTo(0, {position})")
                await self.human_delay('scroll_pause')
            
            # Volver arriba gradualmente
            await page.evaluate("window.scrollTo(0, 0)")
            await self.human_delay('scroll_pause')
            
            print("✅ Scroll natural completado")
            
        except Exception as e:
            print(f"⚠️ Error en scroll natural: {e}")
    
    async def navigate_safely(self, page: Page, url: str, max_retries: int = 3) -> bool:
        """Navega a URL de forma segura con reintentos"""
        for attempt in range(max_retries):
            try:
                print(f"🔗 Navegando a: {url} (intento {attempt + 1}/{max_retries})")
                
                # Delay antes de navegar
                await self.human_delay('between_actions')
                
                # Navegar con timeout
                response = await page.goto(url, 
                    wait_until='domcontentloaded',
                    timeout=30000
                )
                
                if response and response.status < 400:
                    print(f"✅ Navegación exitosa: {response.status}")
                    
                    # Esperar carga completa
                    await self.human_delay('page_load_wait')
                    
                    # Verificar que no sea página de error
                    page_title = await page.title()
                    if 'error' in page_title.lower() or 'not found' in page_title.lower():
                        print(f"⚠️ Página de error detectada: {page_title}")
                        if attempt < max_retries - 1:
                            continue
                        return False
                    
                    return True
                else:
                    print(f"⚠️ Respuesta no válida: {response.status if response else 'Sin respuesta'}")
                    
            except Exception as e:
                print(f"❌ Error navegando (intento {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    delay = random.uniform(2.0, 5.0)
                    print(f"⏳ Esperando {delay:.1f}s antes del siguiente intento...")
                    await asyncio.sleep(delay)
                    
        print(f"❌ Falló navegación después de {max_retries} intentos")
        return False
    
    async def check_page_health(self, page: Page) -> bool:
        """Verifica salud de la página actual"""
        try:
            # Verificar que la página responda
            page_title = await page.title()
            current_url = page.url
            
            # Checks básicos
            if not page_title or len(page_title.strip()) == 0:
                print("⚠️ Página sin título")
                return False
            
            # Verificar si es página de error común
            error_indicators = [
                'error', 'not found', '404', '500', 'blocked', 
                'access denied', 'captcha', 'robot'
            ]
            
            title_lower = page_title.lower()
            url_lower = current_url.lower()
            
            for indicator in error_indicators:
                if indicator in title_lower or indicator in url_lower:
                    print(f"⚠️ Página de error detectada: {indicator}")
                    return False
            
            # Verificar contenido básico
            body = await page.query_selector('body')
            if not body:
                print("⚠️ No se encontró elemento body")
                return False
            
            print(f"✅ Página saludable: {page_title[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Error verificando salud de página: {e}")
            return False
    
    async def handle_popup_and_cookies(self, page: Page) -> None:
        """Maneja popups y cookies automáticamente"""
        try:
            # Esperar un momento para que aparezcan popups
            await asyncio.sleep(2)
            
            # Selectores comunes de popups/cookies
            popup_selectors = [
                'button[data-testid="action:understood"]',  # MercadoLibre cookies
                'button:has-text("Entendido")',
                'button:has-text("Acepto")',
                'button:has-text("Aceptar")',
                'button:has-text("OK")',
                '.cookie-accept',
                '.popup-close',
                '[role="dialog"] button',
                '.modal-close'
            ]
            
            for selector in popup_selectors:
                try:
                    popup_button = await page.query_selector(selector)
                    if popup_button:
                        is_visible = await popup_button.is_visible()
                        if is_visible:
                            print(f"🖱️ Cerrando popup: {selector}")
                            await popup_button.click()
                            await self.human_delay('between_actions')
                            break
                except:
                    continue
            
        except Exception as e:
            print(f"⚠️ Error manejando popups: {e}")
    
    async def warm_up_navigation(self, page: Page) -> None:
        """Calentamiento de navegación para parecer más humano"""
        try:
            print("🔥 Calentando navegación...")
            
            # Visitar entrada gradual
            for entry_url in self.config.ENTRY_URLS:
                success = await self.navigate_safely(page, entry_url)
                if success:
                    await self.handle_popup_and_cookies(page)
                    await self.scroll_naturally(page)
                    await self.human_delay('between_actions')
                else:
                    print(f"⚠️ Falló entrada a: {entry_url}")
                    
            print("✅ Calentamiento completado")
            
        except Exception as e:
            print(f"❌ Error en calentamiento: {e}")
    
    async def extract_property_urls_from_listing(self, page: Page, max_properties: int = 10) -> list:
        """Extrae URLs de propiedades desde página de listado"""
        try:
            print(f"🔍 Buscando URLs de propiedades (máximo: {max_properties})...")
            
            # Esperar a que carguen los resultados
            await page.wait_for_selector('.ui-search-results', timeout=15000)
            await self.human_delay('page_load_wait')
            
            # Selectores para enlaces de propiedades
            property_selectors = [
                '.ui-search-result__content a[href*="MLM-"]',
                '.ui-search-item__group a[href*="MLM-"]',
                'a[href*="/MLM-"]',
                '.ui-search-link[href*="MLM-"]'
            ]
            
            urls_encontradas = set()
            
            for selector in property_selectors:
                try:
                    links = await page.query_selector_all(selector)
                    
                    for link in links:
                        href = await link.get_attribute('href')
                        if href and 'MLM-' in href:
                            # Normalizar URL
                            if href.startswith('/'):
                                href = f"https://casa.mercadolibre.com.mx{href}"
                            elif not href.startswith('http'):
                                href = f"https://casa.mercadolibre.com.mx/{href}"
                            
                            urls_encontradas.add(href)
                            
                            if len(urls_encontradas) >= max_properties:
                                break
                    
                    if len(urls_encontradas) >= max_properties:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error con selector {selector}: {e}")
                    continue
            
            urls_lista = list(urls_encontradas)[:max_properties]
            print(f"✅ Encontradas {len(urls_lista)} URLs de propiedades")
            
            return urls_lista
            
        except Exception as e:
            print(f"❌ Error extrayendo URLs: {e}")
            return []

    # ===== NUEVAS FUNCIONES PARA SCRAPING MASIVO =====
    
    async def rate_limit_control(self, request_count: int, session_start_time: float) -> None:
        """Control de velocidad para evitar rate limiting"""
        try:
            import time
            
            current_time = time.time()
            elapsed_time = current_time - session_start_time
            
            # Calcular requests por minuto actual
            if elapsed_time > 0:
                rpm_actual = (request_count * 60) / elapsed_time
                
                # Rate limit: máximo 8 requests por minuto (conservador)
                max_rpm = 8
                
                if rpm_actual > max_rpm:
                    # Calcular delay necesario
                    target_delay = (request_count * 60) / max_rpm - elapsed_time
                    
                    if target_delay > 0:
                        print(f"⏳ Rate limiting: esperando {target_delay:.1f}s (RPM actual: {rpm_actual:.1f})")
                        await asyncio.sleep(target_delay)
            
            # Delay adicional aleatorio entre requests
            extra_delay = random.uniform(2.0, 5.0)
            print(f"⏱️ Delay entre propiedades: {extra_delay:.1f}s")
            await asyncio.sleep(extra_delay)
            
        except Exception as e:
            print(f"⚠️ Error en rate limiting: {e}")
            await asyncio.sleep(3.0)  # Fallback delay
    
    async def should_rotate_session(self, requests_in_session: int, session_duration: float) -> bool:
        """Determina si debe rotar la sesión actual"""
        try:
            # Criterios para rotación
            max_requests_per_session = random.randint(15, 25)  # Entre 15-25 requests
            max_session_duration = random.uniform(300, 600)    # Entre 5-10 minutos
            
            if requests_in_session >= max_requests_per_session:
                print(f"🔄 Rotación por requests: {requests_in_session}/{max_requests_per_session}")
                return True
                
            if session_duration >= max_session_duration:
                print(f"🔄 Rotación por tiempo: {session_duration/60:.1f} minutos")
                return True
                
            # Rotación aleatoria (5% probabilidad)
            if random.random() < 0.05:
                print("🔄 Rotación aleatoria de sesión")
                return True
                
            return False
            
        except Exception as e:
            print(f"⚠️ Error verificando rotación: {e}")
            return False
    
    async def circuit_breaker_check(self, consecutive_failures: int, total_requests: int) -> bool:
        """Circuit breaker para proteger contra bloqueos"""
        try:
            # Tasa de fallo máxima permitida
            max_failure_rate = 0.3  # 30%
            max_consecutive_failures = 5
            
            if consecutive_failures >= max_consecutive_failures:
                print(f"🚨 Circuit breaker: {consecutive_failures} fallos consecutivos")
                cooldown = random.uniform(30, 60)  # Cooldown de 30-60 segundos
                print(f"❄️ Cooldown de {cooldown:.1f}s antes de continuar...")
                await asyncio.sleep(cooldown)
                return True
            
            if total_requests > 10:
                failure_rate = consecutive_failures / total_requests
                if failure_rate > max_failure_rate:
                    print(f"🚨 Circuit breaker: tasa de fallo {failure_rate:.1%} > {max_failure_rate:.1%}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error en circuit breaker: {e}")
            return False
    
    async def enhanced_session_warming(self, page: Page) -> bool:
        """Calentamiento mejorado para scraping masivo"""
        try:
            print("🔥 Calentamiento mejorado para scraping masivo...")
            
            # 1. Visita gradual con comportamiento humano
            for i, entry_url in enumerate(self.config.ENTRY_URLS):
                print(f"🌐 Entrada {i+1}/{len(self.config.ENTRY_URLS)}: {entry_url}")
                
                success = await self.navigate_safely(page, entry_url)
                if not success:
                    print(f"⚠️ Falló entrada {i+1}")
                    continue
                    
                # Comportamiento humano real
                await self.handle_popup_and_cookies(page)
                await self.scroll_naturally(page)
                
                # Simular lectura/navegación
                read_time = random.uniform(5, 15)
                print(f"📖 Simulando lectura por {read_time:.1f}s...")
                await asyncio.sleep(read_time)
                
                # Delay entre páginas
                await self.human_delay('between_actions')
            
            # 2. Verificar que el calentamiento funcionó
            page_health = await self.check_page_health(page)
            if page_health:
                print("✅ Calentamiento mejorado exitoso")
                return True
            else:
                print("❌ Calentamiento falló - página no saludable")
                return False
                
        except Exception as e:
            print(f"❌ Error en calentamiento mejorado: {e}")
            return False
    
    async def detect_blocking_patterns(self, page: Page) -> Dict[str, bool]:
        """Detecta patrones de bloqueo común"""
        try:
            blocking_indicators = {
                'captcha': False,
                'rate_limited': False,
                'ip_blocked': False,
                'robot_detected': False
            }
            
            # Verificar título y contenido
            page_title = await page.title()
            page_content = await page.content()
            
            title_lower = page_title.lower()
            content_lower = page_content.lower()
            
            # Detectar CAPTCHA
            captcha_indicators = ['captcha', 'verificación', 'verificacion', 'robot', 'automated']
            for indicator in captcha_indicators:
                if indicator in title_lower or indicator in content_lower:
                    blocking_indicators['captcha'] = True
                    break
            
            # Detectar rate limiting
            rate_limit_indicators = ['too many requests', 'rate limit', 'slow down']
            for indicator in rate_limit_indicators:
                if indicator in content_lower:
                    blocking_indicators['rate_limited'] = True
                    break
            
            # Detectar bloqueo de IP
            ip_block_indicators = ['access denied', 'blocked', 'forbidden']
            for indicator in ip_block_indicators:
                if indicator in title_lower:
                    blocking_indicators['ip_blocked'] = True
                    break
            
            # Detectar detección de robot
            robot_indicators = ['automated traffic', 'bot detected', 'unusual activity']
            for indicator in robot_indicators:
                if indicator in content_lower:
                    blocking_indicators['robot_detected'] = True
                    break
            
            # Log resultados
            blocks_detected = sum(blocking_indicators.values())
            if blocks_detected > 0:
                print(f"🚨 Detectados {blocks_detected} indicadores de bloqueo:")
                for block_type, detected in blocking_indicators.items():
                    if detected:
                        print(f"   ❌ {block_type}")
            
            return blocking_indicators
            
        except Exception as e:
            print(f"⚠️ Error detectando bloqueos: {e}")
            return {'captcha': False, 'rate_limited': False, 'ip_blocked': False, 'robot_detected': False} 