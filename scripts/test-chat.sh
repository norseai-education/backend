#!/bin/bash
# Test chat endpoints

STUDENT_ID=${1:-123}

echo "🧪 Testing Chat Endpoints"
echo "=========================="
echo "Student ID: $STUDENT_ID"
echo ""

# Test 1: Initialize chat
echo "1️⃣ Initializing chat session..."
INIT_RESPONSE=$(curl -s -X POST http://localhost:6700/chat/init/$STUDENT_ID)
echo "Response: $INIT_RESPONSE"
echo ""

# Test 2: Send a message
echo "2️⃣ Sending test message..."
MESSAGE='{"message": "Can you teach me about fractions?"}'
echo "Message: $MESSAGE"
echo ""
echo "Response:"
curl -s -X POST http://localhost:6700/chat/s/$STUDENT_ID \
  -H "Content-Type: application/json" \
  -d "$MESSAGE" \
  --no-buffer
echo ""
echo ""

# Test 3: Check status
echo "3️⃣ Checking chat status..."
STATUS_RESPONSE=$(curl -s http://localhost:6700/chat/status/$STUDENT_ID)
echo "Response: $STATUS_RESPONSE"
echo ""

echo "✅ Tests complete!"
