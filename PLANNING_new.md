# Dirección y Arquitectura - Sistema de Scraping Inmobiliario MercadoLibre

## 🎯 **Dirección de Alto Nivel**

### **Visión del Proyecto**
Sistema de scraping masivo especializado en inmuebles de MercadoLibre México, diseñado con arquitectura modular híbrida para automatización completa del proceso de recolección de datos inmobiliarios hacia base de datos estructurada para análisis de mercado.

### **Scope y Objetivos**
- **Alcance Principal**: Automatización escalable de extracción de datos inmobiliarios
- **Objetivo Estratégico**: Plataforma de business intelligence para análisis de mercado inmobiliario
- **Capacidades Objetivo**: Procesamiento masivo, análisis predictivo, monitoreo temporal
- **Escalabilidad**: Nivel nacional con expansión a múltiples portales

### **Principios de Diseño**
- **Modularidad**: Componentes independientes y especializados
- **Escalabilidad**: Arquitectura preparada para crecimiento horizontal y vertical
- **Robustez**: Sistema antibloqueo multicapa y recuperación automática
- **Flexibilidad**: Estructura híbrida SQL + NoSQL para adaptabilidad

---

## 🏗️ **Arquitectura del Sistema**

### **Diseño Modular (4 Componentes Principales)**

```
┌─────────────────────────────────────────────────────────┐
│                ORQUESTADOR PRINCIPAL                     │
│         scraper_masivo_cuernavaca.py                    │
│                                                         │
│  • Coordinación del proceso completo                    │
│  • Gestión de estadísticas y estado                     │
│  • Control de errores y recuperación                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ├─────── CONFIGURACIÓN ──────┐
                  │                            │
┌─────────────────▼───────────────────┐        │  ┌──────────────▼──────────────┐
│         NAVEGACIÓN STEALTH          │        │  │      MODELOS Y CONFIG        │
│          navigation.py              │        │  │        models.py             │
│                                     │        │  │                             │
│  • Sistema antibloqueo multicapa    │        │  │  • Configuraciones centrales│
│  • Session management automático    │        │  │  • Estructuras de datos     │
│  • Rate limiting inteligente        │        │  │  • Parámetros del sistema   │
│  • Circuit breaker protection       │        │  │  • User agents y viewports  │
└─────────────────┬───────────────────┘        │  └─────────────────────────────┘
                  │                            │
┌─────────────────▼───────────────────┐        │  ┌──────────────▼──────────────┐
│      EXTRACCIÓN HÍBRIDA             │        │  │      TESTING Y ANÁLISIS      │
│        extractors.py                │        │  │       test_runner.py         │
│                                     │        │  │                             │
│  • Campos universales estructurados │        │  │  • Reportes estadísticos    │
│  • Categorías dinámicas JSON        │        │  │  • Validación de calidad    │
│  • Parsing inteligente ubicaciones  │        │  │  • Análisis comparativo     │
│  • Normalización automática         │        │  │  • Exportación estructurada │
└─────────────────────────────────────┘        │  └─────────────────────────────┘
                                               │
                                               └── COMPARTIDO POR TODOS
```

### **Flujo Arquitectural**

```
Inicio → Configuración Browser Stealth → Session Warming → Extracción URLs
    ↓
Procesamiento Masivo ← Circuit Breaker ← Rate Limiting ← Session Rotation
    ↓
Extracción Híbrida → Validación → Normalización → Almacenamiento → Reportes
```

### **Patrones Arquitecturales**
- **Separación de Responsabilidades**: Un propósito específico por módulo
- **Dependency Injection**: Configuración centralizada en models.py
- **Circuit Breaker**: Protección automática contra fallos
- **Strategy Pattern**: Múltiples estrategias de extracción según disponibilidad

---

## 💻 **Stack Tecnológico**

### **Core Framework**
- **Python 3.8+**: Lenguaje principal con soporte asyncio
- **Playwright**: Automatización browser con JavaScript completo y stealth
- **Pydantic**: Validación y modelado de datos con type hints
- **Polars**: Manipulación de datasets de alto rendimiento

