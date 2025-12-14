
## Team A Repository Overview (fa25-team-a)

This folder contains a Data Science class Project working code, data, notebooks, and documentation for the Allston Brighton CDC project on the `fa25-team-a-dev` branch. Below is the structure and how to use each section.

### Directory Structure
```bash
fa25-team-a/
├─ data/
│  ├─ raw/                 # Source files exactly as received
│  │  ├─ Allston Brighton CDC Affordable Housing Portfolio.docx
│  │  └─ Voter List - Ward 21 and 22.xls
│  ├─ processed/           # Cleaned and transformed outputs
│  │  ├─ geospatial_data/  # GeoJSON files for mapping
│  │  ├─ census_data/      # Census tract data and shapefiles
│  │  └─ [other processed datasets]
│  ├─ data_dictionary.md   # Column definitions and field-level notes
│  └─ temp.txt             # Scratch placeholder (safe to remove later)
├─ docs/
│  ├─ project_definition.md # Scope, goals, success criteria
│  ├─ research.md           # Background research and references
│  ├─ database_schema_documentation.md  # Database schema details
│  ├─ looker_studio_setup_guide.md      # Looker Studio integration guide
│  ├─ census_tracts_precincts_mapping.md  # Census mapping documentation
│  └─ database_inventory_and_dashboard_plan.md
├─ notebooks/
│  ├─ eda_voterList.ipynb   # Exploratory data analysis notebooks
│  ├─ database_analysis.ipynb  # Database analysis and address mapping
│  ├─ Income & Tracts Geo Visualization.ipynb
│  └─ address_outputs/     # Generated address mapping artifacts
├─ reports/
│  └─ figures/              # Saved plots/visuals for reports
├─ scripts/                 # Reproducible data tasks (ETL, cleaning, export)
│  ├─ data_extraction/      # Data extraction scripts
│  ├─ data_processing/     # Data cleaning and processing
│  ├─ mapping/              # Spatial mapping scripts
│  └─ scraping/             # Web scraping scripts
├─ web_app/                 # Flask web application and dashboard
│  ├─ app.py               # Main Flask application
│  ├─ routes/              # Route modules
│  ├─ templates/           # HTML templates
│  ├─ scripts/             # Data loading and export scripts
│  └─ looker_exports/      # CSV exports for Looker Studio
├─ requirements.txt         # Python dependencies for this workspace
└─ README.md                # You are here
```

### What to put where
- **data/raw**: Original, immutable datasets from the client or public sources. Do not edit files in place; add new versions to `processed`.
- **data/processed**: Outputs created by scripts or notebooks (cleaned tables, merged datasets, feature tables). Use deterministic file names and document provenance.
- **data/data_dictionary.md**: Keep an up-to-date schema: field names, types, allowed values, derivation rules, and known caveats.
- **docs/project_definition.md**: Problem statement, stakeholders, scope, deliverables, milestones, and acceptance criteria.
- **docs/research.md**: Notes and links from literature, policy docs, and prior work that inform assumptions or methods.
- **notebooks**: Iterative exploration and analysis. Name notebooks with a prefix like `topic_dataset.ipynb` / `topic_author.ipynb`. Commit only notebooks that run top-to-bottom without errors; keep heavy outputs cleared.
- **scripts**: Productionized tasks. Prefer small, composable scripts over monoliths. Each script should read from `data/raw` or `processed` and write to `processed` or `reports/figures`.
- **reports/figures**: Auto-generated visuals saved by notebooks or scripts. Use stable filenames where referenced by documents.

### Getting started
1. Create and activate a Python environment, then install dependencies:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
2. Place any new source files into `data/raw/` and register fields in `data/data_dictionary.md`.
3. Use `notebooks/` for EDA; when an analysis stabilizes, migrate logic into `scripts/` for repeatability.

