#!/bin/bash
# ===========================================
# aboutai Backend - Development Start Script
# ===========================================
# Starts all required services for local development:
# - Redis (Docker)
# - SearXNG (Docker)
# - Celery Worker
# - Celery Beat (scheduler)
# - FastAPI Server
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$BACKEND_DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   aboutai Backend - Development Environment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ===========================================
# Check prerequisites
# ===========================================
echo -e "\n${YELLOW}▶ Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker daemon is not running. Please start Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker daemon running${NC}"

# Check Poetry
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}✗ Poetry is not installed.${NC}"
    echo "Install with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi
echo -e "${GREEN}✓ Poetry found${NC}"

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ No .env file found. Creating from env.sample...${NC}"
    cp env.sample .env
    echo -e "${YELLOW}⚠ Please edit .env with your API keys before running again.${NC}"
fi
echo -e "${GREEN}✓ .env file exists${NC}"

# ===========================================
# Install Python dependencies
# ===========================================
echo -e "\n${YELLOW}▶ Installing Python dependencies...${NC}"
poetry install --no-interaction
echo -e "${GREEN}✓ Dependencies installed${NC}"

# ===========================================
# Start Docker services
# ===========================================
echo -e "\n${YELLOW}▶ Starting Docker services...${NC}"

# Start Redis
if docker ps -a --format '{{.Names}}' | grep -q '^aboutai-redis$'; then
    if docker ps --format '{{.Names}}' | grep -q '^aboutai-redis$'; then
        echo -e "${GREEN}✓ Redis already running${NC}"
    else
        docker start aboutai-redis
        echo -e "${GREEN}✓ Redis started${NC}"
    fi
else
    docker run -d --name aboutai-redis -p 6379:6379 redis:7-alpine
    echo -e "${GREEN}✓ Redis container created and started${NC}"
fi

# Start SearXNG
if docker ps -a --format '{{.Names}}' | grep -q '^aboutai-searxng$'; then
    if docker ps --format '{{.Names}}' | grep -q '^aboutai-searxng$'; then
        echo -e "${GREEN}✓ SearXNG already running${NC}"
    else
        docker start aboutai-searxng
        echo -e "${GREEN}✓ SearXNG started${NC}"
    fi
else
    # Create SearXNG with custom settings if available
    if [ -f "searxng/settings.yml" ]; then
        docker run -d \
            --name aboutai-searxng \
            -p 8888:8080 \
            -v "$BACKEND_DIR/searxng/settings.yml:/etc/searxng/settings.yml:ro" \
            -e SEARXNG_BASE_URL=http://localhost:8888/ \
            searxng/searxng:latest
    else
        docker run -d \
            --name aboutai-searxng \
            -p 8888:8080 \
            -e SEARXNG_BASE_URL=http://localhost:8888/ \
            searxng/searxng:latest
    fi
    echo -e "${GREEN}✓ SearXNG container created and started${NC}"
fi

# Wait for services to be ready
echo -e "${YELLOW}▶ Waiting for services to be ready...${NC}"
sleep 3

# Check Redis connection
if docker exec aboutai-redis redis-cli ping | grep -q PONG; then
    echo -e "${GREEN}✓ Redis is responding${NC}"
else
    echo -e "${RED}✗ Redis is not responding${NC}"
    exit 1
fi

# ===========================================
# Set environment variables for local dev
# ===========================================
export REDIS_URL="redis://localhost:6379/0"
export SEARXNG_URL="http://localhost:8888"

# ===========================================
# Create log directory
# ===========================================
LOG_DIR="$BACKEND_DIR/logs"
mkdir -p "$LOG_DIR"

