"""
Multi-Agent Orchestrator - Coordinates all agents
"""
from typing import Dict, List
from agents.route_agent import RouteAgent
from agents.carbon_agent import CarbonAgent
# from agents.policy_agent import PolicyAgent
# from agents.optimizer_agent import OptimizerAgent
import traceback


class MultiAgentOrchestrator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        if not api_key:
            print("⚠️  WARNING: No API key provided to orchestrator!")
        
        try:
            self.route_agent = RouteAgent(api_key)
            print("✅ Route Agent initialized")
            
            self.carbon_agent = CarbonAgent(api_key)
            print("✅ Carbon Agent initialized")
            
            # TODO: Initialize remaining agents
            # self.policy_agent = PolicyAgent(api_key)
            # self.optimizer_agent = OptimizerAgent(api_key)
            
        except Exception as e:
            print(f"❌ Error initializing agents: {e}")
            raise
    
    async def execute(self, user_input: Dict) -> Dict:
        """Execute multi-agent workflow"""
        
        conversation_log = []
        
        try:
            # Step 1: Route Agent - Find routes
            print(f"\n🚚 Route Agent: Finding routes...")
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
                "message": f"Found {len(route_result.get('data', {}).get('routes_found', []))} viable routes",
                "data": route_result.get('data', {})
            })
            print(f"✅ Route Agent completed")
            
            # Step 2: Carbon Agent - Calculate emissions
            print(f"\n🌱 Carbon Agent: Calculating emissions...")
            carbon_input = {
                "routes": route_result.get('data', {}).get('routes_found', []),
                "weight_tons": user_input['weight']
            }
            carbon_result = await self.carbon_agent.execute(carbon_input)
            
            if "error" in carbon_result:
                print(f"❌ Carbon Agent error: {carbon_result['error']}")
                return {
                    "success": False,
                    "error": f"Carbon Agent failed: {carbon_result['error']}",
                    "agent_conversation": conversation_log,
                    "request": user_input
                }
            
            conversation_log.append({
                "agent": "carbon",
                "message": "Analyzed emissions for all routes",
                "data": carbon_result.get('data', {})
            })
            print(f"✅ Carbon Agent completed")
            
            # Step 3: Policy Agent (TODO)
            # print(f"\n⚖️  Policy Agent: Checking compliance...")
            # policy_result = await self.policy_agent.execute({...})
            
            # Step 4: Optimizer Agent (TODO)
            # print(f"\n🎯 Optimizer Agent: Making recommendation...")
            # optimizer_result = await self.optimizer_agent.execute({...})
            
            # For now, return combined results
            print(f"\n🎉 Multi-agent analysis completed!\n")
            
            return {
                "success": True,
                "recommendation": {
                    "routes": route_result.get('data', {}),
                    "emissions": carbon_result.get('data', {}),
                    # Add policy and optimizer results when ready
                },
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