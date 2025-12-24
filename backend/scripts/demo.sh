#!/bin/bash
# PCG Arena Stage 0 Demo Script
# Protocol: arena/v0
#
# This script demonstrates the complete battle/vote flow:
# 1. Creates a session
# 2. Fetches 10 battles
# 3. Submits votes for each battle
# 4. Shows leaderboard changes
#
# Usage: ./demo.sh [API_URL]
#   API_URL defaults to http://localhost:8080

set -e

API_URL="${1:-http://localhost:8080}"
SESSION_ID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())" 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "demo-$(date +%s)")

echo "=========================================="
echo "PCG Arena Stage 0 Demo"
echo "=========================================="
echo "API URL: $API_URL"
echo "Session ID: $SESSION_ID"
echo ""

# Check if jq is available for JSON parsing
if command -v jq &> /dev/null; then
    USE_JQ=true
else
    USE_JQ=false
    echo "Note: jq not found. Using basic JSON parsing."
fi

# Function to extract battle_id from JSON response
extract_battle_id() {
    local json="$1"
    if [ "$USE_JQ" = true ]; then
        echo "$json" | jq -r '.battle.battle_id'
    else
        echo "$json" | grep -o '"battle_id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | grep -o '"[^"]*"' | tail -1 | tr -d '"'
    fi
}

# Function to extract vote_id from JSON response
extract_vote_id() {
    local json="$1"
    if [ "$USE_JQ" = true ]; then
        echo "$json" | jq -r '.vote_id'
    else
        echo "$json" | grep -o '"vote_id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | grep -o '"[^"]*"' | tail -1 | tr -d '"'
    fi
}

# Check health endpoint
echo "Checking backend health..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to connect to backend at $API_URL"
    echo "Make sure the backend is running: docker compose up"
    exit 1
fi
echo "✓ Backend is healthy"
echo ""

# Get initial leaderboard
echo "Initial leaderboard:"
INITIAL_LEADERBOARD=$(curl -s "$API_URL/v1/leaderboard")
if [ "$USE_JQ" = true ]; then
    echo "$INITIAL_LEADERBOARD" | jq -r '.generators[] | "\(.generator_id): \(.rating) (games: \(.games_played))"'
else
    echo "$INITIAL_LEADERBOARD" | grep -o '"generator_id"[^}]*' | head -3
fi
echo ""

# Results array for random selection
RESULTS=("LEFT" "RIGHT" "TIE")

# Main loop: 10 battles
for i in {1..10}; do
    echo "=========================================="
    echo "Battle #$i of 10"
    echo "=========================================="
    
    # Fetch next battle
    echo "Fetching battle..."
    BATTLE_RESPONSE=$(curl -s -X POST "$API_URL/v1/battles:next" \
        -H "Content-Type: application/json" \
        -d "{
            \"client_version\": \"0.1.0\",
            \"session_id\": \"$SESSION_ID\"
        }")
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to fetch battle"
        exit 1
    fi
    
    BATTLE_ID=$(extract_battle_id "$BATTLE_RESPONSE")
    if [ -z "$BATTLE_ID" ] || [ "$BATTLE_ID" = "null" ]; then
        echo "ERROR: Failed to extract battle_id from response"
        echo "Response: $BATTLE_RESPONSE"
        exit 1
    fi
    
    echo "✓ Battle ID: $BATTLE_ID"
    
    # Extract generator names for display
    if [ "$USE_JQ" = true ]; then
        LEFT_GEN=$(echo "$BATTLE_RESPONSE" | jq -r '.battle.left.generator.name')
        RIGHT_GEN=$(echo "$BATTLE_RESPONSE" | jq -r '.battle.right.generator.name')
        echo "  Left: $LEFT_GEN"
        echo "  Right: $RIGHT_GEN"
    fi
    
    # Randomly select result (LEFT, RIGHT, or TIE)
    RESULT=${RESULTS[$((RANDOM % 3))]}
    echo "Voting: $RESULT"
    
    # Submit vote
    VOTE_RESPONSE=$(curl -s -X POST "$API_URL/v1/votes" \
        -H "Content-Type: application/json" \
        -d "{
            \"client_version\": \"0.1.0\",
            \"session_id\": \"$SESSION_ID\",
            \"battle_id\": \"$BATTLE_ID\",
            \"result\": \"$RESULT\",
            \"tags\": []
        }")
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to submit vote"
        exit 1
    fi
    
    VOTE_ID=$(extract_vote_id "$VOTE_RESPONSE")
    if [ -z "$VOTE_ID" ] || [ "$VOTE_ID" = "null" ]; then
        echo "ERROR: Failed to extract vote_id from response"
        echo "Response: $VOTE_RESPONSE"
        exit 1
    fi
    
    echo "✓ Vote ID: $VOTE_ID"
    
    # Show current leaderboard
    CURRENT_LEADERBOARD=$(curl -s "$API_URL/v1/leaderboard")
    echo "Current leaderboard:"
    if [ "$USE_JQ" = true ]; then
        echo "$CURRENT_LEADERBOARD" | jq -r '.generators[] | "  \(.generator_id): \(.rating) (games: \(.games_played), wins: \(.wins), losses: \(.losses))"'
    else
        echo "$CURRENT_LEADERBOARD" | grep -o '"generator_id"[^}]*' | head -3
    fi
    
    # Wait 2 seconds before next iteration (except on last iteration)
    if [ $i -lt 10 ]; then
        echo ""
        echo "Waiting 2 seconds before next battle..."
        sleep 2
        echo ""
    fi
done

echo ""
echo "=========================================="
echo "Demo Complete!"
echo "=========================================="
echo ""
echo "Final leaderboard:"
FINAL_LEADERBOARD=$(curl -s "$API_URL/v1/leaderboard")
if [ "$USE_JQ" = true ]; then
    echo "$FINAL_LEADERBOARD" | jq -r '.generators[] | "\(.generator_id): rating=\(.rating), games=\(.games_played), wins=\(.wins), losses=\(.losses), ties=\(.ties)"'
else
    echo "$FINAL_LEADERBOARD"
fi
echo ""
echo "You can verify persistence by:"
echo "1. Stopping the backend: docker compose down"
echo "2. Restarting: docker compose up"
echo "3. Checking leaderboard: curl $API_URL/v1/leaderboard"
echo ""

