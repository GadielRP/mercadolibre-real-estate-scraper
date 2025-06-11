#!/usr/bin/env python3
"""
UTILIDADES DE DIRECCIÓN - SCRAPER MERCADOLIBRE
==============================================

Funciones especializadas para procesamiento de direcciones y ubicaciones.
Refactorizado desde extractors.py siguiendo principios de separación de responsabilidades.
"""

from typing import Dict, Optional


def es_probable_direccion(text: str) -> bool:
    """
    Determina si un texto es probablemente una dirección válida.
    
    Aplica filtros estrictos y validaciones para identificar direcciones reales
    vs texto descriptivo o metadata de la página.
    
    Args:
        text (str): Texto a evaluar
        
    Returns:
        bool: True si el texto parece ser una dirección válida
        
    Examples:
        >>> es_probable_direccion("Calle Morelos 123, Centro, Cuernavaca, Morelos")
        True
        >>> es_probable_direccion("Casa nueva con 3 recámaras")
        False
    """
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
        'metropolitana', 'villa del real', 'mayorazgos', 'distrito federal', 'alvaro obregón', 'queretaro',
        'oaxaca', 'chiapas', 'tuxtla gutierrez', 'tapachula', 'campeche', 'quintana roo', 'cancun',
        'playa del carmen', 'tabasco', 'villahermosa', 'veracruz', 'xalapa', 'coatzacoalcos',
        'puebla', 'tlaxcala', 'guerrero', 'acapulco', 'chilpancingo', 'hidalgo', 'pachuca',
        'guanajuato', 'leon', 'irapuato', 'celaya', 'michoacan', 'morelia', 'lazaro cardenas'
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


def parsear_ubicacion_completa(direccion_raw: str) -> Dict[str, Optional[str]]:
    """
    Parsea dirección en componentes geográficos estructurados.
    
    Utiliza enfoque simple basado en últimos elementos separados por comas
    para extraer estado y ciudad de direcciones mexicanas.
    
    Args:
        direccion_raw (str): Dirección completa en string
        
    Returns:
        Dict[str, Optional[str]]: Diccionario con pais, estado, ciudad
        
    Examples:
        >>> parsear_ubicacion_completa("Privada Los Pinos 45, Centro, Cuernavaca, Morelos")
        {'pais': 'México', 'estado': 'Morelos', 'ciudad': 'Cuernavaca'}
        >>> parsear_ubicacion_completa("Colonia del Valle, CDMX")
        {'pais': 'México', 'estado': 'Ciudad de México', 'ciudad': 'Colonia del Valle'}
    """
    ubicacion = {
        'pais': 'México',
        'estado': None,
        'ciudad': None
    }
    
    if not direccion_raw:
        return ubicacion
        
    try:
        # ✅ LIMPIEZA PREVIA del string
        direccion_limpia = direccion_raw.strip()
        
        # Reason: Normalizar espacios y separadores para parsing consistente
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
            estado_normalizado = normalizar_estado(estado_raw)
            
            # ✅ ASIGNAR RESULTADOS
            ubicacion['estado'] = estado_normalizado
            ubicacion['ciudad'] = ciudad_raw.title()  # Capitalizar primera letra
            
        elif len(partes) == 1:
            # Solo un elemento - probablemente sea estado
            estado_raw = partes[0].strip()
            estado_normalizado = normalizar_estado(estado_raw)
            ubicacion['estado'] = estado_normalizado
                
    except Exception as e:
        # Reason: En caso de error, retornar estructura básica con México como país
        pass
        
    return ubicacion


def normalizar_estado(estado_raw: str) -> str:
    """
    Normaliza nombre de estado con mapeo de variantes comunes.
    
    Convierte abreviaciones y variantes comunes a nombres oficiales
    de estados mexicanos.
    
    Args:
        estado_raw (str): Nombre de estado en formato original
        
    Returns:
        str: Nombre normalizado del estado
        
    Examples:
        >>> normalizar_estado("CDMX")
        "Ciudad de México"
        >>> normalizar_estado("estado de morelos")
        "Morelos"
        >>> normalizar_estado("Yucatan")
        "Yucatán"
    """
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