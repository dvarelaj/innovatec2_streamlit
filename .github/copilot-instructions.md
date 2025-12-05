# RutaSalud - Copilot Instructions

## Project Overview
**RutaSalud** is a Streamlit-based medical triage and healthcare facility routing application for Colombia. It guides users through symptom assessment (triage), determines urgency levels (T1-T5), and recommends nearby healthcare providers based on their location and condition.

## Architecture & Data Flow

### Core Components
1. **`app.py`**: Main orchestrator with 3-tab horizontal navigation (Inicio → Formulario → Mapa ubicación)
2. **`utils/input_data/triage_symptoms.py`**: Loads and queries hierarchical symptom data (Category → Symptom → Modifier) from Excel
3. **`utils/ui_blocks.py`**: Reusable UI form components (patient ID, symptom selection)
4. **`utils/ui_maps.py`**: Interactive Folium maps with marker clustering and location controls
5. **`utils/ui_geocode.py`**: Geocoding/reverse geocoding using ArcGIS API (preferred) and Nominatim
6. **`data/`**: Excel files containing triage decision trees (`triage_sintomas.xlsx`) and healthcare provider database (`prestadores_mapa.xlsx`)

### State Management Pattern
**Critical**: This app relies heavily on `st.session_state` for persistence across reruns. Key variables include:
- Patient identification: `identificacion_paciente`, `tipo_documento`, `numero_documento`, `sexo`, `departamento`, `ciudad`
- Triage selections: `selected_categoria`, `selected_sintoma`, `selected_modificador`
- Triage results: `decision_triage` (T1-T5), `decision_modalidad`, `decision_especialidad`
- Location: `ubicacion_usuario` (lat/lng dict), `coordinates_queried_ciudad`, `city_lat`, `city_lon`
- Completion flags: `form_inicio_completed`, `form_symptoms_completed`, `form_location_completed`, `triage_completed`
- Navigation: `current_tab_triage`

**Pattern**: Initialize all state variables at the top of `app.py` with `if "key" not in st.session_state`.

## Key Workflows

### Environment Setup
**Conda environment** with Python 3.11 (named `maestria`):
```bash
# Activate environment
conda activate maestria

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app.py
```

### Adding New Symptoms
1. Update `data/triage_sintomas.xlsx` (columns H-J for category/symptom/modifier, K for modalidad, N for triage level, R for specialty)
2. Module auto-reloads via `load_sintomas_from_excel()` - no code changes needed
3. Test with `get_triage_decision(categoria, sintoma, modificador)` in notebooks

### Geocoding Services
**Two parallel systems** (use ArcGIS by default):
- **ArcGIS** (public API, no key): `geocode_address_arcgis()`, `reverse_geocode_arcgis()` - more reliable
- **Nominatim (OpenStreetMap)**: `get_coordinates_co()`, `reverse_geocode()` - fallback

All geocoding functions are cached with `@st.cache_data(show_spinner=False)`.

## Project-Specific Conventions

### Text Normalization
**Always use `text_cleaning()` from `utils/general_utils.py`** when processing user input or Excel data:
- Converts to lowercase
- Removes accents/diacritics (e.g., "Médico" → "medico")
- Replaces spaces with underscores
- Example: `"Urgencias Médico General"` → `"urgencias_medico_general"`

Used for: provider service names (`servicio_prestador`), symptom matching, address parsing.

### Map Interaction Patterns
**Three location modes** (see `app.py` lines 181-243):
1. **"Selección manual"**: Click on map, detect via `last_clicked` comparison
2. **"Ubicación del dispositivo"**: Auto-center via `LocateControl`, detect via `map_output["center"]`
3. **"Escribir dirección"**: Text input → geocode → place marker

**Critical**: Prevent infinite reruns by comparing new coordinates with `last_processed_click` or `last_auto_location` before calling `st.rerun()`.

### Triage Decision Logic (app.py lines 114-125)
- T1/T2 → "Emergencia"
- T3 → "Urgencias"
- T4 → "Cita Prioritaria"
- T5 → "Cita Programada"

Stored in `st.session_state.decision` for display in fixed header.