### **Persistencia y Base de Datos**
- **PostgreSQL**: Base de datos principal con soporte JSON nativo
- **SQLAlchemy**: ORM asíncrono para operaciones complejas
- **asyncpg**: Driver nativo optimizado para PostgreSQL

### **Arquitectura de Datos**
- **Híbrido SQL + NoSQL**: Campos estructurados + categorías dinámicas JSON
- **Normalización Automática**: Parsing inteligente de ubicaciones y metadatos
- **Backup Completo**: Raw data preservado para análisis posterior

### **Testing y Calidad**
- **Pytest**: Framework de testing unitario e integración
- **Type Hints**: Tipado estático completo con mypy
- **Black**: Formateo automático de código
- **Logging**: Sistema robusto para debugging y monitoreo

---

## 🛡️ **Sistema Antibloqueo Multicapa**

### **Arquitectura de Evasión**

**Capa 1: Browser Stealth**
- User agents rotativos actualizados (2025)
- Configuraciones desktop específicas
- Headers HTTP realistas y dinámicos
- JavaScript bypass injection automático

**Capa 2: Comportamiento Humano**
- Patterns de navegación graduales realistas
- Delays variables humanizados (1-6 segundos)
- Session warming con entrada natural
- Scroll patterns y popup handling automático

**Capa 3: Session Management**
- Rotación automática cada 15-25 requests
- Circuit breaker para protección de fallos
- Rate limiting inteligente (8 RPM máximo)
- Health monitoring continuo de páginas

**Capa 4: Detección y Recuperación**
- Pattern detection de bloqueos en tiempo real
- Cooldown automático ante detección
- Reset de estadísticas por sesión nueva
- Logging completo para debugging avanzado

---

## 📊 **Arquitectura de Datos Híbrida**

### **Modelo de Datos Optimizado**

```python
# CAMPOS UNIVERSALES ESTRUCTURADOS (SQL optimizado)
{
    # Características Físicas
    "recamaras": int,
    "banos": float,
    "construccion": float,  # m²
    "terreno": float,       # m²
    "estacionamiento": int,
    
    # Información Comercial
    "precio": float,
    "moneda": str,
    "tipo_propiedad": str,
    "tipo_operacion": str,
    
    # Ubicación Normalizada
    "direccion": str,
    "estado": str,
    "ciudad": str,
    
    # Metadatos del Sistema
    "ml_id": str,
    "titulo": str,
    "descripcion": str,
    
    # CATEGORÍAS DINÁMICAS JSON (NoSQL flexible)
    "servicios": {"campo": "valor", ...},
    "ambientes": {"campo": "valor", ...},
    "seguridad": {"campo": "valor", ...},
    "comodidades": {"campo": "valor", ...},
    
    # BACKUP RAW COMPLETO
    "andes_table_raw": {...}
}
```

### **Ventajas del Diseño Híbrido**
1. **SQL Optimizado**: Campos universales para consultas rápidas y análisis
2. **NoSQL Flexibilidad**: JSON para datos variables por propiedad
3. **Escalabilidad**: Fácil agregar nuevos campos sin romper schema
4. **Backup Completo**: Raw data preservado para análisis posterior
5. **Normalización**: Parsing automático de ubicaciones y características

---

## ⚡ **Estrategias de Performance**

### **Optimizaciones de Velocidad**
- **Extracción Paralela**: Múltiples campos simultáneamente
- **Caching Inteligente**: Selectores DOM reutilizables
- **Session Reuse**: Reutilización de conexiones TCP
- **Memory Management**: Limpieza automática de contextos

### **Escalabilidad Horizontal**
- **Multi-threading**: Procesamiento paralelo de propiedades
- **Queue System**: Cola de requests para procesamiento masivo
- **Load Balancing**: Distribución entre múltiples instancias
- **Microservicios**: Arquitectura preparada para servicios distribuidos

