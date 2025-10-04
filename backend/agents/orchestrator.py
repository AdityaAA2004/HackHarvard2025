"""
Multi-Agent Orchestrator - Coordinates all agents
(Currently only Route Agent for testing)
"""
from typing import Dict, List
from agents.route_agent import RouteAgent
import traceback


class MultiAgentOrchestrator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        if not api_key:
            print("⚠️  WARNING: No API key provided to orchestrator!")
        
        try:
            self.route_agent = RouteAgent(api_key)
            print("✅ Route Agent initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Route Agent: {e}")
            raise
    
    async def execute(self, user_input: Dict) -> Dict:
        """Execute Route Agent only (for testing)"""
        
        conversation_log = []
        
        try:
            # Step 1: Route Agent
            print(f"\n🚚 Route Agent: Finding routes from {user_input['origin']} to {user_input['destination']}...")
            route_result = await self.route_agent.execute(user_input)
            
            if "error" in route_result:
                print(f"❌ Route Agent error: {route_result['error']}")
                return {
                    "success": False,
                    "error": f"Route Agent failed: {route_result['error']}",
                    "agent_conversation": conversation_log,
                    "request": user_input
                }
            
            conversation_log.append({
                "agent": "route",
                "message": route_result.get('raw_response', ''),
                "data": route_result.get('data', {})
            })
            print(f"✅ Route Agent completed")
            
            # For now, return Route Agent result as recommendation
            print(f"\n🎉 Route Agent completed successfully!\n")
            
            return {
                "success": True,
                "recommendation": route_result.get('data', {}),
                "agent_conversation": conversation_log,
                "request": user_input
            }
            
        except Exception as e:
            error_msg = f"Orchestrator error: {str(e)}"
            print(f"\n❌ {error_msg}")
            print(traceback.format_exc())
            
            return {
                "success": False,
                "error": error_msg,
                "agent_conversation": conversation_log,
                "request": user_input
            }