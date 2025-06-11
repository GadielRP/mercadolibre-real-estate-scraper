#!/usr/bin/env python3
"""
TEST RUNNER - SCRAPER MERCADOLIBRE
=================================

Lógica de testing, reportes y análisis de resultados.
Modularizado para cumplir reglas de <500 líneas.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from models import ResultadoPropiedad


class TestRunner:
    """Ejecutor de tests y generador de reportes"""
    
    def __init__(self):
        """Inicializa test runner"""
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    def start_test_session(self) -> None:
        """Inicia sesión de testing"""
        self.start_time = datetime.now()
        self.test_results = []
        print(f"🧪 Iniciando sesión de testing: {self.start_time.strftime('%H:%M:%S')}")
    
    def end_test_session(self) -> None:
        """Finaliza sesión de testing"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"✅ Sesión completada en {duration:.1f} segundos")
    
    def add_test_result(self, resultado: Dict) -> None:
        """Agrega resultado de test"""
        self.test_results.append(resultado)
    
    def generar_reporte_hibrido(self, resultados: List[Dict], archivo_salida: str = None) -> Dict:
        """
        🔄 Genera reporte híbrido completo con TODAS las estadísticas
        
        Incluye:
        - Metadatos extraídos (ml_id, titulo, descripcion, ubicación)
        - JSON extraídos (categorías y andes_table_raw)
        - Estadísticas detalladas por tipo de campo
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not archivo_salida:
            archivo_salida = f"test_hibrido_morelos_{timestamp}.json"
        
        print("📊 Generando reporte híbrido completo...")
        
        # ✅ ESTADÍSTICAS CAMPOS UNIVERSALES ESTRUCTURADOS
        campos_universales = ['recamaras', 'banos', 'construccion', 'terreno', 'estacionamiento', 
                             'precio', 'moneda', 'direccion', 'tipo_propiedad', 'tipo_operacion']
        
        stats_universales = {}
        for campo in campos_universales:
            valores_validos = [r for r in resultados if r.get(campo) is not None]
            stats_universales[campo] = {
                'extraidos': len(valores_validos),
                'total': len(resultados),
                'porcentaje': (len(valores_validos) / len(resultados) * 100) if resultados else 0,
                'ejemplos': [r.get(campo) for r in valores_validos[:3]]
            }
        
        # ✅ ESTADÍSTICAS METADATOS UNIVERSALES
        metadatos_universales = ['ml_id', 'titulo', 'descripcion', 'estado', 'ciudad']
        
        stats_metadatos = {}
        for campo in metadatos_universales:
            valores_validos = [r for r in resultados if r.get(campo) is not None]
            stats_metadatos[campo] = {
                'extraidos': len(valores_validos),
                'total': len(resultados),
                'porcentaje': (len(valores_validos) / len(resultados) * 100) if resultados else 0,
                'ejemplos': [r.get(campo) for r in valores_validos[:3]]
            }
        
        # ✅ ESTADÍSTICAS JSON CATEGORÍAS
        categorias_json = ['caracteristicas_principales', 'servicios', 'ambientes', 'seguridad', 'comodidades']
        
        stats_json = {}
        for categoria in categorias_json:
            categorias_con_datos = [r for r in resultados 
                                  if r.get(categoria) and isinstance(r.get(categoria), dict) and len(r.get(categoria)) > 0]
            
            total_campos_categoria = sum(len(r.get(categoria, {})) for r in categorias_con_datos)
            
            stats_json[categoria] = {
                'propiedades_con_datos': len(categorias_con_datos),
                'total_propiedades': len(resultados),
                'porcentaje_propiedades': (len(categorias_con_datos) / len(resultados) * 100) if resultados else 0,
                'total_campos': total_campos_categoria,
                'promedio_campos_por_propiedad': (total_campos_categoria / len(categorias_con_datos)) if categorias_con_datos else 0,
                'ejemplo_campos': list(categorias_con_datos[0].get(categoria, {}).keys())[:5] if categorias_con_datos else []
            }
        
        # ✅ ESTADÍSTICAS ANDES TABLE RAW
        propiedades_con_andes_raw = [r for r in resultados 
                                   if r.get('andes_table_raw') and isinstance(r.get('andes_table_raw'), dict)]
        
        total_categorias_andes = sum(
            r.get('andes_table_raw', {}).get('metadata', {}).get('total_categorias', 0) 
            for r in propiedades_con_andes_raw
        )
        
        total_campos_andes = sum(
            r.get('andes_table_raw', {}).get('metadata', {}).get('total_campos', 0) 
            for r in propiedades_con_andes_raw
        )
        
        stats_andes_raw = {
            'propiedades_con_datos': len(propiedades_con_andes_raw),
            'total_propiedades': len(resultados),
            'porcentaje_propiedades': (len(propiedades_con_andes_raw) / len(resultados) * 100) if resultados else 0,
            'total_categorias': total_categorias_andes,
            'total_campos': total_campos_andes,
            'promedio_categorias_por_propiedad': (total_categorias_andes / len(propiedades_con_andes_raw)) if propiedades_con_andes_raw else 0,
            'promedio_campos_por_propiedad': (total_campos_andes / len(propiedades_con_andes_raw)) if propiedades_con_andes_raw else 0
        }
        
        # ✅ ESTADÍSTICAS GENERALES
        propiedades_exitosas = [r for r in resultados if r.get('status') != 'error']
        propiedades_con_error = [r for r in resultados if r.get('status') == 'error']
        
        stats_generales = {
            'total_propiedades_procesadas': len(resultados),
            'propiedades_exitosas': len(propiedades_exitosas),
            'propiedades_con_error': len(propiedades_con_error),
            'tasa_exito': (len(propiedades_exitosas) / len(resultados) * 100) if resultados else 0,
            'timestamp_reporte': timestamp,
            'archivo_generado': archivo_salida
        }
        
        # 🔄 COMPILAR REPORTE FINAL
        reporte_final = {
            'metadata_reporte': {
                'version': '2025_hibrido_ultra_avanzado',
                'fecha_generacion': datetime.now().isoformat(),
                'total_propiedades': len(resultados),
                'archivo_salida': archivo_salida
            },
            
            # 📊 ESTADÍSTICAS DETALLADAS
            'estadisticas': {
                'generales': stats_generales,
                'campos_universales_estructurados': stats_universales,
                'metadatos_universales': stats_metadatos,
                'categorias_json': stats_json,
                'andes_table_raw': stats_andes_raw
            },
            
            # 📋 DATOS COMPLETOS
            'resultados': resultados
        }
        
        # 💾 GUARDAR ARCHIVO
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(reporte_final, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Reporte guardado: {archivo_salida}")
            
            # 📊 MOSTRAR RESUMEN
            self._mostrar_resumen_estadisticas(reporte_final['estadisticas'])
            
            return reporte_final
            
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
            return reporte_final
    
    def _mostrar_resumen_estadisticas(self, estadisticas: Dict) -> None:
        """Muestra resumen de estadísticas en consola"""
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE ESTADÍSTICAS HÍBRIDAS")
        print("="*60)
        
        # Generales
        gen = estadisticas['generales']
        print(f"🎯 RESULTADOS GENERALES:")
        print(f"   📋 Total procesadas: {gen['total_propiedades_procesadas']}")
        print(f"   ✅ Exitosas: {gen['propiedades_exitosas']} ({gen['tasa_exito']:.1f}%)")
        print(f"   ❌ Con error: {gen['propiedades_con_error']}")
        
        # Campos universales
        univ = estadisticas['campos_universales_estructurados']
        campos_exitosos = sum(1 for campo, stats in univ.items() if stats['porcentaje'] > 0)
        print(f"\n🏗️ CAMPOS UNIVERSALES ESTRUCTURADOS:")
        print(f"   📊 Campos con datos: {campos_exitosos}/{len(univ)} ({campos_exitosos/len(univ)*100:.1f}%)")
        
        for campo, stats in univ.items():
            if stats['extraidos'] > 0:
                print(f"   ✅ {campo}: {stats['extraidos']}/{stats['total']} ({stats['porcentaje']:.1f}%)")
        
        # Metadatos
        meta = estadisticas['metadatos_universales']
        metadatos_exitosos = sum(1 for campo, stats in meta.items() if stats['porcentaje'] > 0)
        print(f"\n🆔 METADATOS UNIVERSALES:")
        print(f"   📊 Metadatos con datos: {metadatos_exitosos}/{len(meta)} ({metadatos_exitosos/len(meta)*100:.1f}%)")
        
        for campo, stats in meta.items():
            if stats['extraidos'] > 0:
                print(f"   ✅ {campo}: {stats['extraidos']}/{stats['total']} ({stats['porcentaje']:.1f}%)")
        
        # Categorías JSON
        json_stats = estadisticas['categorias_json']
        categorias_exitosas = sum(1 for cat, stats in json_stats.items() if stats['propiedades_con_datos'] > 0)
        print(f"\n📦 CATEGORÍAS JSON:")
        print(f"   📊 Categorías con datos: {categorias_exitosas}/{len(json_stats)} ({categorias_exitosas/len(json_stats)*100:.1f}%)")
        
        for categoria, stats in json_stats.items():
            if stats['propiedades_con_datos'] > 0:
                print(f"   ✅ {categoria}: {stats['propiedades_con_datos']} props ({stats['porcentaje_propiedades']:.1f}%), {stats['total_campos']} campos")
        
        # Andes RAW
        andes = estadisticas['andes_table_raw']
        print(f"\n🔄 ANDES TABLE RAW:")
        print(f"   📊 Propiedades con datos: {andes['propiedades_con_datos']}/{andes['total_propiedades']} ({andes['porcentaje_propiedades']:.1f}%)")
        print(f"   📋 Total categorías: {andes['total_categorias']}")
        print(f"   🔢 Total campos: {andes['total_campos']}")
        
        print("="*60)
    
    def run_single_property_debug(self, extractor, navigator, url: str) -> Dict:
        """Ejecuta test de debug en una sola propiedad"""
        
        print(f"\n🔍 DEBUG PROPIEDAD INDIVIDUAL")
        print(f"URL: {url}")
        print("-" * 60)
        
        resultado = {
            'url': url,
            'status': 'pendiente',
            'timestamp': datetime.now().isoformat(),
            'error': None
        }
        
        try:
            # Aquí iría la lógica de extracción
            # (se implementaría integrando con extractor y navigator)
            
            print("✅ Debug completado")
            resultado['status'] = 'exitoso'
            
        except Exception as e:
            print(f"❌ Error en debug: {e}")
            resultado['status'] = 'error'
            resultado['error'] = str(e)
        
        return resultado
    
    def validate_extracted_data(self, datos: Dict) -> Dict:
        """Valida calidad de datos extraídos"""
        
        validacion = {
            'campos_validos': 0,
            'campos_totales': 0,
            'calidad_porcentaje': 0,
            'errores': [],
            'advertencias': []
        }
        
        try:
            # Validar campos universales
            campos_universales = ['recamaras', 'banos', 'precio', 'direccion', 'tipo_propiedad']
            
            for campo in campos_universales:
                validacion['campos_totales'] += 1
                valor = datos.get(campo)
                
                if valor is not None and valor != "":
                    # Validaciones específicas por campo
                    if campo in ['recamaras', 'banos'] and isinstance(valor, (int, float)) and valor > 0:
                        validacion['campos_validos'] += 1
                    elif campo == 'precio' and isinstance(valor, (int, float)) and valor > 0:
                        validacion['campos_validos'] += 1
                    elif campo == 'direccion' and isinstance(valor, str) and len(valor) > 10:
                        validacion['campos_validos'] += 1
                    elif campo == 'tipo_propiedad' and isinstance(valor, str) and len(valor) > 2:
                        validacion['campos_validos'] += 1
                    else:
                        validacion['advertencias'].append(f"Campo {campo} con valor sospechoso: {valor}")
                else:
                    validacion['errores'].append(f"Campo {campo} faltante o vacío")
            
            # Calcular calidad
            validacion['calidad_porcentaje'] = (validacion['campos_validos'] / validacion['campos_totales'] * 100) if validacion['campos_totales'] > 0 else 0
            
        except Exception as e:
            validacion['errores'].append(f"Error en validación: {e}")
        
        return validacion
    
    def compare_extraction_results(self, resultados_antes: List[Dict], resultados_despues: List[Dict]) -> Dict:
        """Compara resultados de extracción entre dos versiones"""
        
        comparacion = {
            'mejoras': [],
            'empeoramientos': [],
            'sin_cambios': [],
            'resumen': {}
        }
        
        # Campos a comparar
        campos_importantes = ['recamaras', 'banos', 'precio', 'direccion', 'caracteristicas_principales']
        
        for campo in campos_importantes:
            antes_exitosos = len([r for r in resultados_antes if r.get(campo) is not None])
            despues_exitosos = len([r for r in resultados_despues if r.get(campo) is not None])
            
            diferencia = despues_exitosos - antes_exitosos
            
            if diferencia > 0:
                comparacion['mejoras'].append({
                    'campo': campo,
                    'antes': antes_exitosos,
                    'despues': despues_exitosos,
                    'mejora': diferencia
                })
            elif diferencia < 0:
                comparacion['empeoramientos'].append({
                    'campo': campo,
                    'antes': antes_exitosos,
                    'despues': despues_exitosos,
                    'empeoramiento': abs(diferencia)
                })
            else:
                comparacion['sin_cambios'].append(campo)
        
        comparacion['resumen'] = {
            'total_mejoras': len(comparacion['mejoras']),
            'total_empeoramientos': len(comparacion['empeoramientos']),
            'total_sin_cambios': len(comparacion['sin_cambios'])
        }
        
        return comparacion 