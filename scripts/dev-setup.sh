#!/bin/bash

# HackSeek Development Environment Setup Script
set -e

echo "🚀 Setting up HackSeek development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your API keys."
else
    echo "✅ .env file already exists."
fi

# Create development database seed file
if [ ! -f database/dev-seed.sql ]; then
    echo "📊 Creating development database seed file..."
    mkdir -p database
    cat > database/dev-seed.sql << 'EOF'
-- Development seed data for HackSeek
-- Sample hackathons for testing

INSERT INTO hackathons (id, title, description, start_date, end_date, location, prize_money, registration_url, platform, created_at) VALUES
('dev-hack-1', 'Local Dev Hackathon', 'Test hackathon for development', '2024-12-01', '2024-12-03', 'Online', 5000, 'https://example.com/dev-hack-1', 'devpost', NOW()),
('dev-hack-2', 'AI Challenge 2024', 'Build AI solutions', '2024-12-15', '2024-12-17', 'San Francisco, CA', 10000, 'https://example.com/ai-challenge', 'unstop', NOW()),
('dev-hack-3', 'Web3 Innovation', 'Blockchain hackathon', '2025-01-05', '2025-01-07', 'New York, NY', 15000, 'https://example.com/web3-hack', 'devfolio', NOW())
ON CONFLICT (id) DO NOTHING;

EOF
    echo "✅ Development seed data created."
fi

# Stop any running containers
echo "🛑 Stopping any running containers..."
docker-compose -f docker-compose.dev.yml down 2>/dev/null || true

# Build and start development environment
echo "🏗️  Building development containers..."
docker-compose -f docker-compose.dev.yml build

echo "🎯 Starting development environment..."
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
timeout=30
while [ $timeout -gt 0 ]; do
    if docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U hackseek_user -d hackseek_dev >/dev/null 2>&1; then
        break
    fi
    sleep 1
    timeout=$((timeout - 1))
done

if [ $timeout -eq 0 ]; then
    echo "❌ Database failed to start within 30 seconds"
    exit 1
fi

echo "✅ Database is ready!"

# Start backend and frontend
echo "🔄 Starting backend and frontend..."
docker-compose -f docker-compose.dev.yml up -d backend frontend

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📍 Services:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Database: localhost:5432"
echo "   Redis:    localhost:6379"
echo ""
echo "🔧 Optional services (use profiles):"
echo "   PgAdmin:  docker-compose -f docker-compose.dev.yml --profile admin up -d pgadmin"
echo "   Scraper:  docker-compose -f docker-compose.dev.yml --profile scraper up -d scraper"
echo ""
echo "📝 Next steps:"
echo "   1. Update .env with your API keys"
echo "   2. Visit http://localhost:3000 to see the app"
echo "   3. Check backend health: curl http://localhost:8000/health"
echo ""
echo "🛑 To stop: docker-compose -f docker-compose.dev.yml down"