# Cloud SQL Upload Guide - Using Cloud Console & Cloud Shell

## Step 1: Upload SQL File to Cloud Storage

### Via Cloud Console (3-dot menu method):

1. **Go to Google Cloud Console**
   - Navigate to [Cloud Storage](https://console.cloud.google.com/storage)
   - Create a bucket (if you don't have one):
     - Click "Create Bucket"
     - Name: `abcdc-database-backups` (or your choice)
     - Location: Same region as your Cloud SQL instance
     - Click "Create"

2. **Upload the SQL file**
   - Click on your bucket
   - Click "Upload Files" button
   - Select: `database_export_20251119_180829.sql` (from web_app directory)
   - Wait for upload to complete
   - Note the file path: `gs://YOUR_BUCKET_NAME/database_export_20251119_180829.sql`

---

## Step 2: Set Up Cloud SQL Instance (if not done)

1. **Go to Cloud SQL Console**
   - Navigate to [SQL](https://console.cloud.google.com/sql)
   - Click "Create Instance"
   - Choose "PostgreSQL"

2. **Configure Instance**
   - Instance ID: `abcdc-database`
   - Password: Set a strong password (save it!)
   - Database version: PostgreSQL 14 or 15
   - Region: Choose closest (e.g., `us-east1`)
   - Machine type: `db-f1-micro` (free tier) or `db-g1-small`
   - Storage: 20GB (minimum)
   - Click "Create"

3. **Create Database**
   - Go to your instance → "Databases" tab
   - Click "Create database"
   - Name: `abcdc_spatial`
   - Click "Create"

---

## Step 3: Import via Cloud Shell

1. **Open Cloud Shell**
   - In Cloud Console, click the Cloud Shell icon (top right)
   - Or go to: [Cloud Shell](https://shell.cloud.google.com)

2. **Download the SQL file to Cloud Shell** (if not using GCS)
   - Option A: If file is in Cloud Storage, it's already there
   - Option B: Upload via Cloud Shell upload button (folder icon in toolbar)

3. **Import to Cloud SQL**
   ```bash
   # Set your variables
   INSTANCE_NAME="abcdc-database"
   DATABASE_NAME="abcdc_spatial"
   SQL_FILE="database_export_20251119_180829.sql"
   BUCKET_NAME="YOUR_BUCKET_NAME"  # If using Cloud Storage
   
   # Method 1: Import from Cloud Storage (recommended)
   gcloud sql import sql $INSTANCE_NAME \
     gs://$BUCKET_NAME/$SQL_FILE \
     --database=$DATABASE_NAME
   
   # Method 2: If file is in Cloud Shell home directory
   # First, you need to upload to Cloud Storage:
   gsutil cp $SQL_FILE gs://$BUCKET_NAME/
   
   # Then import:
   gcloud sql import sql $INSTANCE_NAME \
     gs://$BUCKET_NAME/$SQL_FILE \
     --database=$DATABASE_NAME
   ```

4. **Wait for import to complete**
   - This may take 5-10 minutes for a 77MB file
   - Check status in Cloud SQL Console → Operations tab

---

## Step 4: Verify Import

In Cloud Shell, connect and verify:

```bash
# Connect to your Cloud SQL instance
gcloud sql connect $INSTANCE_NAME --user=postgres --database=$DATABASE_NAME

# Once connected, run:
\dt

# Check table counts
SELECT 
    'elderly_housing_conditions' as table_name, 
    COUNT(*) as row_count 
FROM elderly_housing_conditions
UNION ALL
SELECT 'elderly_permits_one_to_one', COUNT(*) FROM elderly_permits_one_to_one
UNION ALL
SELECT 'elderly_permits_one_to_one_summary', COUNT(*) FROM elderly_permits_one_to_one_summary
UNION ALL
SELECT 'elderly_violations_one_to_one', COUNT(*) FROM elderly_violations_one_to_one
UNION ALL
SELECT 'elderly_violations_one_to_one_summary', COUNT(*) FROM elderly_violations_one_to_one_summary;

# Exit
\q
```

---

## Alternative: Direct Upload via Cloud Shell

If you prefer to work entirely in Cloud Shell:

1. **Open Cloud Shell**

2. **Upload file via Cloud Shell UI**
   - Click the folder icon (Upload file) in Cloud Shell toolbar
   - Select `database_export_20251119_180829.sql`
   - File will be in your home directory

3. **Create Cloud Storage bucket** (if needed)
   ```bash
   gsutil mb gs://abcdc-database-backups
   ```

4. **Copy file to Cloud Storage**
   ```bash
   gsutil cp database_export_20251119_180829.sql gs://abcdc-database-backups/
   ```

5. **Import to Cloud SQL**
   ```bash
   gcloud sql import sql abcdc-database \
     gs://abcdc-database-backups/database_export_20251119_180829.sql \
     --database=abcdc_spatial
   ```

---

## Troubleshooting

### "Permission denied" error
- Make sure Cloud SQL Admin API is enabled
- Check your IAM permissions

### "File too large" error
- Cloud SQL import has limits, but 77MB should be fine
- If issues, try splitting the import or using Cloud SQL Proxy

### "Database does not exist" error
- Make sure you created the `abcdc_spatial` database first

### Import taking too long
- Normal for 77MB file - can take 10-15 minutes
- Check Operations tab in Cloud SQL Console for progress

---

## Next Steps After Import

1. **Enable PostGIS extension** (if not auto-enabled):
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

2. **Verify all tables loaded**:
   - Check row counts match your local database
   - Test a few queries

3. **Connect Looker Studio**:
   - Use Cloud SQL instance IP or connection name
   - Enable SSL
   - Test connection

