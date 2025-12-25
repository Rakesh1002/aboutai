#!/bin/bash
# ===========================================
# aboutai Backend - Stop Development Services
# ===========================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   aboutai Backend - Stopping Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Kill Python processes
echo -e "\n${YELLOW}▶ Stopping Python processes...${NC}"
pkill -f "celery -A app.core" 2>/dev/null && echo -e "${GREEN}✓ Celery stopped${NC}" || echo -e "${YELLOW}⚠ No Celery processes found${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null && echo -e "${GREEN}✓ Uvicorn stopped${NC}" || echo -e "${YELLOW}⚠ No Uvicorn processes found${NC}"

# Stop Docker containers
echo -e "\n${YELLOW}▶ Stopping Docker containers...${NC}"

if docker ps --format '{{.Names}}' | grep -q '^aboutai-redis$'; then
    docker stop aboutai-redis
    echo -e "${GREEN}✓ Redis stopped${NC}"
else
    echo -e "${YELLOW}⚠ Redis not running${NC}"
fi

if docker ps --format '{{.Names}}' | grep -q '^aboutai-searxng$'; then
    docker stop aboutai-searxng
    echo -e "${GREEN}✓ SearXNG stopped${NC}"
else
    echo -e "${YELLOW}⚠ SearXNG not running${NC}"
fi

echo -e "\n${GREEN}✓ All services stopped${NC}"
echo -e "${YELLOW}To remove containers: docker rm aboutai-redis aboutai-searxng${NC}"

