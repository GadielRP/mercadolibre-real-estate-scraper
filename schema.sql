-- schema.sql
-- Esquema Híbrido Optimizado: PostgreSQL + JSONB (implementado primero en SQLite)
-- 
-- FILOSOFÍA DEL DISEÑO:
-- 1. Campos UNIVERSALES → Columnas estructuradas (para consultas SQL eficientes)
-- 2. Campos VARIABLES → JSON (para flexibilidad total)
-- 3. Compatibilidad SQLite → PostgreSQL (migración futura)

-- =============================================================================
-- TABLA PRINCIPAL: PROPIEDADES
-- =============================================================================

CREATE TABLE propiedades (
    -- ✅ IDENTIFICACIÓN UNIVERSAL
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ml_id TEXT UNIQUE,                               -- ID único de MercadoLibre
    url TEXT UNIQUE NOT NULL,
    titulo TEXT NOT NULL DEFAULT 'Sin título',
    descripcion TEXT DEFAULT '',                     -- Descripción completa de la propiedad
    
    
    -- ✅ CAMPOS COMERCIALES UNIVERSALES (siempre presentes, altamente consultados)
    precio DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    moneda TEXT CHECK(moneda IN ('MXN', 'USD')) NOT NULL DEFAULT 'MXN',
    tipo_operacion TEXT CHECK(tipo_operacion IN ('venta', 'renta')) NOT NULL DEFAULT 'venta',
    tipo_propiedad TEXT CHECK(tipo_propiedad IN ('casa', 'departamento', 'terreno', 'local', 'oficina')) NOT NULL DEFAULT 'casa',
    
    -- ✅ UBICACIÓN ESTRUCTURADA UNIVERSAL (altamente consultada)
    pais TEXT NOT NULL DEFAULT 'México',
    estado TEXT NOT NULL DEFAULT 'No especificado',
    ciudad TEXT NOT NULL DEFAULT 'No especificada',
    direccion_completa TEXT DEFAULT '',              -- Dirección raw completa
    
    -- ✅ CARACTERÍSTICAS FÍSICAS UNIVERSALES (siempre presentes)
    superficie_total DECIMAL(10,2) NOT NULL DEFAULT 0.0,      -- Terreno/total
    superficie_construida DECIMAL(10,2) NOT NULL DEFAULT 0.0,  -- Construcción
    recamaras INTEGER NOT NULL DEFAULT 0,
    banos DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    estacionamiento INTEGER NOT NULL DEFAULT 0,
    
    -- 🔄 CARACTERÍSTICAS VARIABLES (JSON - máxima flexibilidad)
    caracteristicas_principales JSON,                -- Antigüedad, orientación, mantenimiento, etc.
    servicios JSON,                                  -- Internet, A/C, gas, cisterna, etc.
    ambientes JSON,                                  -- Alberca, jardín, terraza, jacuzzi, etc.
    seguridad JSON,                                  -- Alarma, seguridad, portón eléctrico, etc.
    comodidades JSON,                                -- Gimnasio, área de juegos, etc.
    
    -- ✅ METADATOS DEL SISTEMA
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    fuente TEXT DEFAULT 'mercadolibre',
    
    -- ✅ DATOS RAW COMPLETOS (backup completo)
    andes_table_raw JSON,                            -- Tabla andes completa como backup
    html_snapshot TEXT                               -- HTML snapshot para debugging (opcional)
);

-- =============================================================================
-- TABLA DE CONTACTO (estructura tradicional - campos conocidos)
-- =============================================================================

CREATE TABLE contactos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    propiedad_id INTEGER,
    tipo TEXT CHECK(tipo IN ('telefono', 'email', 'whatsapp')) NOT NULL,
    valor TEXT NOT NULL,
    nombre_contacto TEXT,
    tipo_vendedor TEXT CHECK(tipo_vendedor IN ('particular', 'agente', 'inmobiliaria')),
    FOREIGN KEY(propiedad_id) REFERENCES propiedades(id) ON DELETE CASCADE
);

-- =============================================================================
-- VISTAS ÚTILES PARA CONSULTAS
-- =============================================================================

-- Vista de propiedades activas
CREATE VIEW propiedades_activas AS
SELECT * FROM propiedades WHERE is_active = 1;

-- Vista de estadísticas por ciudad
CREATE VIEW estadisticas_por_ciudad AS
SELECT 
    ciudad,
    COUNT(*) as total_propiedades,
    AVG(precio) as precio_promedio,
    MIN(precio) as precio_minimo,
    MAX(precio) as precio_maximo,
    AVG(superficie_total) as superficie_promedio
FROM propiedades
WHERE is_active = 1
GROUP BY ciudad
ORDER BY total_propiedades DESC;

-- =============================================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================================================

-- Índices para campos estructurados (consultas frecuentes)
CREATE INDEX idx_propiedades_ml_id ON propiedades(ml_id);
CREATE INDEX idx_propiedades_precio ON propiedades(precio);
CREATE INDEX idx_propiedades_tipo_operacion ON propiedades(tipo_operacion);
CREATE INDEX idx_propiedades_ciudad ON propiedades(ciudad);
CREATE INDEX idx_propiedades_recamaras ON propiedades(recamaras);
CREATE INDEX idx_contactos_propiedad_id ON contactos(propiedad_id);