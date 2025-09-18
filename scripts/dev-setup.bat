@echo off
REM HackSeek Development Environment Setup Script for Windows
setlocal EnableDelayedExpansion

echo 🚀 Setting up HackSeek development environment...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env >nul
    echo ✅ .env file created. Please update it with your API keys.
) else (
    echo ✅ .env file already exists.
)

REM Create development database seed file
if not exist database\dev-seed.sql (
    echo 📊 Creating development database seed file...
    if not exist database mkdir database
    (
        echo -- Development seed data for HackSeek
        echo -- Sample hackathons for testing
        echo.
        echo INSERT INTO hackathons ^(id, title, description, start_date, end_date, location, prize_money, registration_url, platform, created_at^) VALUES
        echo ^('dev-hack-1', 'Local Dev Hackathon', 'Test hackathon for development', '2024-12-01', '2024-12-03', 'Online', 5000, 'https://example.com/dev-hack-1', 'devpost', NOW()^),
        echo ^('dev-hack-2', 'AI Challenge 2024', 'Build AI solutions', '2024-12-15', '2024-12-17', 'San Francisco, CA', 10000, 'https://example.com/ai-challenge', 'unstop', NOW()^),
        echo ^('dev-hack-3', 'Web3 Innovation', 'Blockchain hackathon', '2025-01-05', '2025-01-07', 'New York, NY', 15000, 'https://example.com/web3-hack', 'devfolio', NOW()^)
        echo ON CONFLICT ^(id^) DO NOTHING;
    ) > database\dev-seed.sql
    echo ✅ Development seed data created.
)

REM Stop any running containers
echo 🛑 Stopping any running containers...
docker-compose -f docker-compose.dev.yml down >nul 2>&1

REM Build and start development environment
echo 🏗️  Building development containers...
docker-compose -f docker-compose.dev.yml build

echo 🎯 Starting development environment...
docker-compose -f docker-compose.dev.yml up -d postgres redis

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
set /a timeout=30
:wait_loop
docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U hackseek_user -d hackseek_dev >nul 2>&1
if not errorlevel 1 goto db_ready
timeout /t 1 /nobreak >nul
set /a timeout-=1
if !timeout! gtr 0 goto wait_loop

echo ❌ Database failed to start within 30 seconds
pause
exit /b 1

:db_ready
echo ✅ Database is ready!

REM Start backend and frontend
echo 🔄 Starting backend and frontend...
docker-compose -f docker-compose.dev.yml up -d backend frontend

echo.
echo 🎉 Development environment is ready!
echo.
echo 📍 Services:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    Database: localhost:5432
echo    Redis:    localhost:6379
echo.
echo 🔧 Optional services (use profiles):
echo    PgAdmin:  docker-compose -f docker-compose.dev.yml --profile admin up -d pgadmin
echo    Scraper:  docker-compose -f docker-compose.dev.yml --profile scraper up -d scraper
echo.
echo 📝 Next steps:
echo    1. Update .env with your API keys
echo    2. Visit http://localhost:3000 to see the app
echo    3. Check backend health: curl http://localhost:8000/health
echo.
echo 🛑 To stop: docker-compose -f docker-compose.dev.yml down
echo.
pause