### **Métricas de Performance Objetivo**
- **Velocidad**: 4-6 segundos por propiedad
- **Memoria**: < 500MB durante ejecución masiva
- **CPU**: < 30% utilización promedio
- **Escalabilidad**: 100+ propiedades por sesión sin degradación

---

## 🗄️ **Integración con Base de Datos**

### **Diseño de Schema**
```sql
-- Tabla principal con campos universales
CREATE TABLE propiedades (
    ml_id VARCHAR PRIMARY KEY,
    recamaras INTEGER,
    banos DECIMAL(3,1),
    precio DECIMAL(12,2),
    estado VARCHAR(50),
    ciudad VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla para categorías dinámicas JSON
CREATE TABLE categorias_json (
    ml_id VARCHAR REFERENCES propiedades(ml_id),
    categoria VARCHAR(50),
    datos JSONB,
    PRIMARY KEY (ml_id, categoria)
);

-- Tabla de metadatos y control
CREATE TABLE metadata_scraping (
    ml_id VARCHAR REFERENCES propiedades(ml_id),
    version_sistema VARCHAR(20),
    timestamp_scraping TIMESTAMP,
    raw_data JSONB
);
```

### **Estrategias de Inserción**
- **Batch Processing**: Inserción masiva para performance
- **Deduplicación**: Control automático por ML_ID
- **Validación Pre-inserción**: Verificación de integridad
- **Rollback Automático**: Recuperación ante errores

---

## 🚀 **Escalabilidad y Extensibilidad**

### **Puntos de Extensión Diseñados**

**Nuevas Fuentes de Datos:**
- Interfaz común en navigation.py para múltiples portales
- Configuración específica por sitio en models.py
- Extractores modulares especializados

**Nuevos Campos de Extracción:**
- Extensión natural de ResultadoPropiedad
- Agregado automático al pipeline híbrido
- Actualización automática de reportes

**Nuevas Capacidades de Análisis:**
- Plugin system para nuevos tipos de análisis
- API extensible para consultas personalizadas
- Machine Learning integrable para predicciones

### **Arquitectura Futura (Microservicios)**
```
Scraping Service (Actual) → Processing Service → Storage Service
                                      ↓
Analytics Service ← API Gateway ← Monitoring Service
```

---

## 📋 **Principios de Desarrollo**

### **Convenciones de Código**
- **Modularidad**: Máximo 500 líneas por archivo
- **Tipado Estático**: Type hints en todas las funciones
- **Documentación**: Google style docstrings
- **Testing**: Pytest para todas las funcionalidades críticas

### **Patrones de Error Handling**
- **Try-catch Específico**: Por tipo de error esperado
- **Logging Estructurado**: Niveles apropiados con contexto
- **Recuperación Automática**: Cuando sea técnicamente posible
- **Fallbacks**: Para funcionalidades críticas del sistema

### **Arquitectura de Testing**
- **Unit Tests**: Funciones de parsing y validación
- **Integration Tests**: Flujo completo end-to-end
- **Performance Tests**: Métricas de velocidad y memoria
- **Data Validation**: Verificación automática de calidad

---

## 🎯 **Evolución Arquitectural**

### **Fase Actual: Monolito Modular**
Sistema modular con 4 componentes especializados, optimizado para scraping masivo con extracción híbrida y persistencia en base de datos.

### **Fase Intermedia: Servicios Distribuidos**
- Separación en microservicios independientes
- Queue system para procesamiento asíncrono
- API Gateway para acceso unificado
- Monitoring y alertas automatizadas

### **Fase Avanzada: Plataforma de Análisis**
- Machine Learning integrado para predicciones
- Dashboard interactivo en tiempo real
- API pública para desarrolladores externos
- Integración con CRMs y herramientas empresariales

---

**Versión de Arquitectura**: v2.0 - Sistema Híbrido Modular  
**Estado**: Diseño Validado - Implementación en Producción  
**Próxima Evolución**: Integración de Persistencia y Analytics 