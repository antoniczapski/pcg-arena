# PCG Arena - Database Backup Script (S1-K1) - Windows version
# This script creates a timestamped backup of the SQLite database

param(
    [string]$BackupDir = "$PSScriptRoot\..\..\db\backups",
    [string]$DbPath = "$PSScriptRoot\..\..\db\local\arena.sqlite",
    [int]$KeepDays = 7
)

$ErrorActionPreference = "Stop"

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "Created backup directory: $BackupDir"
}

# Generate timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "arena_${Timestamp}.sqlite"
$BackupPath = Join-Path $BackupDir $BackupFile

# Check if database exists
if (!(Test-Path $DbPath)) {
    Write-Error "Database file not found: $DbPath"
    exit 1
}

# Create backup
Write-Host "Creating backup: $BackupFile"
Copy-Item $DbPath $BackupPath

# Verify backup
if (Test-Path $BackupPath) {
    $Size = (Get-Item $BackupPath).Length / 1MB
    Write-Host "Backup created successfully: $BackupFile ($([math]::Round($Size, 2)) MB)" -ForegroundColor Green
} else {
    Write-Error "Backup failed"
    exit 1
}

# S1-K3: Rotate backups - keep only last N days
Write-Host "Rotating backups (keeping last $KeepDays days)..."
$CutoffDate = (Get-Date).AddDays(-$KeepDays)
Get-ChildItem -Path $BackupDir -Filter "arena_*.sqlite" | 
    Where-Object { $_.LastWriteTime -lt $CutoffDate } |
    ForEach-Object {
        Write-Host "  Deleting old backup: $($_.Name)"
        Remove-Item $_.FullName
    }

# Count remaining backups
$BackupCount = (Get-ChildItem -Path $BackupDir -Filter "arena_*.sqlite").Count
Write-Host "Backup complete. Total backups: $BackupCount" -ForegroundColor Green

