# Google Maps Platform Python Samples

This directory contains executable, real-world Critical User Journey (CUJ) samples demonstrating how to integrate the `googlemaps` Python library into applications and data workflows.

## Quick Start

1. Set your Google Maps API key in your environment:
   ```bash
   export GOOGLE_MAPS_API_KEY="YOUR_API_KEY"
   ```

2. Run any of the sample scripts:
   ```bash
   python samples/real_estate_insights.py
   python samples/delivery_route_planner.py
   python samples/travel_discovery_assistant.py
   python samples/data_science_pandas_geocoding.py
   python samples/fleet_optimization_matrix.py
   python samples/infrastructure_elevation_snapping.py
   python samples/isochrone_reachability_cuj.py
   ```

*(Note: If no API key is provided, the samples display structured execution flows and gracefully handle demo execution).*

---

## Included Samples Overview

### 1. Real Estate & Location Intelligence (`real_estate_insights.py`)
- **CUJ:** A real estate portal evaluates a property address before listing.
- **APIs Used:** Address Validation API, Geocoding API, Places API (New), Air Quality API, Pollen API, Solar API.

### 2. Delivery & Logistics Route Planner (`delivery_route_planner.py`)
- **CUJ:** A logistics application plans delivery routes from a warehouse to multiple drop-off points.
- **APIs Used:** Routes API v2 (`computeRoutes`, `computeRouteMatrix`), Geocoding API.

### 3. Travel & Local Discovery Assistant (`travel_discovery_assistant.py`)
- **CUJ:** A consumer travel app assists users in discovering places, viewing rich photos/details, and getting directions.
- **APIs Used:** Places API (New) (`autocomplete`, `searchText`, `placeDetails`, `photoMedia`), Routes API v2 (`computeRoutes`).

### 4. Data Pipeline Integration & Pandas Export (`data_science_pandas_geocoding.py`)
- **CUJ:** A data engineer processes address streams into structured Pandas DataFrames for spatial analysis.
- **APIs Used:** Geocoding API, Address Validation API.

### 5. Fleet Routing & Solver Matrix Optimization (`fleet_optimization_matrix.py`)
- **CUJ:** A dispatch engine computes multi-hub distance/ETA matrices and formats them for mathematical solvers (e.g. OR-Tools / SciPy).
- **APIs Used:** Distance Matrix API, Routes API v2 (`computeRouteMatrix`).

### 6. Infrastructure & Environmental Analysis (`infrastructure_elevation_snapping.py`)
- **CUJ:** A telemetry platform snaps raw GPS breadcrumbs onto road geometries and queries elevation profiles.
- **APIs Used:** Roads API (`snapToRoads`), Elevation API (`elevation`, `elevationAlongPath`).

### 7. Isochrone Reachability & 15-Minute Urban Planning (`isochrone_reachability_cuj.py`)
- **CUJ:** An urban planning or retail analysis platform computes 15-minute reachability boundaries for transit/driving.
- **APIs Used:** Isochrones API (`generateIsochrones`), Places API (New).
