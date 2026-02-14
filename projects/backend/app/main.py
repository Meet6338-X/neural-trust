"""
ChainGuardian Backend - AI-Powered DeFi Risk & Compliance Assistant

FastAPI application serving as the bridge between the frontend,
AI risk engine, and GuardianVault smart contract.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models.database import init_db
from app.api.routes import analysis, vault, audit, audit_contract, reputation, portfolio, simulate
from app.api.routes import blockchain, chatbot
from app.api.websockets.alerts import websocket_handler, manager
from app.services.asset_protection import asset_protection_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting ChainGuardian Backend...")
    logger.info(f"Environment: {settings.ALGORAND_NETWORK}")
    logger.info(f"AI Model: {settings.AI_MODEL}")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ChainGuardian Backend...")


# Create FastAPI application
app = FastAPI(
    title="ChainGuardian API",
    description="""
## AI-Powered DeFi Risk & Compliance Assistant on Algorand

ChainGuardian combines off-chain AI intelligence with on-chain blockchain enforcement 
to protect users from risky or fraudulent financial actions.

### Core Features

* **AI Risk Analysis** - Analyze transactions for potential risks using AI
* **Smart Contract Audit** - Audit TEAL and Python smart contracts for vulnerabilities
* **Address Reputation** - Get trust scores for Algorand addresses
* **Portfolio Analysis** - Analyze portfolio risk exposure
* **Transaction Simulation** - Simulate transactions before execution
* **Real-Time Alerts** - WebSocket-based real-time risk alerts

### API Endpoints

| Category | Description |
|----------|-------------|
| `/api/analysis` | Transaction risk analysis |
| `/api/audit` | Smart contract auditing |
| `/api/reputation` | Address reputation scoring |
| `/api/portfolio` | Portfolio risk analysis |
| `/api/simulate` | Transaction simulation |
| `/api/vault` | Guardian Vault management |
| `/ws/alerts` | Real-time WebSocket alerts |

### Authentication

Most endpoints are publicly accessible. Rate limiting may apply.

### Support

