# Healthcare Triage and Provider Recommendation System - Web App

**Authors**: 

| Nombre           | Correo                           |
|------------------|-----------------------------------|
| Diana Varela    | dianacvarelaj@gmail.com           |
| Jhonattan Reales | jhonatanreales21@gmail.com       |

## Project Overview
"RutaSalud" is an interactive web application developed using **Streamlit** to assist users in navigating healthcare services in Colombia. The application provides a comprehensive triage system to assess the urgency of medical conditions and recommends nearby healthcare providers based on the user's symptoms and location. This project aims to improve access to healthcare by offering personalized recommendations and route guidance.

## Key Features
- **Symptom-Based Triage**: Users can input their symptoms to receive a triage classification (T1-T5) based on urgency.
- **Provider Recommendation**: The system suggests healthcare providers tailored to the user's needs, considering specialty, urgency, and proximity.
- **Interactive Maps**: Visualize routes to recommended providers with interactive maps and external navigation links.
- **Dynamic Location Selection**: Automatically loads department and city options based on available provider data.
- **User-Friendly Interface**: Intuitive design with dynamic color-coded feedback for triage results.

## Tools and Technologies
- **Streamlit**: Framework for building interactive web applications.
- **Folium**: Library for creating interactive maps and visualizing routes.
- **Sentence-Transformers**: Used for semantic matching in the recommendation engine.
- **RapidFuzz**: Provides fuzzy matching as a fallback for service recommendations.
- **ArcGIS and Nominatim APIs**: Geocoding and reverse geocoding services to handle user and provider locations.
- **Pandas**: Data manipulation and preprocessing.
- **Caching**: Optimized performance with caching strategies for data and model loading.

## How It Works
1. **Triage Process**:
   - Users complete a form detailing their symptoms.
   - The system evaluates the input using a hierarchical decision tree to classify urgency (T1-T5).
2. **Recommendation Engine**:
   - Matches user needs with provider services using semantic similarity and rule-based filtering.
   - Filters providers by location and distance.
3. **Route Visualization**:
   - Displays an interactive map with the user's location, provider locations, and routes.
   - Includes external navigation links for turn-by-turn directions.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/JhonattanReales21/innovatec2_streamlit.git
   ```
2. Navigate to the project directory:
   ```bash
   cd innovatec2_streamlit
   ```
3. Create and activate a Python environment (e.g., Conda):
   ```bash
   conda create -n 'YOUR_ENV_NAME' python=3.11
   conda activate 'YOUR_ENV_NAME'
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Future Enhancements
- **Provider Availability**: Incorporate real-time data on provider availability and capacity.
- **Expanded Data Sources**: Transition to scalable data storage solutions (e.g., AWS S3).
- **Enhanced Routing**: Integrate traffic data for more accurate route estimations.
- **Multi-Language Support**: Add support for additional languages to improve accessibility.

## Acknowledgments
This project was developed as part of the Master’s program in Applied Artificial Intelligence of ICESI university. Special thanks to our tutors and peers for their guidance and feedback.