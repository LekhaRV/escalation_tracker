#!/bin/bash
# Install jq if needed (sudo apt-get install jq) but we will just grep if jq missing

echo "🔑 Logging in (JSON)..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@tarento.com", "password": "admin123"}' | grep -oP '"access_token":"\K[^"]+')

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed. Response:"
    curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@tarento.com", "password": "admin123"}'
    exit 1
fi

echo "✅ Token: ${TOKEN:0:10}..."

echo "📊 Fetching Analytics..."
RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/analytics?type=dashboard" \
     -H "Authorization: Bearer $TOKEN")

echo "🔍 Response Snippet:"
echo $RESPONSE | grep -o "daily_trends"
if [[ $RESPONSE == *"daily_trends"* ]]; then
    echo "✅ 'daily_trends' FOUND in response!"
else
    echo "❌ 'daily_trends' MISSING from response."
    echo "Full Response:"
    echo $RESPONSE
fi

echo "🔍 Response Snippet (Insights):"
if [[ $RESPONSE == *"recent_insights"* ]]; then
    echo "✅ 'recent_insights' FOUND in response!"
else
    echo "❌ 'recent_insights' MISSING from response."
fi
