-- schema_mercadolibre.sql
--
-- Este diseño es robusto y flexible: las características adicionales (alberca, jardín, seguridad, amueblado, etc.)
-- se almacenan en la tabla 'caracteristicas' y se relacionan con las propiedades mediante la tabla many-to-many
-- 'propiedades_caracteristicas'. Esto permite agregar nuevas características sin modificar la tabla principal.
-- Además, los campos NOT NULL que provienen del scraping tienen valores por defecto para evitar errores si el scraping falla.

-- Tabla principal de propiedades
CREATE TABLE "propiedades" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identificación y Básicos (Obligatorios)
    "ml_id" TEXT UNIQUE,  -- ID de MercadoLibre
    "url" TEXT UNIQUE NOT NULL,
    "titulo" TEXT NOT NULL DEFAULT 'Sin título',
    "tipo_operacion" TEXT CHECK("tipo_operacion" IN ('venta', 'renta')) NOT NULL DEFAULT 'venta',
    "tipo_propiedad" TEXT CHECK("tipo_propiedad" IN ('casa', 'departamento', 'terreno', 'local', 'oficina')) NOT NULL DEFAULT 'casa',
    "precio" DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    "moneda" TEXT CHECK("moneda" IN ('MXN', 'USD')) NOT NULL DEFAULT 'MXN',
    "descripcion" TEXT DEFAULT '',
    
    -- Ubicación (Obligatorios)
    "pais" TEXT NOT NULL DEFAULT 'No especificado',
    "estado" TEXT NOT NULL DEFAULT 'No especificado',
    "ciudad" TEXT NOT NULL DEFAULT 'No especificada',
    "colonia" TEXT NOT NULL DEFAULT 'No especificada',
    "codigo_postal" TEXT NOT NULL DEFAULT '',
    
    -- Características Físicas (Obligatorios)
    "superficie" DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    "construccion" DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    "recamaras" INTEGER NOT NULL DEFAULT 0,
    "banos" DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    "estacionamiento" INTEGER NOT NULL DEFAULT 0,
    "ambientes" INTEGER NOT NULL DEFAULT 0,
    "pisos" INTEGER NOT NULL DEFAULT 1,
    "antiguedad" INTEGER NOT NULL DEFAULT 0,
    
    -- Metadatos del Sistema
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOLEAN DEFAULT 1,
    "fuente" TEXT DEFAULT 'mercadolibre',
    
    -- Metadatos de Extracción
    "calidad_extraccion" INTEGER DEFAULT 0,
    "last_scraped" TIMESTAMP,
    "error_extraccion" TEXT,
    "proxy_usado" TEXT
);

-- Tabla de características adicionales (similar a la estructura actual)
CREATE TABLE "caracteristicas" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre" TEXT NOT NULL UNIQUE,
    "categoria" TEXT CHECK("categoria" IN ('interior', 'exterior', 'servicios', 'seguridad', 'otros'))
);

CREATE TABLE "formas_de_pago" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "propiedad_id" INTEGER,
    "credito_infonavit" BOOLEAN,
    "credito_bancario" BOOLEAN,
    "recurso_propio" BOOLEAN,
    "descripcion" TEXT,
    FOREIGN KEY("propiedad_id") REFERENCES "propiedades"("id") ON DELETE CASCADE
);

CREATE TABLE "propiedades_caracteristicas" (
    "propiedad_id" INTEGER,
    "caracteristica_id" INTEGER,
    "detalles" TEXT DEFAULT '',
    "cantidad" INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY("propiedad_id", "caracteristica_id", "detalles"),
    FOREIGN KEY("propiedad_id") REFERENCES "propiedades"("id") ON DELETE CASCADE,
    FOREIGN KEY("caracteristica_id") REFERENCES "caracteristicas"("id") ON DELETE CASCADE
);

-- Tabla de contacto (similar a la estructura actual)
CREATE TABLE "contactos" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "propiedad_id" INTEGER,
    "tipo" TEXT CHECK("tipo" IN ('telefono', 'email', 'whatsapp')) NOT NULL,
    "valor" TEXT NOT NULL,
    "nombre_contacto" TEXT,
    "tipo_vendedor" TEXT CHECK("tipo_vendedor" IN ('particular', 'agente', 'inmobiliaria')),
    FOREIGN KEY("propiedad_id") REFERENCES "propiedades"("id") ON DELETE CASCADE
);

-- Vistas útiles
CREATE VIEW "propiedades_activas" AS
SELECT * FROM propiedades WHERE is_active = 1;

CREATE VIEW "propiedades_venta" AS
SELECT * FROM propiedades 
WHERE tipo_operacion = 'venta' AND is_active = 1;

CREATE VIEW "propiedades_renta" AS
SELECT * FROM propiedades 
WHERE tipo_operacion = 'renta' AND is_active = 1;

CREATE VIEW "propiedades_por_ciudad" AS
SELECT 
    ciudad,
    COUNT(*) as total_propiedades,
    AVG(precio) as precio_promedio,
    MIN(precio) as precio_minimo,
    MAX(precio) as precio_maximo
FROM propiedades
WHERE is_active = 1
GROUP BY ciudad
ORDER BY total_propiedades DESC;

CREATE VIEW "propiedades_con_caracteristicas" AS
SELECT
    p.id,
    p.titulo,
    p.precio,
    p.ciudad,
    c.nombre as caracteristica,
    pc.detalles,
    pc.cantidad
FROM propiedades p
JOIN propiedades_caracteristicas pc ON p.id = pc.propiedad_id
JOIN caracteristicas c ON c.id = pc.caracteristica_id
WHERE p.is_active = 1;

-- Índices para optimización
CREATE INDEX "idx_propiedades_ml_id" ON "propiedades"("ml_id");
CREATE INDEX "idx_propiedades_url" ON "propiedades"("url");
CREATE INDEX "idx_propiedades_tipo_operacion" ON "propiedades"("tipo_operacion");
CREATE INDEX "idx_propiedades_tipo_propiedad" ON "propiedades"("tipo_propiedad");
CREATE INDEX "idx_propiedades_pais" ON "propiedades"("pais");
CREATE INDEX "idx_propiedades_estado" ON "propiedades"("estado");
CREATE INDEX "idx_propiedades_ciudad" ON "propiedades"("ciudad");
CREATE INDEX "idx_propiedades_colonia" ON "propiedades"("colonia");
CREATE INDEX "idx_propiedades_precio" ON "propiedades"("precio");
CREATE INDEX "idx_propiedades_is_active" ON "propiedades"("is_active");
CREATE INDEX "idx_propiedades_last_scraped" ON "propiedades"("last_scraped");

-- Índices para tablas relacionadas
CREATE INDEX "idx_propiedades_caracteristicas_propiedad_id" ON "propiedades_caracteristicas"("propiedad_id");
CREATE INDEX "idx_propiedades_caracteristicas_caracteristica_id" ON "propiedades_caracteristicas"("caracteristica_id");
CREATE INDEX "idx_caracteristicas_nombre" ON "caracteristicas"("nombre");
CREATE INDEX "idx_contactos_propiedad_id" ON "contactos"("propiedad_id");
CREATE INDEX "idx_historico_precios_propiedad_id" ON "historico_precios"("propiedad_id");
CREATE INDEX "idx_extracciones_log_propiedad_id" ON "extracciones_log"("propiedad_id");