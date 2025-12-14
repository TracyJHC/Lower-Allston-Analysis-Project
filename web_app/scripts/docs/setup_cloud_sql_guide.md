# Google Cloud SQL Setup Guide for Looker Studio

## Step 1: Get Google Cloud Account (Student Benefits)

### Option A: GitHub Student Developer Pack
1. Go to [GitHub Education](https://education.github.com/pack)
2. Sign up with your student email
3. Get $200 in Google Cloud credits

### Option B: Google Cloud Free Tier
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Sign up with your Google account
3. Get $300 free credits (valid for 90 days)
4. Free tier includes some Cloud SQL usage

### Option C: Google Cloud for Education
- Check if your school participates
- May have additional credits

---

## Step 2: Enable Required APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select or create a project
3. Enable these APIs:
   - Cloud SQL Admin API
   - Compute Engine API (if needed)

```bash
# Or use gcloud CLI:
gcloud services enable sqladmin.googleapis.com
```

---

## Step 3: Create Cloud SQL PostgreSQL Instance

### Via Console:
1. Go to **SQL** in Google Cloud Console
2. Click **Create Instance**
3. Choose **PostgreSQL**
4. Configure:
   - **Instance ID**: `abcdc-database`
   - **Password**: (set a strong password - save it!)
   - **Database version**: PostgreSQL 14 or 15
   - **Region**: Choose closest to you (e.g., `us-east1`)
   - **Machine type**: `db-f1-micro` (free tier) or `db-g1-small` (smallest paid)
   - **Storage**: 10GB (minimum)
   - **Backup**: Enable (recommended)
5. Click **Create**

### Via gcloud CLI:
```bash
gcloud sql instances create abcdc-database \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-east1 \
  --root-password=YOUR_PASSWORD_HERE
```

**Important**: Save your instance connection name and password!

---

## Step 4: Create Database

```bash
gcloud sql databases create abcdc_spatial --instance=abcdc-database
```

Or via Console:
1. Go to your SQL instance
2. Click **Databases** tab
3. Click **Create database**
4. Name: `abcdc_spatial`

---

## Step 5: Export Local Database

Run the export script (see `export_database_for_cloud_sql.sh`)

---

## Step 6: Import to Cloud SQL

### Option A: Using Cloud SQL Proxy (Recommended)
```bash
# Download Cloud SQL Proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.arm64
chmod +x cloud-sql-proxy

# Start proxy in background
./cloud-sql-proxy PROJECT_ID:REGION:INSTANCE_NAME &

# Import using psql
psql -h 127.0.0.1 -U postgres -d abcdc_spatial -f database_export.sql
```

### Option B: Direct Import via gcloud
```bash
gcloud sql import sql abcdc-database \
  gs://YOUR_BUCKET_NAME/database_export.sql \
  --database=abcdc_spatial
```

---

## Step 7: Configure Looker Studio Connection

1. Go to [Looker Studio](https://lookerstudio.google.com)
2. Click **Create** → **Data Source**
3. Search for **PostgreSQL**
4. Enter connection details:
   - **Host**: `YOUR_INSTANCE_IP` (from Cloud SQL console)
   - **Port**: `5432`
   - **Database**: `abcdc_spatial`
   - **Username**: `postgres`
   - **Password**: (your Cloud SQL password)
   - **SSL**: Enable (required)
5. Click **Connect**
6. Select tables to use
7. Click **Create Report**

---

## Cost Estimate

- **db-f1-micro**: ~$7-10/month (or free tier eligible)
- **Storage**: ~$0.17/GB/month
- **Total**: ~$10-15/month for small instance

With student credits, this should be free for several months!

---

## Troubleshooting

### Connection Issues
- Check firewall rules (allow your IP)
- Verify SSL is enabled
- Check instance is running

### Import Issues
- Ensure database exists
- Check file size limits
- Verify PostGIS extension is enabled

---

## Next Steps

After setup, you can:
1. Connect Looker Studio to your Cloud SQL instance
2. Create dashboards with live data
3. Set up scheduled refreshes
4. Share dashboards with your team