### Workflow and Branching
- Always branch off from the latest `fa25-team-a-active` branch:
  ```bash
  git checkout fa25-team-a-active
  git pull origin fa25-team-a-active
  git checkout -b feat/short-description

- Keep commits **small**, **focused**, and use **clear, descriptive messages**.
- Push your branch and open a **Pull Request (PR)** into `fa25-team-a-dev` for review and integration.
- Avoid pushing directly to `fa25-team-a-dev` — it is a **protected branch**.
- Once reviewed and approved, your PR will be merged into `fa25-team-a-dev`.

  
### Dataset documentation
- Cross-team dataset documentation is maintained in the `dataset-documentation/` directory. Refer to `dataset-documentation/README.md` and `dataset-documentation/DATASETDOC-fa-25.md` for shared definitions, stewardship details, and standards that complement this team's `data/data_dictionary.md`.
- A team-specific dataset documentation file, `fa25-team-a/docs/DATASETDOC-fa-25.md`, is maintained in this repository. Once finalized, its contents should be merged into the main `dataset-documentation/` folder to keep project-wide records up to date.


### Reproducibility

This analysis is **fully reproducible** with proper setup. All analysis notebooks can be run independently to regenerate all results, datasets, and visualizations.

#### Prerequisites

1. **PostgreSQL Database with PostGIS Extension**
   - PostgreSQL 12+ required
   - PostGIS extension must be installed and enabled
   - Database name: `abcdc_spatial` (configurable via `.env`)

2. **Python Environment**
   - Python 3.9+ recommended
   - All dependencies listed in `requirements.txt` and `web_app/requirements.txt`

3. **Data Files**
   - Raw data files in `data/raw/` (voter list, property assessments, violations, etc.)
   - Processed geospatial data in `data/processed/geospatial_data/`
   - Census tract data in `data/processed/census_data/`

#### Setup Steps

1. **Install Dependencies**:
   ```bash
   # Main project dependencies
   pip install -r requirements.txt
   
   # Web app dependencies (includes database connection)
   cd web_app
   pip install -r requirements.txt
   cd ..
   ```

2. **Database Setup**:
   ```bash
   # Create PostgreSQL database with PostGIS
   createdb abcdc_spatial
   psql abcdc_spatial -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   
   # Load database schema
   psql abcdc_spatial -f web_app/config/complete_schema.sql
   ```

3. **Environment Configuration**:
   Create `web_app/.env` file:
   ```
   DB_HOST=localhost
   DB_NAME=abcdc_spatial
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_PORT=5432
   ```

4. **Load Data into Database**:
   ```bash
   cd web_app/scripts/data_loading
   
   # Load core data (run in order)
   python load_buildings_data.py
   python load_geocoded_voters.py
   python load_census_data.py
   python load_geospatial_layers.py
   python load_stores.py
   python find_nearby_stores.py
   python map_precincts_to_census_tracts.py
   ```

5. **Fix Notebook Paths**: Update hardcoded absolute paths in notebooks to use relative paths:
   ```python
   import os
   project_root = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
   sys.path.append(os.path.join(project_root, 'fa25-team-a', 'web_app'))
   ```
   Affected: `elderly_location_analysis.ipynb`, `elderly_housing_eligibility.ipynb`, `elderly_barriers_analysis.ipynb`, `elderly_tenure_analysis.ipynb`, `housing_market_impact_analysis.ipynb`

#### Running the Analysis

All analysis notebooks are self-contained and can be run independently:

1. **Question 1** (`elderly_location_analysis.ipynb`): Demographics and location analysis
2. **Question 2** (`elderly_housing_eligibility.ipynb`): Eligibility scoring and priority levels
3. **Question 3** (`elderly_barriers_analysis.ipynb`): Financial, housing condition, and violation barriers
4. **Question 4** (`elderly_tenure_analysis.ipynb`): Homeowner/renter status and residency
5. **Question 5** (`housing_market_impact_analysis.ipynb`): Market impact and outreach strategy

#### Expected Outputs

After running all notebooks, you should have:

- **Analysis Datasets**: All CSV files in `data/processed/elderly_analysis/` (46 files)
- **Submission Dataset**: Organized folder at `data/processed/submission_dataset/` (31 files)
- **Visualizations**: PNG files in `reports/figures/` (8 files)
- **Documentation**: Markdown files in `docs/` (question1.md through question5.md)

#### Verification

Verify setup by checking database counts:
```python
from web_app.config.database import execute_query
result = execute_query("SELECT COUNT(*) as count FROM voters WHERE is_elderly = true;", fetch_one=True)
# Should return: 7396
result = execute_query("SELECT COUNT(*) as count FROM voters_buildings_map;", fetch_one=True)
# Should return: ~30,832
```
Run each notebook from top to bottom and verify output files are generated.

#### Known Limitations

1. **Hardcoded Paths**: Notebooks use absolute paths that need to be updated for different environments (see Setup Step 5)
2. **Database Dependency**: All analysis requires a fully populated PostgreSQL database
3. **Large Files**: Some large data files (database exports, permits) are excluded from git due to size limits
4. **Data Timestamps**: Analysis uses 2020 voter data and 2025 property data - results are specific to this time period

#### Troubleshooting

- **Database Connection Errors**: Verify `.env` file exists and database is running
- **Import Errors**: Ensure `web_app` directory is in Python path (see path fix above)
- **Missing Data**: Run data loading scripts in order to populate database
- **PostGIS Errors**: Verify PostGIS extension is installed: `psql abcdc_spatial -c "SELECT PostGIS_version();"`

For detailed database setup, see `docs/database_schema_documentation.md`.

### Questions
If you're unsure where something belongs, default to `docs/` for narrative materials, `data/raw` for untouched inputs, and `scripts/` for repeatable transformations.

### Recent Work

**Comprehensive Elderly Housing Analysis (November 2025):**
- Completed analysis addressing 5 research questions (demographics, eligibility, barriers, tenure, market impact)
- Eligibility scoring system (0-100 points): 1,080 qualifying residents (15.5%) identified
- Key findings: 7,396 elderly residents (16.9% of voters), 150 homeowners in outreach pool ($163.3M property value)
- Generated LaTeX report (`reports/latex/Elderly_Housing_Analysis_Report.pdf`) and submission dataset (31 CSV files)
- Analysis notebooks: `elderly_location_analysis.ipynb`, `elderly_housing_eligibility.ipynb`, `elderly_barriers_analysis.ipynb`, `elderly_tenure_analysis.ipynb`, `housing_market_impact_analysis.ipynb`

**Data Infrastructure:**
- Voter→Building mapping: 72.9% coverage (5,391 of 7,396 elderly mapped), 30,832+ links with 100% accuracy
- Census tracts mapping: PostGIS spatial joins linking precincts to census tracts with income analysis
- Geocoding: 5,713 elderly voters (75.9%) with coordinates from building/parcel geometry and direct geocoding
- Store mapping: 55 stores mapped to 3,641 elderly voters using Haversine distance calculations

**Web Application & Integration:**
- Flask dashboard with GeoJSON API endpoints, census tract visualizations, and interactive maps
- Looker Studio integration: CSV exports and Cloud SQL PostgreSQL connection for real-time dashboards
- Database: PostgreSQL with PostGIS, 26MB exported to Google Cloud SQL

Where to look:
- Matching SQL and creation logic: `fa25-team-a/notebooks/database_analysis.ipynb` (cells creating and populating `voters_buildings_map`).
- Database schema: `fa25-team-a/docs/database_schema_documentation.md`.
- Census mapping: `fa25-team-a/docs/census_tracts_precincts_mapping.md`.
- Looker Studio setup: `fa25-team-a/docs/looker_studio_setup_guide.md`.
- Web application: `fa25-team-a/web_app/README.md`.
- Store data loading: `fa25-team-a/web_app/scripts/load_stores.py`.
- Store-voter mapping: `fa25-team-a/web_app/scripts/find_nearby_stores.py`.
