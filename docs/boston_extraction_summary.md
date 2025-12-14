# MassGIS Boston Data Extraction

## Why This Exists

The MassGIS website is terrible for downloading data.
This script extracts data directly from the statewide database,
filtered specifically for Boston/Allston-Brighton.

## Extracted Layers

### Boston Parcels
- Features: 98,964
- File: `parcels/boston_parcels.geojson`
- Source: L3_TAXPAR_POLY (from 2.2M statewide parcels)

### boston_parks_openspace
- Features: 1,099
- File: `boston_parks_openspace.geojson`

### boston_major_roads
- Features: 141
- File: `boston_major_roads.geojson`

## How to Use This Script for Other Towns

```python
# Change the town name:
town = get_town_boundary("CAMBRIDGE")  # or BROOKLINE, SOMERVILLE, etc.
parcels = extract_parcels_by_town(town, "CAMBRIDGE")
```

## Available Layers to Extract

The MassGIS Vector database has 662 layers including:
- Roads, streets, highways
- Parks, open space, conservation land
- Water bodies, wetlands
- Transit (MBTA lines, stations)
- Zoning districts
- Building footprints
- Census boundaries
- and 650+ more...

Use `extract_layer_by_town()` to get any layer you want!
