#!/bin/bash
# ===========================================
# aboutai Backend - Service Status
# ===========================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   aboutai Backend - Service Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${YELLOW}Docker Containers:${NC}"

# Redis
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^aboutai-redis$'; then
    echo -e "  Redis:    ${GREEN}● Running${NC} (localhost:6379)"
elif docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q '^aboutai-redis$'; then
    echo -e "  Redis:    ${YELLOW}○ Stopped${NC}"
else
    echo -e "  Redis:    ${RED}✗ Not created${NC}"
fi

# SearXNG
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^aboutai-searxng$'; then
    echo -e "  SearXNG:  ${GREEN}● Running${NC} (localhost:8888)"
elif docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q '^aboutai-searxng$'; then
    echo -e "  SearXNG:  ${YELLOW}○ Stopped${NC}"
else
    echo -e "  SearXNG:  ${RED}✗ Not created${NC}"
fi

echo -e "\n${YELLOW}Python Processes:${NC}"

# Celery Worker
if pgrep -f "celery -A app.core.*worker" > /dev/null; then
    CELERY_PID=$(pgrep -f "celery -A app.core.*worker" | head -1)
    echo -e "  Celery Worker:  ${GREEN}● Running${NC} (PID: $CELERY_PID)"
else
    echo -e "  Celery Worker:  ${RED}○ Not running${NC}"
fi

# Celery Beat
if pgrep -f "celery -A app.core.*beat" > /dev/null; then
    BEAT_PID=$(pgrep -f "celery -A app.core.*beat" | head -1)
    echo -e "  Celery Beat:    ${GREEN}● Running${NC} (PID: $BEAT_PID)"
else
    echo -e "  Celery Beat:    ${RED}○ Not running${NC}"
fi

# FastAPI
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    API_PID=$(pgrep -f "uvicorn app.main:app" | head -1)
    echo -e "  FastAPI:        ${GREEN}● Running${NC} (PID: $API_PID)"
else
    echo -e "  FastAPI:        ${RED}○ Not running${NC}"
fi

echo -e "\n${YELLOW}Endpoints:${NC}"
echo "  API:       http://localhost:8080"
echo "  Docs:      http://localhost:8080/docs"
echo "  SearXNG:   http://localhost:8888"

# Health check
echo -e "\n${YELLOW}Health Check:${NC}"
if curl -s http://localhost:8080/health 2>/dev/null | grep -q "healthy"; then
    echo -e "  API Status: ${GREEN}● Healthy${NC}"
else
    echo -e "  API Status: ${RED}○ Not responding${NC}"
fi

echo ""

