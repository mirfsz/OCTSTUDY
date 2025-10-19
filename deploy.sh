#!/bin/bash

# SPF Study Coach - Vercel Deployment Script

echo "🚀 Deploying SPF Study Coach to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "   npm i -g vercel"
    exit 1
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel. Please run:"
    echo "   vercel login"
    exit 1
fi

# Deploy to Vercel
echo "📦 Deploying application..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set up Vercel Postgres database in your Vercel dashboard"
echo "2. Add environment variables:"
echo "   - SECRET_KEY (generate a random string)"
echo "   - POSTGRES_HOST (from Vercel Postgres)"
echo "   - POSTGRES_DATABASE (from Vercel Postgres)"
echo "   - POSTGRES_USER (from Vercel Postgres)"
echo "   - POSTGRES_PASSWORD (from Vercel Postgres)"
echo "   - POSTGRES_PORT (5432)"
echo "3. The database will be automatically initialized on first visit"
echo ""
echo "🎉 Your SPF Study Coach is ready!"
