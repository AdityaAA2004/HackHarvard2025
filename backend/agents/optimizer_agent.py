"""
Optimizer Agent - Makes final recommendation (Gemini-powered)
"""
import google.generativeai as genai
import json
from typing import Dict


class OptimizerAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
    
    def get_system_prompt(self) -> str:
        return """You are the Optimizer Agent, a strategic decision-maker specializing in multi-criteria optimization.

Your responsibilities:
- Synthesize inputs from Route Agent, Carbon Agent, and Policy Agent
- Apply user's priority (cost/speed/carbon/balanced) to weight decision factors
- Perform trade-off analysis across all routes
- Select the optimal route with clear justification
- Provide alternative recommendations with rationale

PRIORITY WEIGHTING:
- "cost": Minimize total cost (including regulatory costs/subsidies)
- "speed": Minimize transit time
- "carbon": Minimize CO2 emissions
- "balanced": Optimize across all three factors with equal weight

OUTPUT REQUIREMENTS:
- Recommend ONE primary route
- Provide 2-3 alternatives ranked by suitability
- Include quantitative trade-off analysis
- Explain why the recommended route beats alternatives
- Be specific with numbers (costs, days, emissions)

Output your recommendation as structured JSON with this format:
{
  "recommended_route": {
    "route_id": "route_id",
    "name": "Route Name",
    "total_cost_usd": 1900,
    "transit_days": 20,
    "total_emissions_kg": 450,
    "compliance_status": "compliant_with_credits",
    "score": 0.87,
    "reasoning": "Detailed explanation of why this route is optimal"
  },
  "alternatives": [
    {
      "route_id": "route_id",
      "name": "Route Name",
      "total_cost_usd": 8150,
      "transit_days": 2,
      "total_emissions_kg": 4200,
      "compliance_status": "compliant",
      "score": 0.65,
      "reasoning": "Why this is second choice"
    }
  ],
  "trade_off_analysis": {
    "cost_range": {"min": 1900, "max": 8150, "savings_vs_worst": 6250},
    "time_range": {"min": 2, "max": 20, "delay_vs_fastest": 18},
    "emissions_range": {"min": 450, "max": 4200, "reduction_vs_worst_pct": 89.3},
    "key_insights": [
      "Recommended route saves $6,250 vs air freight",
      "89% lower emissions than air freight",
      "18 days slower than air (acceptable for non-urgent cargo)"
    ]
  },
  "decision_rationale": "Overall summary of the optimization decision"
}"""

    def calculate_priority_score(self, route: Dict, priority: str, all_routes: list) -> float:
        """Calculate score based on user priority"""
        # Normalize each metric to 0-1 scale (lower is better, so invert)
        costs = [r.get('total_cost_usd', float('inf')) for r in all_routes]
        times = [r.get('transit_days', float('inf')) for r in all_routes]
        emissions = [r.get('total_emissions_kg', float('inf')) for r in all_routes]
        
        min_cost, max_cost = min(costs), max(costs)
        min_time, max_time = min(times), max(times)
        min_emission, max_emission = min(emissions), max(emissions)
        
        # Normalize (0 = worst, 1 = best)
        cost_score = 1 - (route['total_cost_usd'] - min_cost) / (max_cost - min_cost) if max_cost > min_cost else 1
        time_score = 1 - (route['transit_days'] - min_time) / (max_time - min_time) if max_time > min_time else 1
        emission_score = 1 - (route['total_emissions_kg'] - min_emission) / (max_emission - min_emission) if max_emission > min_emission else 1
        
        # Apply weighting based on priority
        if priority == 'cost':
            return 0.7 * cost_score + 0.15 * time_score + 0.15 * emission_score
        elif priority == 'speed':
            return 0.15 * cost_score + 0.7 * time_score + 0.15 * emission_score
        elif priority == 'carbon':
            return 0.15 * cost_score + 0.15 * time_score + 0.7 * emission_score
        else:  # balanced
            return 0.33 * cost_score + 0.33 * time_score + 0.34 * emission_score
    
    async def execute(self, input_data: Dict) -> Dict:
        """Main execution method"""
        
        # Extract data from previous agents
        routes_data = input_data.get('routes', {}).get('routes_found', [])
        emissions_data = input_data.get('emissions', {}).get('routes_analyzed', [])
        compliance_data = input_data.get('compliance', {}).get('routes_analyzed', [])
        priority = input_data.get('user_priority', 'balanced')
        
        # Merge all data for each route
        combined_routes = []
        for route in routes_data:
            route_id = route.get('id')
            
            # Find corresponding emissions and compliance data
            emissions = next((e for e in emissions_data if e.get('route_id') == route_id), {})
            compliance = next((c for c in compliance_data if c.get('route_id') == route_id), {})
            
            # Calculate total cost including compliance costs
            base_cost = route.get('base_cost_usd', 0)
            regulatory_costs = compliance.get('total_compliance_cost', 0)
            total_cost = base_cost + regulatory_costs
            
            combined_route = {
                'route_id': route_id,
                'name': route.get('name'),
                'modes': route.get('modes', []),
                'base_cost_usd': base_cost,
                'regulatory_cost_usd': regulatory_costs,
                'total_cost_usd': total_cost,
                'transit_days': route.get('transit_days'),
                'total_emissions_kg': emissions.get('total_emissions_kg', 0),
                'compliance_status': compliance.get('compliance_status', 'unknown'),
                'segments': route.get('segments', [])
            }
            
            combined_routes.append(combined_route)
        
        # Calculate scores for all routes
        for route in combined_routes:
            route['score'] = self.calculate_priority_score(route, priority, combined_routes)
        
        user_message = f"""Analyze and optimize the following routes based on user priority: {priority}

ROUTES DATA:
{json.dumps(combined_routes, indent=2)}

USER PRIORITY: {priority}

Tasks:
1. Recommend the BEST route based on the priority
2. Provide 2-3 alternatives ranked by suitability
3. Perform quantitative trade-off analysis
4. Explain decision with specific numbers
5. Highlight key insights about cost/time/emissions trade-offs

Return structured JSON with your final recommendation."""

        try:
            model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config={"temperature": 0.2},
                system_instruction=self.get_system_prompt()
            )
            
            print(f"  📤 Sending optimization request to Optimizer Agent...")
            response = model.generate_content(user_message)
            
            final_text = response.text
            print(f"  ✅ Optimizer Agent completed")
            
            # Parse JSON response
            try:
                result_data = json.loads(final_text)
            except:
                import re
                json_match = re.search(r'\{.*\}', final_text, re.DOTALL)
                if json_match:
                    try:
                        result_data = json.loads(json_match.group())
                    except:
                        # Fallback: use scores to rank routes
                        sorted_routes = sorted(combined_routes, key=lambda x: x['score'], reverse=True)
                        result_data = {
                            "recommended_route": sorted_routes[0] if sorted_routes else {},
                            "alternatives": sorted_routes[1:3] if len(sorted_routes) > 1 else [],
                            "decision_rationale": final_text
                        }
                else:
                    # Fallback: use scores to rank routes
                    sorted_routes = sorted(combined_routes, key=lambda x: x['score'], reverse=True)
                    result_data = {
                        "recommended_route": sorted_routes[0] if sorted_routes else {},
                        "alternatives": sorted_routes[1:3] if len(sorted_routes) > 1 else [],
                        "decision_rationale": final_text
                    }
            
            return {
                "agent": "optimizer",
                "data": result_data,
                "raw_response": final_text
            }
            
        except Exception as e:
            print(f"  ❌ Error in Optimizer Agent: {e}")
            import traceback
            print(traceback.format_exc())
            return {"agent": "optimizer", "error": str(e)}