### Provider Data Cleaning Pattern (notebooks/data_input.ipynb)
Standard preprocessing steps for `prestadores_mapa.xlsx`:
1. Lowercase and normalize column names with `text_cleaning()`
2. Remove null `prestador` values and blacklisted providers
3. Filter by `direccionamiento != 9`
4. Drop providers with missing/zero lat/lng
5. Apply `text_cleaning()` to `concepto_factura` → `servicio_prestador`
6. Filter to predefined service list (e.g., `urgencias_medico_general`, `consulta_ortopedista`)
7. Rename columns to standard format (`lat`, `lng`, `prioridad_recomendacion`)

## File Locations & Naming

### Data Files
- **Triage decisions**: `data/triage_sintomas.xlsx` (columns H=categoria, I=sintoma, J=modificador, K=modalidad, N=triage, R=especialidad)
- **Healthcare providers**: `data/prestadores_mapa.xlsx` (raw), `data/prestadores_urg.xlsx`
- **Department-city mapping**: Hardcoded in `utils/ui_data.py` as `DEPARTAMENTOS_CIUDADES`

### Style System
All styling centralized in `utils/ui_style.py`:
- Color palette constants: `PRIMARY_BLUE`, `SECONDARY_BLUE`, `LIGHT_BLUE`, `YELLOW_ACCENT`, etc.
- Call `general_style_orch()` once at app start to inject all CSS
- Buttons styled with rounded corners (15px), shadows, and hover scale effects

### Notebooks vs Production Code
- `notebooks/`: Exploratory analysis (e.g., `data_input.ipynb` for provider data cleaning, `maps_input_test.ipynb` for map prototyping)
- `utils/`: Production modules imported by `app.py`
- **Pattern**: Prototype in notebooks, extract functions to `utils/` when stable

## Integration Points

### External APIs
1. **ArcGIS Geocoding** (no authentication):
   - Endpoint: `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/`
   - Always append `, Colombia` to search queries for relevance
2. **Nominatim** (requires `user_agent`):
   - Set to `"triage_app_geocode"` or `"triage_app_geocode_reverse"`
   - Retry logic: 3 attempts with 2-second delays

### Map Libraries
- **Folium**: Base mapping with tile layers (OpenStreetMap, ArcGIS World Topo, World Imagery)
- **streamlit-folium**: Embedding via `st_folium()` - returns dict with `last_clicked`, `center`, `bounds`
- **Plugins**: `MarkerCluster` (city markers), `LocateControl` (GPS), `Fullscreen`

## Common Pitfalls

1. **Forgetting to initialize state**: Always check `if "key" not in st.session_state` before first use
2. **Geocoding loops**: Cache results and use location keys (`f"{lat:.6f}_{lon:.6f}"`) to prevent redundant API calls
3. **Map rerun storms**: Only call `st.rerun()` when location coordinates actually change (see lines 202-210 in `app.py`)
4. **Excel column indexing**: Triage file uses 0-based indices (column H = index 7); verify with `data/triage_sintomas.xlsx` structure
5. **Text matching**: Always use `text_cleaning()` on both sides of comparisons when matching provider services or symptoms

## Testing Approach

- **Manual testing via notebooks**: Use `data_input.ipynb` to validate data loading and geocoding functions
- **No automated tests**: Project lacks pytest/unit test infrastructure (planned for future)
- **Debug pattern**: Add `st.write(st.session_state)` to inspect state during development

## Future Development Notes

### Provider Recommendation System (Next Priority)
- **Current state**: Stubbed out in `app.py` (lines 336-355)
- **Goal**: Match users to healthcare providers based on triage results and symptoms
- **Implementation plan**:
  - Calculate distances from `ubicacion_usuario` to provider coordinates
  - Filter by `decision_especialidad` from triage
  - Rank by `prioridad_recomendacion` (direccionamiento field)
  - Consider moving logic to new `utils/provider_matcher.py` module

### Data Source Migration (Future Architecture)
**Current**: Local Excel files (`data/*.xlsx`)  
**Planned transition**:
1. **Short-term**: SharePoint shared documents (enables team collaboration)
2. **Long-term**: AWS S3 bucket (production-ready, scalable)

**Migration considerations**:
- Abstract data loading behind interface in `utils/input_data/`
- Add configuration for data source selection (local/SharePoint/S3)
- Implement caching strategy for remote data sources
- Consider using `pandas.read_excel()` with URLs or boto3 for S3
