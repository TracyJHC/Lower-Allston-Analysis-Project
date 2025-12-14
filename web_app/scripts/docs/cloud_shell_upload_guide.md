# Cloud Shell Upload & Import Guide

## Step 1: Upload SQL File to Cloud Shell

### Method 1: Via Cloud Console (3-dot menu)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the **Cloud Shell** icon (terminal icon in top right)
3. In Cloud Shell, click the **3-dot menu** (⋮) → **Upload file**
4. Select: `database_export_20251119_180829.sql`
5. Wait for upload to complete

### Method 2: Direct upload via Cloud Shell
```bash
# In Cloud Shell, click "Upload file" button
# Or use gcloud storage if file is already in a bucket
```

## Step 2: Set Up Cloud SQL Instance (if not done)

### Via Console:
1. Go to **SQL** in Cloud Console
2. Click **Create Instance**
3. Choose **PostgreSQL**
4. Configure:
   - Instance ID: `abcdc-database`
   - Password: (set strong password - save it!)
   - Database version: PostgreSQL 14 or 15
   - Region: `us-east1` (or closest)
   - Machine type: `db-f1-micro` (free tier)
   - Storage: 20GB
5. Click **Create**

### Via Cloud Shell:
```bash
gcloud sql instances create abcdc-database \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-east1 \
  --root-password=YOUR_PASSWORD_HERE
```

## Step 3: Create Database

### Via Console:
1. Go to your SQL instance
2. Click **Databases** tab
3. Click **Create database**
4. Name: `abcdc_spatial`

### Via Cloud Shell:
```bash
gcloud sql databases create abcdc_spatial --instance=abcdc-database
```

## Step 4: Import Database in Cloud Shell

### Option A: Using Cloud SQL Proxy (Recommended)
```bash
# Download Cloud SQL Proxy
wget https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.linux.amd64 -O cloud-sql-proxy
chmod +x cloud-sql-proxy

# Get your connection name (from Cloud SQL Console)
CONNECTION_NAME="PROJECT_ID:REGION:INSTANCE_NAME"
# Example: my-project:us-east1:abcdc-database

# Start proxy in background
./cloud-sql-proxy $CONNECTION_NAME --port=5432 &

# Wait a few seconds for proxy to start
sleep 5

# Import database
export PGPASSWORD="YOUR_DB_PASSWORD"
psql -h 127.0.0.1 -p 5432 -U postgres -d abcdc_spatial -f database_export_20251119_180829.sql

# Stop proxy when done
pkill cloud-sql-proxy
```

### Option B: Upload to Cloud Storage and Import
```bash
# Create a bucket (if you don't have one)
gsutil mb gs://YOUR_BUCKET_NAME

# Upload SQL file to bucket
gsutil cp database_export_20251119_180829.sql gs://YOUR_BUCKET_NAME/

# Import from bucket
gcloud sql import sql abcdc-database \
  gs://YOUR_BUCKET_NAME/database_export_20251119_180829.sql \
  --database=abcdc_spatial
```

## Step 5: Verify Import

```bash
# Connect to database via proxy
./cloud-sql-proxy $CONNECTION_NAME --port=5432 &

# Check tables
psql -h 127.0.0.1 -p 5432 -U postgres -d abcdc_spatial -c "\dt"

# Check elderly analysis tables
psql -h 127.0.0.1 -p 5432 -U postgres -d abcdc_spatial -c "
SELECT 
    'elderly_housing_conditions' as table_name, COUNT(*) as row_count 
FROM elderly_housing_conditions
UNION ALL
SELECT 'elderly_permits_one_to_one', COUNT(*) FROM elderly_permits_one_to_one
UNION ALL
SELECT 'elderly_permits_one_to_one_summary', COUNT(*) FROM elderly_permits_one_to_one_summary
UNION ALL
SELECT 'elderly_violations_one_to_one', COUNT(*) FROM elderly_violations_one_to_one
UNION ALL
SELECT 'elderly_violations_one_to_one_summary', COUNT(*) FROM elderly_violations_one_to_one_summary;
"
```

## Step 6: Connect Looker Studio

1. Go to [Looker Studio](https://lookerstudio.google.com)
2. Create → Data Source → PostgreSQL
3. Enter connection details:
   - **Host**: Get from Cloud SQL Console (Public IP or use Cloud SQL Auth Proxy)
   - **Port**: 5432
   - **Database**: abcdc_spatial
   - **Username**: postgres
   - **Password**: Your Cloud SQL password
   - **SSL**: Enable

## Troubleshooting

### File too large for upload?
- Use Cloud Storage method instead
- Or split the import into smaller chunks

### Connection issues?
- Check firewall rules in Cloud SQL
- Verify instance is running
- Check connection name format

### Import errors?
- Check PostGIS extension is enabled
- Verify database exists
- Check file encoding (should be UTF-8)