- Documentation: `/docs`
- Health Check: `/health`
- Detailed Health: `/health/detailed`
    """,
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "ChainGuardian Team",
        "email": "support@chainguardian.app",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints for monitoring service status.",
        },
        {
            "name": "web",
            "description": "Web page routes for the ChainGuardian dashboard.",
        },
        {
            "name": "Analysis",
            "description": "AI-powered transaction risk analysis endpoints.",
        },
        {
            "name": "Contract Audit",
            "description": "Smart contract security auditing for TEAL and Python contracts.",
        },
        {
            "name": "Address Reputation",
            "description": "Address trust scoring and reputation management.",
        },
        {
            "name": "Portfolio Analysis",
            "description": "Portfolio risk analysis and recommendations.",
        },
        {
            "name": "Transaction Simulation",
            "description": "Transaction simulation and fee estimation.",
        },
        {
            "name": "Vault",
            "description": "Guardian Vault management endpoints.",
        },
        {
            "name": "Audit Log",
            "description": "On-chain audit log retrieval.",
        },
        {
            "name": "websocket",
            "description": "WebSocket connection status and management.",
        },
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


# Include routers
app.include_router(analysis.router, prefix=settings.API_PREFIX)
app.include_router(vault.router, prefix=settings.API_PREFIX)
app.include_router(audit.router, prefix=settings.API_PREFIX)
app.include_router(audit_contract.router, prefix=settings.API_PREFIX)
app.include_router(reputation.router, prefix=settings.API_PREFIX)
app.include_router(portfolio.router, prefix=settings.API_PREFIX)
app.include_router(simulate.router, prefix=settings.API_PREFIX)
app.include_router(blockchain.router, prefix=settings.API_PREFIX)
app.include_router(chatbot.router, prefix=settings.API_PREFIX)
app.include_router(asset_protection_router, prefix=settings.API_PREFIX)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "ChainGuardian Backend",
        "network": settings.ALGORAND_NETWORK,
    }


# Detailed health check endpoint
@app.get("/health/detailed", tags=["health"])
async def detailed_health_check():
    """
    Detailed health check endpoint with service dependencies status.
    """
    import time
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "service": "ChainGuardian Backend",
        "uptime": "running",
        "checks": {}
    }
    
    # Check AI service configuration
    ai_configured = bool(settings.OPENROUTER_API_KEY)
    health_status["checks"]["ai_service"] = {
        "status": "configured" if ai_configured else "not_configured",
        "model": settings.AI_MODEL,
        "provider": "OpenRouter"
    }
    
    # Check blockchain connectivity
    try:
        from app.services.blockchain_service import get_blockchain_service
        blockchain_service = get_blockchain_service()
        # Try to get the latest block
        latest_block = blockchain_service.algod_client.status()
        health_status["checks"]["blockchain"] = {
            "status": "connected",
            "network": settings.ALGORAND_NETWORK,
            "last_round": latest_block.get("last-round", "unknown")
        }
    except Exception as e:
        health_status["checks"]["blockchain"] = {
            "status": "error",
            "error": str(e)[:100]
        }
        health_status["status"] = "degraded"
    
    # Check database connectivity
    try:
        from app.models.database import async_engine
        from sqlalchemy import text
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "connected",
            "type": "SQLite"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "error",
            "error": str(e)[:100]
        }
        health_status["status"] = "degraded"
    
    # Check Guardian Vault contract
    health_status["checks"]["guardian_vault"] = {
        "status": "configured" if settings.GUARDIAN_VAULT_APP_ID else "not_configured",
        "app_id": settings.GUARDIAN_VAULT_APP_ID
    }
    
    # Overall status
    if health_status["status"] != "healthy":
        health_status["status"] = "degraded"
    
    return health_status


# WebSocket endpoint for real-time alerts
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time risk alerts.
    
    Clients can subscribe to address alerts by sending:
    {"type": "subscribe", "address": "ALGORAND_ADDRESS"}
    
    And unsubscribe with:
    {"type": "unsubscribe", "address": "ALGORAND_ADDRESS"}
    """
    connection_id = str(uuid.uuid4())
    await websocket_handler(websocket, connection_id)


# WebSocket status endpoint
@app.get("/ws/status", tags=["websocket"])
async def websocket_status():
    """Get WebSocket connection status."""
    return {
        "active_connections": manager.get_connection_count(),
        "status": "operational"
    }


# Web page routes
@app.get("/", response_class=HTMLResponse, tags=["web"])
async def root(request: Request):
    """Root endpoint - Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse, tags=["web"])
async def dashboard(request: Request):
    """Dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/vault", response_class=HTMLResponse, tags=["web"])
async def vault_page(request: Request):
    """Vault management page."""
    return templates.TemplateResponse("vault.html", {"request": request})


@app.get("/blockchain", response_class=HTMLResponse, tags=["web"])
async def blockchain_page(request: Request):
    """Blockchain management page."""
    return templates.TemplateResponse("blockchain.html", {"request": request})


@app.get("/asset-protection", response_class=HTMLResponse, tags=["web"])
async def asset_protection_page(request: Request):
    """Asset Protection page."""
    return templates.TemplateResponse("asset_protection.html", {"request": request})


@app.get("/quick-analysis", response_class=HTMLResponse, tags=["web"])
async def quick_analysis_page(request: Request):
    """Quick Address Analysis page - simplified input."""
    return templates.TemplateResponse("simple_analysis.html", {"request": request})


@app.get("/chatbot", response_class=HTMLResponse, tags=["web"])
async def chatbot_page(request: Request):
    """AI Chatbot page."""
    return templates.TemplateResponse("chatbot.html", {"request": request})


@app.get("/audit", response_class=HTMLResponse, tags=["web"])
async def audit_page(request: Request):
    """Audit log page."""
    return templates.TemplateResponse("audit.html", {"request": request})


# API root endpoint
@app.get("/api", tags=["root"])
async def api_root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "ChainGuardian API",
        "description": "AI-Powered DeFi Risk & Compliance Assistant on Algorand",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
 
 
