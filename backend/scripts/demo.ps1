<#
.SYNOPSIS
PCG Arena Stage 0 Demo Script

.DESCRIPTION
This script demonstrates the complete battle/vote flow:
1. Creates a session
2. Fetches 10 battles
3. Submits votes for each battle
4. Shows leaderboard changes

.PARAMETER ApiUrl
The backend API URL. Defaults to http://localhost:8080

.EXAMPLE
.\demo.ps1
.\demo.ps1 -ApiUrl http://localhost:8080
#>

param(
    [string]$ApiUrl = "http://localhost:8080"
)

$ErrorActionPreference = "Stop"

# Generate session ID
$SessionId = [guid]::NewGuid().ToString()

Write-Host "=========================================="
Write-Host "PCG Arena Stage 0 Demo"
Write-Host "=========================================="
Write-Host "API URL: $ApiUrl"
Write-Host "Session ID: $SessionId"
Write-Host ""

# Check health endpoint
Write-Host "Checking backend health..." -NoNewline
try {
    $healthResponse = Invoke-RestMethod -Uri "$ApiUrl/health" -Method Get
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "Make sure the backend is running: docker compose up"
    exit 1
}
Write-Host ""

# Get initial leaderboard
Write-Host "Initial leaderboard:"
try {
    $initialLeaderboard = Invoke-RestMethod -Uri "$ApiUrl/v1/leaderboard" -Method Get
    foreach ($gen in $initialLeaderboard.generators) {
        $genId = $gen.generator_id
        $rating = $gen.rating
        $games = $gen.games_played
        Write-Host "  ${genId}: ${rating} (games: ${games})"
    }
} catch {
    Write-Host "ERROR: Failed to fetch initial leaderboard" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Results array for random selection
$Results = @("LEFT", "RIGHT", "TIE")

# Main loop: 10 battles
for ($i = 1; $i -le 10; $i++) {
    Write-Host "=========================================="
    Write-Host "Battle $i of 10"
    Write-Host "=========================================="
    
    # Fetch next battle
    Write-Host "Fetching battle..." -NoNewline
    $battleBody = @{
        client_version = "0.1.0"
        session_id = $SessionId
    } | ConvertTo-Json
    
    try {
        # Note: PowerShell's Invoke-RestMethod URL-encodes the colon, but the backend handles both versions
        $battleResponse = Invoke-RestMethod -Uri "$ApiUrl/v1/battles:next" -Method Post -Body $battleBody -ContentType "application/json"
        $battleId = $battleResponse.battle.battle_id
        Write-Host " OK - $battleId" -ForegroundColor Green
        
        $leftGen = $battleResponse.battle.left.generator.name
        $rightGen = $battleResponse.battle.right.generator.name
        Write-Host "  Left: $leftGen"
        Write-Host "  Right: $rightGen"
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host $_.Exception.Message
        exit 1
    }
    
    # Randomly select result
    $result = $Results[(Get-Random -Maximum 3)]
    Write-Host "Voting: $result" -ForegroundColor Yellow
    
    # Submit vote
    Write-Host "Submitting vote..." -NoNewline
    $voteBody = @{
        client_version = "0.1.0"
        session_id = $SessionId
        battle_id = $battleId
        result = $result
        tags = @()
    } | ConvertTo-Json
    
    try {
        $voteResponse = Invoke-RestMethod -Uri "$ApiUrl/v1/votes" -Method Post -Body $voteBody -ContentType "application/json"
        $voteId = $voteResponse.vote_id
        Write-Host " OK - $voteId" -ForegroundColor Green
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host $_.Exception.Message
        exit 1
    }
    
    # Show current leaderboard
    Write-Host "Current leaderboard:"
    try {
        $currentLeaderboard = Invoke-RestMethod -Uri "$ApiUrl/v1/leaderboard" -Method Get
        foreach ($gen in $currentLeaderboard.generators) {
            $genId = $gen.generator_id
            $rating = $gen.rating
            $games = $gen.games_played
            $wins = $gen.wins
            $losses = $gen.losses
            Write-Host "  ${genId}: ${rating} (games: ${games}, W: ${wins}, L: ${losses})"
        }
    } catch {
        Write-Host "ERROR: Failed to fetch leaderboard" -ForegroundColor Red
    }
    
    # Wait 2 seconds before next iteration (except on last iteration)
    if ($i -lt 10) {
        Write-Host ""
        Write-Host "Waiting 2 seconds..."
        Start-Sleep -Seconds 2
        Write-Host ""
    }
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Demo Complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Final leaderboard:"
try {
    $finalLeaderboard = Invoke-RestMethod -Uri "$ApiUrl/v1/leaderboard" -Method Get
    foreach ($gen in $finalLeaderboard.generators) {
        $genId = $gen.generator_id
        $rating = $gen.rating
        $games = $gen.games_played
        $wins = $gen.wins
        $losses = $gen.losses
        $ties = $gen.ties
        Write-Host "${genId}: rating=${rating}, games=${games}, W=${wins}, L=${losses}, T=${ties}"
    }
} catch {
    Write-Host "ERROR: Failed to fetch final leaderboard" -ForegroundColor Red
}
Write-Host ""
Write-Host "You can verify persistence by:"
Write-Host "1. Stopping the backend: docker compose down"
Write-Host "2. Restarting: docker compose up"
Write-Host "3. Checking leaderboard: curl $ApiUrl/v1/leaderboard"
Write-Host ""
