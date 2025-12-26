
# ToyVerse Setup Script

Write-Host "Starting ToyVerse Setup..." -ForegroundColor Green

# 1. Configuration
$DB_SERVER = "localhost\SQLEXPRESS"
$DB_NAME = "ToyVerseDB"
$ODBC_DRIVER = "ODBC Driver 18 for SQL Server"
$BACKEND_DIR = Join-Path $PSScriptRoot "ToyVerse-Backend"
$FRONTEND_DIR = Join-Path $PSScriptRoot "ToyVerse-Frontend"

# 2. Database Creation Check
Write-Host "`nChecking Database..."
$createDbQuery = "IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '$DB_NAME') BEGIN CREATE DATABASE [$DB_NAME]; END"
try {
    # Try using sqlcmd first (standard with SQL Server)
    sqlcmd -S $DB_SERVER -E -Q $createDbQuery -C
    Write-Host "   Database '$DB_NAME' checked/created successfully." -ForegroundColor Green
} catch {
    Write-Host "   Warning: Could not create database via sqlcmd. Trying to proceed, SQLAlchemy might handle table updates but DB must exist." -ForegroundColor Yellow
}

# 3. Backend Setup
Write-Host "`nSetting up Backend..."
Set-Location $BACKEND_DIR

# Create .env file manually line by line to avoid syntax issues
$lines = @(
    "DB_SERVER=$DB_SERVER",
    "DB_NAME=$DB_NAME",
    "DB_DRIVER=$ODBC_DRIVER",
    "DEBUG=True",
    "SECRET_KEY=dev_secret_key_123",
    "ALGORITHM=HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES=30",
    "GROQ_API_KEY="
)
$lines | Out-File ".env" -Encoding utf8
Write-Host "   Generated .env file."

# Python Virtual Env
if (-not (Test-Path "venv")) {
    Write-Host "   Creating Python virtual environment..."
    python -m venv venv
}

# Install Requirements
Write-Host "   Installing Python dependencies..."
.\venv\Scripts\python -m pip install --upgrade pip
.\venv\Scripts\pip install -r requirements.txt

# Run Database Migrations/Init via a temporary python script
Write-Host "   Initializing Database Tables..."
$pyScript = "
import sys
import os
sys.path.append(os.getcwd())
try:
    from app.core.database import init_db
    init_db()
    print('   Database tables initialized.')
except Exception as e:
    print(f'   Error initializing DB: {e}')
"
$pyScript | Out-File "init_db_temp.py" -Encoding utf8
.\venv\Scripts\python init_db_temp.py
Remove-Item "init_db_temp.py"

# 4. Frontend Setup
Write-Host "`nSetting up Frontend..."
if (Test-Path $FRONTEND_DIR) {
    Set-Location $FRONTEND_DIR
    if (Get-Command "npm" -ErrorAction SilentlyContinue) {
        Write-Host "   Installing Node modules..."
        npm install
    } else {
        Write-Host "   Warning: 'npm' not found. Skipping frontend dependency install." -ForegroundColor Yellow
    }
}

Write-Host "`nSetup Complete!" -ForegroundColor Green
Write-Host "To run the app:"
Write-Host "1. Backend: cd ToyVerse-Backend; .\venv\Scripts\uvicorn app.main:app --reload"
Write-Host "2. Frontend: cd ToyVerse-Frontend; npm run dev"
