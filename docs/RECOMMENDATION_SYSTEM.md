# Sistema de Recomendación de Prestadores

## Descripción General

El sistema de recomendación de RutaSalud conecta los resultados del triage con prestadores de salud cercanos, utilizando matching semántico para sugerir servicios apropiados basándose en el nivel de urgencia y especialidad requerida.

## Arquitectura

### Flujo de Datos

```
Usuario completa triage
    ↓
[Triage Result: T1-T5, Especialidad]
    ↓
Build Correspondence Table (cached)
    - Load triage combinations from Excel
    - Load provider data (clean + merge)
    - Semantic matching (SBERT)
    ↓
Get Recommended Services
    - Filter by triage level
    - Match specialty
    ↓
Filter Providers
    - By recommended services
    - By location (dept + municipality)
    - Calculate distances (if GPS available)
    ↓
Display Top 5 Providers
    - Sorted by distance (if available)
    - Sorted by priority
```

### Módulos Clave

#### 1. `utils/triage_matching.py`
- `build_triage_combinations_from_excel()`: Carga y normaliza combinaciones de triage
- `build_correspondence_table()`: Construye tabla de correspondencia triage→servicios

**Pipeline de matching**:
1. Deduplica combinaciones clínicas
2. Filtra servicios por nivel de triage:
   - T1-T3 → `urgencias_*`
   - T4-T5 → `consulta_*`
   - T1 → + `cirugia_*`
3. Match de especialidad (semántico o fuzzy)
4. Fallback a servicios genéricos (`*_general`, `*_no_programada`)
5. Maneja casos sin coincidencias (urgencias o consulta medicina general)

#### 2. `utils/semantic_matching.py`
- `load_semantic_model()`: Carga modelo SBERT (cached con `@st.cache_resource`)
- `semantic_match_services()`: Calcula similitud coseno entre especialidad y servicios
- `fuzzy_match_services()`: Matching con RapidFuzz (fallback)

**Modelo usado**: `paraphrase-multilingual-MiniLM-L12-v2`
- Optimizado para español
- 384 dimensiones
- Rápido (CPU-friendly)

#### 3. `utils/recommendation_engine.py`
- `load_and_prepare_provider_data()`: Carga, limpia y fusiona datasets (cached)
- `build_triage_correspondence_table()`: Construye tabla completa (cached)
- `get_recommended_services()`: Obtiene servicios para un caso específico
- `filter_providers_by_service_and_location()`: Filtra y rankea prestadores

#### 4. `utils/input_data/providers_utils.py`
- `clean_providers_data()`: Pipeline de limpieza (8 pasos)
- `merge_provider_locations()`: Fusiona coordenadas con clave compuesta

## Uso en Streamlit

### Integración en `app.py`

```python
from utils.recommendation_engine import (
    build_triage_correspondence_table,
    get_recommended_services,
    filter_providers_by_service_and_location,
)

# Después de completar triage
if st.session_state.get("recommendation_step", False):
    # 1. Build correspondence table (cached)
    df_correspondencia = build_triage_correspondence_table(
        threshold=0.7,
        top_k=3,
        method="semantic"
    )
    
    # 2. Get recommended services
    recomendacion = get_recommended_services(
        nivel_triage=st.session_state.decision_triage,
        especialidad=st.session_state.decision_especialidad,
        df_correspondencia=df_correspondencia
    )
    
    # 3. Filter providers
    providers_filtered = filter_providers_by_service_and_location(
        df_prestadores=load_and_prepare_provider_data(),
        servicios=recomendacion["servicios"],
        departamento=st.session_state.departamento,
        municipio=st.session_state.ciudad,
        user_location=st.session_state.ubicacion_usuario,
        max_distance_km=50.0
    )
```

### Variables de Sesión

```python
# Input del usuario
st.session_state.decision_triage       # "T1", "T2", ..., "T5"
st.session_state.decision_especialidad # "ortopedia", "medicina_general", etc.
st.session_state.departamento          # "CUNDINAMARCA"
st.session_state.ciudad                # "BOGOTÁ"
st.session_state.ubicacion_usuario     # {"lat": 4.6097, "lng": -74.0817}

# Estado de recomendación
st.session_state.recommendation_step   # True cuando se activa
st.session_state.recommended_providers # DataFrame con prestadores filtrados
```

