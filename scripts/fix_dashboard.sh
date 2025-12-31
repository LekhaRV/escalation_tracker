#!/bin/bash
echo "🔧 Fixing Dashboard Data..."

echo "🌱 Seeding historical data (30 days)..."
docker exec tarento_backend python /app/scripts/super_seed.py

echo "🧠 Generating insights..."
docker exec tarento_backend python /app/scripts/run_insights.py

echo "✅ Done! Please refresh your dashboard."
