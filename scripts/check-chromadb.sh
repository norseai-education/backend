#!/bin/bash
# Check ChromaDB collections and data

echo "📊 ChromaDB Collections Status"
echo "==============================="
echo ""

# Get all collections
echo "📚 Collections:"
COLLECTIONS=$(curl -s "http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections")
echo "$COLLECTIONS" | python3 -m json.tool

echo ""
echo "📈 Collection Sizes:"

# Count items in each collection
for collection in "AMC8_math" "student_persona" "math_related" "AMC8_problems" "conversation_history"; do
    COUNT=$(curl -s "http://localhost:8000/api/v1/collections/$collection/count")
    echo "  $collection: $COUNT items"
done

echo ""
