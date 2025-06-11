#!/usr/bin/env python3
"""
UTILIDADES NUMÉRICAS - SCRAPER MERCADOLIBRE
==========================================

Funciones utilitarias para parsing numérico consolidadas.
Refactorizado desde extractors.py siguiendo principios de modularidad.
"""

import re
from typing import Union, Optional


def parse_numeric(value: str) -> Union[int, float, None]:
    """
    Parsea valor numérico desde string con lógica consolidada.
    
    Maneja automáticamente:
    - Enteros y flotantes
    - Formatos mexicanos (comas como separadores de miles)
    - Limpieza de caracteres no numéricos
    - Validación de valores vacíos/nulos
    
    Args:
        value (str): Valor string a parsear
        
    Returns:
        Union[int, float, None]: 
            - int si el valor es entero
            - float si tiene decimales
            - None si no se puede parsear
            
    Examples:
        >>> parse_numeric("2,550,000")
        2550000
        >>> parse_numeric("131.5")
        131.5
        >>> parse_numeric("$2,550,000.00")
        2550000.0
        >>> parse_numeric("")
        None
    """
    if not value:
        return None
        
    try:
        # Reason: Limpiar todos los caracteres no numéricos excepto comas y puntos
        clean_value = re.sub(r'[^\d,.]', '', value)
        
        if not clean_value:
            return None
            
        # Reason: Manejar formato mexicano donde coma = separador de miles y punto = decimal
        if ',' in clean_value and '.' not in clean_value:
            # Caso: "2,550" -> "2.550" (coma como separador de miles)
            clean_value = clean_value.replace(',', '.')
        elif ',' in clean_value and '.' in clean_value:
            # Caso: "2,550.00" -> "2550.00" (coma como separador de miles, punto como decimal)
            clean_value = clean_value.replace(',', '')
            
        # Convertir a float para manejar decimales
        numeric_value = float(clean_value)
        
        # Reason: Retornar int si el valor es entero para mantener tipos precisos
        if numeric_value.is_integer():
            return int(numeric_value)
        else:
            return numeric_value
            
    except (ValueError, AttributeError):
        # Reason: En caso de error, retornar None en lugar de raising exception
        return None 