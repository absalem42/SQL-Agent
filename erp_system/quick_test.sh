#!/bin/bash

echo "🚀 Testing ERP AI System API..."

BASE_URL="http://localhost:8000"

echo ""
echo "1. Testing basic endpoints..."
echo "GET /"
curl -s $BASE_URL/ | jq 2>/dev/null || curl -s $BASE_URL/

echo ""
echo "GET /health"
curl -s $BASE_URL/health | jq 2>/dev/null || curl -s $BASE_URL/health

echo ""
echo "GET /customers"
curl -s $BASE_URL/customers | jq '. | length' 2>/dev/null || echo "No jq installed"

echo ""
echo "2. Testing router agent..."

echo ""
echo "Sales test:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"text":"show me customers"}' | jq -r '.response' 2>/dev/null || curl -s -X POST "$BASE_URL/chat" -H "Content-Type: application/json" -d '{"text":"show me customers"}'

echo ""
echo "Finance test:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"text":"what invoices do we have?"}' | jq -r '.response' 2>/dev/null || curl -s -X POST "$BASE_URL/chat" -H "Content-Type: application/json" -d '{"text":"what invoices do we have?"}'

echo ""
echo "✅ All tests completed!"