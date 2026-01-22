#!/bin/bash
# Deployment script for Google App Engine

echo "🚀 Starting deployment to Google App Engine..."

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations on Cloud SQL
echo "🗄️  Running database migrations..."
ENVIRONMENT=production python manage.py migrate --noinput

# Deploy to App Engine
echo "☁️  Deploying to App Engine..."
gcloud app deploy --quiet

echo "✅ Deployment complete!"
echo "🌐 Your API is live at: https://voicetrack-app.uc.r.appspot.com"
