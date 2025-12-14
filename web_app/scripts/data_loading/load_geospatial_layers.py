#!/usr/bin/env python3
"""
Load GeoJSON layers (roads, precincts, boundary) into PostGIS tables.
Simple and explicit for your paths.
"""
import os
import json
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'abcdc_spatial'),
    'user': os.getenv('DB_USER', 'Studies'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432'),
}

GEO_DIR = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/geospatial_data'
ROADS = os.path.join(GEO_DIR, 'boston_major_roads.geojson')
PRECINCTS = os.path.join(GEO_DIR, 'allston_brighton_precincts.geojson')
BOUNDARY = os.path.join(GEO_DIR, 'allston_brighton_boundary.geojson')
PARKS = os.path.join(GEO_DIR, 'boston_parks_openspace.geojson')


def connect():
    return psycopg.connect(**DB_CONFIG)


def ensure_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS geo_roads (
                id SERIAL PRIMARY KEY,
                name TEXT,
                geom geometry(Geometry, 4326)
            );
        """)
        cur.execute("TRUNCATE geo_roads")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS geo_precincts (
                id SERIAL PRIMARY KEY,
                precinct TEXT,
                ward TEXT,
                geom geometry(Geometry, 4326)
            );
        """)
        cur.execute("TRUNCATE geo_precincts")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS geo_boundary (
                id SERIAL PRIMARY KEY,
                name TEXT,
                geom geometry(Geometry, 4326)
            );
        """)
        cur.execute("TRUNCATE geo_boundary")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS geo_parks (
                id SERIAL PRIMARY KEY,
                name TEXT,
                park_type TEXT,
                area_sqft DOUBLE PRECISION,
                geom geometry(Geometry, 4326)
            );
        """)
        cur.execute("TRUNCATE geo_parks")
    conn.commit()


def load_geojson_file(conn, path, table, name_fields=None):
    if not os.path.exists(path):
        print(f"Skipping {path} (not found)")
        return 0

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get('features', [])
    inserted = 0
    with conn.cursor() as cur:
        for feat in features:
            geom = feat.get('geometry')
            props = feat.get('properties') or {}
            if not geom:
                continue

            name_val = None
            if name_fields:
                for field in name_fields:
                    if field in props and props[field]:
                        name_val = str(props[field])
                        break

            geom_json = json.dumps(geom)

            if table == 'geo_roads':
                cur.execute(
                    "INSERT INTO geo_roads (name, geom) VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s),4326))",
                    [name_val, geom_json]
                )
            elif table == 'geo_precincts':
                precinct = str(props.get('PRECINCT') or props.get('precinct') or '')
                ward = str(props.get('WARD') or props.get('ward') or '')
                cur.execute(
                    "INSERT INTO geo_precincts (precinct, ward, geom) VALUES (%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s),4326))",
                    [precinct, ward, geom_json]
                )
            elif table == 'geo_boundary':
                cur.execute(
                    "INSERT INTO geo_boundary (name, geom) VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s),4326))",
                    [name_val or 'Allston-Brighton', geom_json]
                )
            elif table == 'geo_parks':
                park_name = props.get('NAME') or props.get('Name') or props.get('name')
                park_type = props.get('TYPE') or props.get('Type') or props.get('type')
                area = props.get('ACRES') or props.get('Shape_Area') or props.get('AREA_SQFT') or 0
                try:
                    # Some datasets have acres; convert to sqft
                    if 'ACRES' in props:
                        area = float(props['ACRES']) * 43560.0
                    else:
                        area = float(area)
                except Exception:
                    area = None
                cur.execute(
                    "INSERT INTO geo_parks (name, park_type, area_sqft, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s),4326))",
                    [park_name, park_type, area, geom_json]
                )
            inserted += 1
    conn.commit()
    print(f"Loaded {inserted} features into {table}")
    return inserted


def main():
    conn = connect()
    ensure_tables(conn)

    load_geojson_file(conn, ROADS, 'geo_roads', name_fields=['name', 'NAME', 'FULLNAME'])
    load_geojson_file(conn, PRECINCTS, 'geo_precincts')
    load_geojson_file(conn, BOUNDARY, 'geo_boundary', name_fields=['name', 'NAME'])
    load_geojson_file(conn, PARKS, 'geo_parks')

    conn.close()
    print("✅ Geospatial layers loaded.")


if __name__ == '__main__':
    main()