# ===========================================
# Function to cleanup on exit
# ===========================================
cleanup() {
    echo -e "\n${YELLOW}▶ Shutting down...${NC}"
    
    # Kill background processes
    if [ ! -z "$CELERY_PID" ]; then
        kill $CELERY_PID 2>/dev/null || true
    fi
    if [ ! -z "$BEAT_PID" ]; then
        kill $BEAT_PID 2>/dev/null || true
    fi
    if [ ! -z "$FASTAPI_PID" ]; then
        kill $FASTAPI_PID 2>/dev/null || true
    fi
    
    # Kill any remaining celery processes
    pkill -f "celery -A app.core" 2>/dev/null || true
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    
    echo -e "${GREEN}✓ All processes stopped${NC}"
    echo -e "${YELLOW}Note: Docker containers (Redis, SearXNG) are still running.${NC}"
    echo -e "${YELLOW}To stop them: docker stop aboutai-redis aboutai-searxng${NC}"
}

trap cleanup EXIT INT TERM

# ===========================================
# Start Celery Worker
# ===========================================
echo -e "\n${YELLOW}▶ Starting Celery worker...${NC}"
REDIS_URL="$REDIS_URL" poetry run celery -A app.core.celery_app worker \
    --loglevel=info \
    -Q default,pipeline,scraper,publisher \
    --logfile="$LOG_DIR/celery-worker.log" \
    --pidfile="$LOG_DIR/celery-worker.pid" &
CELERY_PID=$!
sleep 2

if kill -0 $CELERY_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Celery worker started (PID: $CELERY_PID)${NC}"
else
    echo -e "${RED}✗ Celery worker failed to start. Check $LOG_DIR/celery-worker.log${NC}"
    exit 1
fi

# ===========================================
# Start Celery Beat (Scheduler)
# ===========================================
echo -e "\n${YELLOW}▶ Starting Celery beat scheduler...${NC}"
REDIS_URL="$REDIS_URL" poetry run celery -A app.core.celery_app beat \
    --loglevel=info \
    --logfile="$LOG_DIR/celery-beat.log" \
    --pidfile="$LOG_DIR/celery-beat.pid" &
BEAT_PID=$!
sleep 2

if kill -0 $BEAT_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Celery beat started (PID: $BEAT_PID)${NC}"
else
    echo -e "${YELLOW}⚠ Celery beat may have failed. Check $LOG_DIR/celery-beat.log${NC}"
fi

# ===========================================
# Start FastAPI Server
# ===========================================
echo -e "\n${YELLOW}▶ Starting FastAPI server...${NC}"

# Find available port starting from 8080
API_PORT=8080
while lsof -i :$API_PORT &>/dev/null; do
    API_PORT=$((API_PORT + 1))
    if [ $API_PORT -gt 8100 ]; then
        echo -e "${RED}✗ Could not find available port between 8080-8100${NC}"
        exit 1
    fi
done

REDIS_URL="$REDIS_URL" SEARXNG_URL="$SEARXNG_URL" poetry run uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port $API_PORT &
FASTAPI_PID=$!
sleep 3

if kill -0 $FASTAPI_PID 2>/dev/null; then
    echo -e "${GREEN}✓ FastAPI server started on port $API_PORT (PID: $FASTAPI_PID)${NC}"
else
    echo -e "${RED}✗ FastAPI server failed to start${NC}"
    exit 1
fi

# ===========================================
# Display status
# ===========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   ✓ All services started successfully!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BLUE}FastAPI Server:${NC}  http://localhost:$API_PORT"
echo -e "  ${BLUE}API Docs:${NC}        http://localhost:$API_PORT/docs"
echo -e "  ${BLUE}Health Check:${NC}    http://localhost:$API_PORT/health"
echo -e "  ${BLUE}SearXNG:${NC}         http://localhost:8888"
echo -e "  ${BLUE}Redis:${NC}           Upstash (cloud)"
echo ""
echo -e "  ${YELLOW}Logs:${NC}"
echo -e "    - Celery Worker: $LOG_DIR/celery-worker.log"
echo -e "    - Celery Beat:   $LOG_DIR/celery-beat.log"
echo ""
echo -e "  ${YELLOW}Press Ctrl+C to stop all services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ===========================================
# Tail logs (keep script running)
# ===========================================
echo -e "\n${YELLOW}▶ Tailing logs (Ctrl+C to stop)...${NC}\n"
tail -f "$LOG_DIR/celery-worker.log" "$LOG_DIR/celery-beat.log" 2>/dev/null || wait

