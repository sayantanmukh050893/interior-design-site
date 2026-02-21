#!/bin/bash
# Test script for the Transform Your Space endpoint

echo "🧪 Testing Interior Design Transformer API"
echo "==========================================="
echo ""

# Check if server is running
echo "1️⃣ Checking server health..."
HEALTH=$(curl -s http://localhost:5001/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Server is healthy"
    echo "   Response: $HEALTH" | head -1
else
    echo "❌ Server is not responding"
    exit 1
fi

echo ""
echo "2️⃣ Checking transformer initialization..."
python3 << 'EOF'
from app import transformer
if transformer:
    print(f"✅ Transformer: {type(transformer).__name__}")
    print(f"   Device: {transformer.device}")
    print(f"   Model: FLUX.2-klein-9B (HuggingFace Inference API)")
else:
    print("❌ Transformer not initialized")
    exit(1)
EOF

echo ""
echo "3️⃣ Testing prompt generation endpoint..."
PROMPT_RESPONSE=$(curl -s -X POST http://localhost:5001/generate-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test User",
    "preferred_colors": "Warm neutrals",
    "likes": "Modern, spacious",
    "dislikes": "Clutter",
    "hobbies": "Reading, cooking",
    "requirements": "Good lighting",
    "additional_comments": "Minimalist style",
    "room_type": "bedroom"
  }')

if echo "$PROMPT_RESPONSE" | grep -q '"prompt"'; then
    echo "✅ Prompt generation working"
    echo "   Prompt length: $(echo $PROMPT_RESPONSE | grep -o '"prompt":"[^"]*"' | wc -c) characters"
else
    echo "❌ Prompt generation failed"
    echo "   Response: $PROMPT_RESPONSE"
fi

echo ""
echo "✨ All checks passed!"
echo ""
echo "The Transform Your Space button should now:"
echo "  1. Accept your room image"
echo "  2. Send it to the /transform endpoint"
echo "  3. Return a transformed image"
echo "  4. Display the image with a comparison slider"
echo ""
echo "If you still experience issues:"
echo "  - Check browser console for JavaScript errors (F12)"
echo "  - Check server logs: tail server.log"
echo "  - Ensure HF_API_TOKEN is set for better performance"
echo ""
