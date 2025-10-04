"""
API Routes - FastAPI endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from orchestrator import MultiAgentOrchestrator
import os

router = APIRouter()

# Initialize orchestrator with API key from environment
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
orchestrator = MultiAgentOrchestrator(CLAUDE_API_KEY)


class RouteRequest(BaseModel):
    origin: str = Field(..., description="Origin city", example="Shanghai")
    destination: str = Field(..., description="Destination city", example="Berlin")
    weight: float = Field(..., gt=0, description="Weight in tons", example=10.0)
    priority: str = Field(..., description="Optimization priority", 
                         pattern="^(cost|speed|carbon|balanced)$", example="balanced")


class RouteResponse(BaseModel):
    success: bool
    recommendation: dict
    agent_conversation: list
    request: dict
    error: Optional[str] = None


@router.post("/optimize-route", response_model=RouteResponse)
async def optimize_route(request: RouteRequest):
    """
    Optimize shipping route using multi-agent system
    
    - **origin**: Starting city (e.g., Shanghai, New York)
    - **destination**: Destination city (e.g., Berlin, Tokyo)
    - **weight**: Cargo weight in tons
    - **priority**: cost | speed | carbon | balanced
    """
    try:
        result = await orchestrator.execute(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Multi-Agent Carbon Routing API",
        "agents": ["route", "carbon", "policy", "optimizer"]
    }


@router.get("/available-locations")
async def get_available_locations():
    """Get list of supported locations"""
    import json
    from pathlib import Path
    
    data_dir = Path(__file__).parent.parent / "data"
    with open(data_dir / 'locations.json') as f:
        locations_data = json.load(f)
    
    return {
        "locations": list(locations_data['locations'].keys()),
        "count": len(locations_data['locations'])
    }