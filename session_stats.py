#!/usr/bin/env python3
"""
GESTOR DE ESTADÍSTICAS DE SESIÓN - SCRAPER MERCADOLIBRE
======================================================

Centraliza el manejo de estadísticas de sesión para scraping masivo.
Refactorizado desde scraper_masivo_cuernavaca.py siguiendo principios de modularidad.
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class SessionStats:
    """
    Estructura de datos para estadísticas de sesión de scraping.
    
    Attributes:
        total_processed: Total de propiedades procesadas
        successful_extractions: Extracciones exitosas
        failed_extractions: Extracciones fallidas  
        consecutive_failures: Fallos consecutivos (para circuit breaker)
        session_start_time: Timestamp de inicio de sesión
        requests_in_session: Requests realizados en sesión actual
        blocking_detected: Si se detectó bloqueo en sesión
    """
    total_processed: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    consecutive_failures: int = 0
    session_start_time: float = field(default_factory=time.time)
    requests_in_session: int = 0
    blocking_detected: bool = False


class SessionStatsManager:
    """
    Gestor centralizado de estadísticas de sesión para scraping masivo.
    
    Maneja tracking, cálculos y reporting de métricas de performance
    durante operaciones de scraping con medidas antibloqueo.
    """
    
    def __init__(self):
        """Inicializa gestor con estadísticas limpias."""
        self.stats = SessionStats()
    
    def update_from_result(self, resultado: Dict) -> None:
        """
        Actualiza estadísticas basándose en resultado de extracción.
        
        Args:
            resultado (Dict): Diccionario con resultado de procesamiento
                            Debe contener 'status' key con valor 'exitoso' o error
        
        Examples:
            >>> manager = SessionStatsManager()
            >>> resultado = {'status': 'exitoso', 'url': 'https://...'}
            >>> manager.update_from_result(resultado)
            >>> manager.get_success_rate()
            100.0
        """
        self.stats.total_processed += 1
        self.stats.requests_in_session += 1
        
        if resultado.get('status') == 'exitoso':
            self.stats.successful_extractions += 1
            self.stats.consecutive_failures = 0  # Reason: Reset en éxito
        else:
            self.stats.failed_extractions += 1
            self.stats.consecutive_failures += 1
    
    def reset_session(self) -> None:
        """
        Resetea estadísticas para nueva sesión (mantiene totales acumulados).
        
        Usado cuando se rota sesión por medidas antibloqueo,
        preservando estadísticas totales pero reseteando métricas de sesión.
        """
        # Reason: Mantener totales acumulados pero resetear métricas de sesión específica
        self.stats.session_start_time = time.time()
        self.stats.requests_in_session = 0
        # Nota: No reseteamos consecutive_failures aquí ya que es importante para circuit breaker
    
    def mark_blocking_detected(self) -> None:
        """Marca que se detectó bloqueo en la sesión actual."""
        self.stats.blocking_detected = True
    
    def get_success_rate(self) -> float:
        """
        Calcula tasa de éxito porcentual.
        
        Returns:
            float: Porcentaje de éxito (0.0-100.0)
        """
        if self.stats.total_processed == 0:
            return 0.0
        return (self.stats.successful_extractions / self.stats.total_processed) * 100
    
    def get_session_duration(self) -> float:
        """
        Obtiene duración de sesión actual en segundos.
        
        Returns:
            float: Segundos transcurridos desde inicio de sesión
        """
        return time.time() - self.stats.session_start_time
    
    def get_avg_time_per_property(self) -> float:
        """
        Calcula tiempo promedio por propiedad procesada.
        
        Returns:
            float: Segundos promedio por propiedad
        """
        if self.stats.total_processed == 0:
            return 0.0
        total_duration = time.time() - self.stats.session_start_time
        return total_duration / self.stats.total_processed
    
    def should_circuit_break(self, max_consecutive_failures: int = 3) -> bool:
        """
        Determina si debe activarse circuit breaker.
        
        Args:
            max_consecutive_failures (int): Máximo de fallos consecutivos permitidos
            
        Returns:
            bool: True si debe activarse circuit breaker
        """
        return self.stats.consecutive_failures >= max_consecutive_failures
    
    async def handle_circuit_breaker(self, max_consecutive_failures: int = 3) -> bool:
        """
        Maneja circuit breaker con cooldown automático integrado.
        
        Combina verificación + cooldown de la función obsoleta circuit_breaker_check.
        
        Args:
            max_consecutive_failures (int): Máximo de fallos consecutivos permitidos
            
        Returns:
            bool: True si se activó circuit breaker y se aplicó cooldown
        """
        import asyncio
        import random
        
        try:
            # Tasa de fallo máxima permitida  
            max_failure_rate = 0.3  # 30%
            
            if self.stats.consecutive_failures >= max_consecutive_failures:
                print(f"🚨 Circuit breaker: {self.stats.consecutive_failures} fallos consecutivos")
                cooldown = random.uniform(30, 60)  # Cooldown de 30-60 segundos
                print(f"❄️ Cooldown de {cooldown:.1f}s antes de continuar...")
                await asyncio.sleep(cooldown)
                return True
            
            if self.stats.total_processed > 10:
                failure_rate = self.stats.consecutive_failures / self.stats.total_processed
                if failure_rate > max_failure_rate:
                    print(f"🚨 Circuit breaker: tasa de fallo {failure_rate:.1%} > {max_failure_rate:.1%}")
                    cooldown = random.uniform(30, 60)
                    print(f"❄️ Cooldown de {cooldown:.1f}s antes de continuar...")
                    await asyncio.sleep(cooldown)
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error en circuit breaker: {e}")
            return False
    
    def get_progress_summary(self, current: int, total: int) -> Dict[str, float]:
        """
        Genera resumen de progreso para display.
        
        Args:
            current (int): Elemento actual procesándose
            total (int): Total de elementos a procesar
            
        Returns:
            Dict[str, float]: Métricas de progreso formateadas
        """
        percentage = (current / total) * 100 if total > 0 else 0
        
        return {
            'percentage': round(percentage, 1),
            'successful': self.stats.successful_extractions,
            'failed': self.stats.failed_extractions,
            'success_rate': round(self.get_success_rate(), 1),
            'session_duration_minutes': round(self.get_session_duration() / 60, 2),
            'avg_time_per_property': round(self.get_avg_time_per_property(), 2)
        }
    
    def get_final_report_data(self, total_target: int) -> Dict:
        """
        Genera datos para reporte final de scraping masivo.
        
        Args:
            total_target (int): Número objetivo de propiedades
            
        Returns:
            Dict: Estadísticas finales estructuradas
        """
        total_time = time.time() - self.stats.session_start_time
        
        return {
            'duracion_total_minutos': round(total_time / 60, 2),
            'propiedades_objetivo': total_target,
            'propiedades_exitosas': self.stats.successful_extractions,
            'propiedades_fallidas': self.stats.failed_extractions,
            'tasa_exito_final': round(self.get_success_rate(), 2),
            'promedio_tiempo_por_propiedad': round(self.get_avg_time_per_property(), 2),
            'requests_totales': self.stats.requests_in_session,
            'bloqueos_detectados': self.stats.blocking_detected
        } 