## Configuración

### Parámetros del Sistema

**Matching semántico** (`build_triage_correspondence_table()`):
- `threshold`: 0.7 (similitud mínima 0-1)
- `top_k`: 3 (máximo servicios sugeridos por caso)
- `method`: "semantic" o "fuzzy"

**Filtrado geográfico** (`filter_providers_by_service_and_location()`):
- `max_distance_km`: 50.0 (radio máximo desde ubicación usuario)

### Caching

**Importante**: Todas las operaciones pesadas usan caché de Streamlit:

```python
@st.cache_data(ttl=3600)  # 1 hora
def load_and_prepare_provider_data():
    # Evita recargar Excel en cada rerun
    pass

@st.cache_resource
def load_semantic_model():
    # Singleton: carga modelo UNA sola vez
    pass
```

**Invalidar caché**:
- Cambios en archivos Excel → reiniciar app
- Actualizar manualmente: botón "Clear cache" en menú Streamlit

## Data Sources

### Archivos Requeridos

1. **`data/triage_sintomas.xlsx`**
   - Columnas: H (categoria), I (sintoma), J (modificador), K (modalidad), N (triage), R (especialidad)
   - Usado por: `build_triage_combinations_from_excel()`

2. **`data/prestadores_mapa.xlsx`**
   - Dataset principal de prestadores
   - Usado por: `clean_providers_data()`

3. **`data/prestadores_urg.xlsx`**
   - Dataset con coordenadas actualizadas
   - Usado por: `merge_provider_locations()`

### Limpieza de Datos

Pipeline de `clean_providers_data()`:
1. Normalizar nombres de columnas (`text_cleaning`)
2. Filtrar valores null en `prestador`
3. Aplicar blacklist de prestadores
4. Filtrar `direccionamiento != 9`
5. Validar coordenadas (lat/lng no null ni cero)
6. Normalizar `concepto_factura` → `servicio_prestador`
7. Filtrar por lista de servicios permitidos
8. Renombrar columnas a formato estándar

## Troubleshooting

### Error: "No se encontraron prestadores"

**Causas posibles**:
1. No hay prestadores con el servicio en esa ciudad
2. Coordenadas inválidas (fuera del radio `max_distance_km`)
3. Servicio no está en la lista de servicios filtrados

**Solución**:
```python
# Verificar servicios disponibles en el dataset
df = load_and_prepare_provider_data()
print(df["servicio_prestador"].unique())

# Ampliar radio de búsqueda
filter_providers_by_service_and_location(
    ...,
    max_distance_km=100.0  # Aumentar de 50 a 100 km
)
```

### Error: "Model loading failed"

**Causa**: Modelo SBERT no descargado o caché corrupto

**Solución**:
```bash
# Reinstalar sentence-transformers
pip install --upgrade sentence-transformers

# Limpiar caché de Streamlit
rm -rf ~/.streamlit/cache
```

### Performance Lento

**Optimizaciones**:
1. Verificar que `@st.cache_data` y `@st.cache_resource` están activos
2. Reducir `top_k` (menos servicios por caso)
3. Usar método "fuzzy" en lugar de "semantic" (más rápido)
4. Pre-filtrar dataset de prestadores (solo ciudades principales)

## Extensiones Futuras

### 1. Sistema de Rating
- Añadir columna `rating` en `prestadores_mapa.xlsx`
- Integrar en ranking después de distancia/prioridad

### 2. Filtros Adicionales
- Por EPS/régimen
- Por horario de atención
- Por disponibilidad en tiempo real (API externa)

### 3. A/B Testing
- Comparar método "semantic" vs "fuzzy"
- Optimizar `threshold` según feedback de usuarios

### 4. Feedback Loop
- Guardar clicks en prestadores recomendados
- Reentrenar modelo con datos de uso real

## Referencias

- **SBERT**: [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084)
- **RapidFuzz**: [RapidFuzz Documentation](https://maxbachmann.github.io/RapidFuzz/)
- **Streamlit Caching**: [Caching Guide](https://docs.streamlit.io/library/advanced-features/caching)
