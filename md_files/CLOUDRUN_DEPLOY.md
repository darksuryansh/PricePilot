# Google Cloud Run Deployment Guide

## Prerequisites
1. Google Cloud account
2. Google Cloud CLI installed
3. Docker installed locally (optional, for testing)

## Step-by-Step Deployment

### 1. Install Google Cloud CLI
Download from: https://cloud.google.com/sdk/docs/install

### 2. Initialize and Login
```bash
gcloud init
gcloud auth login
```

### 3. Set Your Project
```bash
# Create new project or use existing
gcloud projects create pricepilot-app --name="PricePilot"

# Set as active project
gcloud config set project pricepilot-app
```

### 4. Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 5. Build and Deploy to Cloud Run
```bash
# Navigate to your project directory
cd c:\pc\Price_tracker

# Deploy (this builds and deploys in one command)
gcloud run deploy pricepilot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "MONGODB_URI=your_mongodb_uri,GEMINI_API_KEY=your_gemini_key,SECRET_KEY=your_secret_key,GOOGLE_CLIENT_ID=your_google_client_id,RAPIDAPI_KEY=your_rapidapi_key"
```

**Replace environment variables with your actual values!**

### 6. Alternative: Deploy with Environment File
Create a `.env.yaml` file:
```yaml
MONGODB_URI: "mongodb+srv://..."
GEMINI_API_KEY: "AIzaSy..."
SECRET_KEY: "your-secret-key"
GOOGLE_CLIENT_ID: "your-client-id"
RAPIDAPI_KEY: "your-rapidapi-key"
```

Then deploy:
```bash
gcloud run deploy pricepilot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --env-vars-file .env.yaml
```

### 7. Get Your Service URL
After deployment completes, you'll get a URL like:
```
https://pricepilot-xxxxx-uc.a.run.app
```

### 8. Update Frontend Environment Variable
Update your Vercel environment variable:
- `VITE_API_BASE_URL` = `https://pricepilot-xxxxx-uc.a.run.app`

### 9. Test Your Deployment
```bash
# Health check
curl https://your-service-url.run.app/api/health

# Get products
curl https://your-service-url.run.app/api/products/recent
```

## Local Docker Testing (Optional)

### Build locally:
```bash
docker build -t pricepilot .
```

### Run locally:
```bash
docker run -p 8080:8080 \
  -e MONGODB_URI="your_uri" \
  -e GEMINI_API_KEY="your_key" \
  -e SECRET_KEY="your_secret" \
  pricepilot
```

### Test:
```bash
curl http://localhost:8080/api/health
```

## Cloud Run Advantages Over Render
- ✅ Better performance (Google infrastructure)
- ✅ No cold starts on free tier
- ✅ 2 million requests/month free
- ✅ 360,000 GB-seconds memory free
- ✅ 180,000 vCPU-seconds free
- ✅ Automatic HTTPS
- ✅ Custom domains free
- ✅ Better reliability
- ✅ Faster builds
- ✅ Native Docker support

## Monitoring
```bash
# View logs
gcloud run services logs read pricepilot --region us-central1

# View service details
gcloud run services describe pricepilot --region us-central1
```

## Update Deployment
```bash
# Redeploy after code changes
gcloud run deploy pricepilot --source .
```

## Cost Estimate
**Free Tier (Always Free):**
- 2 million requests/month
- 360,000 GB-seconds memory
- 180,000 vCPU-seconds

**Your app should stay FREE with normal usage!**

## Troubleshooting

### If deployment fails:
```bash
# Check build logs
gcloud builds list

# View specific build
gcloud builds log <BUILD_ID>
```

### If service crashes:
```bash
# Check logs
gcloud run services logs read pricepilot --limit 50
```

### Update environment variables:
```bash
gcloud run services update pricepilot \
  --set-env-vars "NEW_VAR=value"
```

## Delete Service (if needed)
```bash
gcloud run services delete pricepilot --region us-central1
```
