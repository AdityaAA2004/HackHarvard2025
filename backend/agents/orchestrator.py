"""
Multi-Agent Orchestrator - Coordinates all agents
"""
from typing import Dict, List
from agents.route_agent import RouteAgent
from agents.carbon_agent import CarbonAgent
from agents.policy_agent import PolicyAgent
from agents.optimizer_agent import OptimizerAgent


class MultiAgentOrchestrator:
    def __init__(self, api_key: str):
        self.route_agent = RouteAgent(api_key)
        self.carbon_agent = CarbonAgent(api_key)
        self.policy_agent = PolicyAgent(api_key)
        self.optimizer_agent = OptimizerAgent(api_key)
    
    async def execute(self, user_input: Dict) -> Dict:
        """Execute all agents in sequence and return results"""
        
        conversation_log = []
        
        try:
            # Step 1: Route Agent
            print("🚚 Route Agent: Finding routes...")
            route_result = await self.route_agent.execute(user_input)
            conversation_log.append({
                "agent": "route",
                "message": route_result.get('raw_response', ''),
                "data": route_result.get('data', {})
            })
            
            # Step 2: Carbon Agent
            print("🌱 Carbon Agent: Calculating emissions...")
            carbon_result = await self.carbon_agent.execute(
                route_result,
                user_input['weight']
            )
            conversation_log.append({
                "agent": "carbon",
                "message": carbon_result.get('raw_response', ''),
                "data": carbon_result.get('data', {})
            })
            
            # Step 3: Policy Agent
            print("📋 Policy Agent: Checking compliance...")
            policy_result = await self.policy_agent.execute(
                route_result,
                carbon_result,
                user_input['origin'],
                user_input['destination']
            )
            conversation_log.append({
                "agent": "policy",
                "message": policy_result.get('raw_response', ''),
                "data": policy_result.get('data', {})
            })
            
            # Step 4: Optimizer Agent
            print("🎯 Optimizer Agent: Making recommendation...")
            optimizer_result = await self.optimizer_agent.execute(
                route_result,
                carbon_result,
                policy_result,
                user_input['priority']
            )
            conversation_log.append({
                "agent": "optimizer",
                "message": optimizer_result.get('raw_response', ''),
                "data": optimizer_result.get('data', {})
            })
            
            # Compile final response
            return {
                "success": True,
                "recommendation": optimizer_result.get('data', {}),
                "agent_conversation": conversation_log,
                "request": user_input
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_conversation": conversation_log,
                "request": user_input
            }