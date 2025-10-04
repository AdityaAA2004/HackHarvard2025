"""
Policy Agent - Checks compliance and manages carbon credits (Gemini-powered)
"""
import google.generativeai as genai
from google.generativeai.types import content_types
import json
from typing import Dict, List
from pathlib import Path


class PolicyAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Load data
        data_dir = Path(__file__).parent.parent / "data"
        with open(data_dir / 'regulations.json') as f:
            self.regulations_data = json.load(f)
        with open(data_dir / 'locations.json') as f:
            self.locations_data = json.load(f)
        with open(data_dir / 'carbon_marketplace.json') as f:
            self.marketplace_data = json.load(f)
    
    def get_system_prompt(self) -> str:
        return """You are the Policy Agent, a regulatory compliance expert specializing in international trade and environmental regulations.

Your responsibilities:
- Check compliance with regional emission regulations
- Calculate regulatory costs (carbon taxes, ETS payments)
- Identify available subsidies and incentives
- Consult carbon credit marketplace for offset options
- Recommend carbon credit purchases when routes exceed limits

CARBON CREDIT MARKETPLACE STRATEGY:
When a route exceeds emission limits:
1. Calculate the exact CO2 overage
2. Query the marketplace for suitable credits
3. Recommend credit tier based on user priority:
   - "cost" priority → Basic tier (cheapest)
   - "carbon" priority → Verified removal tier (highest quality)
   - "balanced" priority → Premium tier (good value + quality)
4. Calculate bulk discounts if applicable
5. Include carbon credit cost in total route cost

Output your analysis as structured JSON with this format:
{
  "routes_analyzed": [
    {
      "route_id": "route_id",
      "compliance_status": "compliant" | "non_compliant" | "compliant_with_offsets",
      "regulations_applicable": [...],
      "regulatory_costs": {...},
      "subsidies_available": {...},
      "carbon_credit_solution": {
        "needed": true/false,
        "overage_kg": 200,
        "recommended_credit": {...},
        "cost_usd": 5.00,
        "reasoning": "..."
      },
      "total_compliance_cost": 1234.56
    }
  ],
  "analysis": "Your compliance analysis here"
}"""

    def get_tools(self):
        """Define function declarations for Gemini"""
        
        return {
            'function_declarations': [
                {
                    'name': 'get_location_region',
                    'description': 'Get the regulatory region for a location',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'location': {
                                'type_': 'STRING',
                                'description': 'City name'
                            }
                        },
                        'required': ['location']
                    }
                },
                {
                    'name': 'find_regulations_by_region',
                    'description': 'Get applicable regulations for a region',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'region': {
                                'type_': 'STRING',
                                'description': 'Region code (EU, US, ASIA, etc.)'
                            }
                        },
                        'required': ['region']
                    }
                },
                {
                    'name': 'check_regulation_compliance',
                    'description': 'Check if a route complies with a specific regulation',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'regulation_id': {
                                'type_': 'STRING',
                                'description': 'Regulation ID'
                            },
                            'route_data': {
                                'type_': 'OBJECT',
                                'description': 'Route information including emissions'
                            }
                        },
                        'required': ['regulation_id', 'route_data']
                    }
                },
                {
                    'name': 'query_carbon_marketplace',
                    'description': 'Search carbon credit marketplace for offset options',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'quantity_tons': {
                                'type_': 'NUMBER',
                                'description': 'CO2 quantity in metric tons to offset'
                            },
                            'quality_preference': {
                                'type_': 'STRING',
                                'description': 'Preferred quality tier: basic, premium, or verified_removal'
                            }
                        },
                        'required': ['quantity_tons']
                    }
                },
                {
                    'name': 'calculate_credit_cost',
                    'description': 'Calculate total cost for carbon credits including bulk discounts',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'credit_id': {
                                'type_': 'STRING',
                                'description': 'Carbon credit ID'
                            },
                            'quantity_tons': {
                                'type_': 'NUMBER',
                                'description': 'Quantity to purchase in metric tons'
                            }
                        },
                        'required': ['credit_id', 'quantity_tons']
                    }
                }
            ]
        }
    
    def execute_tool(self, function_call) -> Dict:
        """Execute tool calls"""
        tool_name = function_call.name
        tool_input = dict(function_call.args)
        
        print(f"  🔧 Executing tool: {tool_name} with input: {tool_input}")
        
        if tool_name == "get_location_region":
            location = tool_input['location']
            location_data = self.locations_data['locations'].get(location)
            if location_data:
                print(f"  ✅ Found region: {location_data['region']}")
                return {
                    "location": location,
                    "region": location_data['region'],
                    "country": location_data['country']
                }
            return {"error": "Location not found"}
        
        elif tool_name == "find_regulations_by_region":
            region = tool_input['region']
            region_data = self.regulations_data['regions'].get(region)
            if region_data:
                print(f"  ✅ Found {len(region_data['policies'])} regulations")
                return region_data
            return {"error": "Region not found"}
        
        elif tool_name == "check_regulation_compliance":
            regulation_id = tool_input['regulation_id']
            route_data = tool_input['route_data']
            
            # Search for regulation across all regions
            for region_name, region_data in self.regulations_data['regions'].items():
                for policy in region_data['policies']:
                    if policy['id'] == regulation_id:
                        # Simulate compliance check
                        emissions_kg = route_data.get('total_emissions_kg', 0)
                        
                        result = {
                            "regulation_id": regulation_id,
                            "regulation_name": policy['name'],
                            "compliant": True,
                            "costs": {},
                            "penalties": {},
                            "subsidies": {}
                        }
                        
                        # Check thresholds
                        if 'threshold_tons_co2' in policy:
                            threshold_kg = policy['threshold_tons_co2'] * 1000
                            if emissions_kg > threshold_kg:
                                result['compliant'] = False
                                overage_tons = (emissions_kg - threshold_kg) / 1000
                                
                                if 'cost_per_ton_eur' in policy:
                                    cost = overage_tons * policy['cost_per_ton_eur']
                                    result['costs']['ets_cost_eur'] = round(cost, 2)
                                elif 'penalty_per_ton_usd' in policy:
                                    penalty = overage_tons * policy['penalty_per_ton_usd']
                                    result['penalties']['penalty_usd'] = round(penalty, 2)
                        
                        # Check for subsidies
                        if policy.get('type') == 'subsidy':
                            modes = route_data.get('modes', [])
                            if any(m in policy.get('modes_eligible', []) for m in modes):
                                base_cost = route_data.get('base_cost_usd', 0)
                                subsidy_pct = policy.get('subsidy_percentage', 0)
                                subsidy = (base_cost * subsidy_pct / 100)
                                max_subsidy = policy.get('max_subsidy_eur', subsidy)
                                result['subsidies']['green_corridor_eur'] = min(subsidy, max_subsidy)
                        
                        print(f"  ✅ Compliance check: {result['compliant']}")
                        return result
            
            return {"error": "Regulation not found"}
        
        elif tool_name == "query_carbon_marketplace":
            quantity_tons = float(tool_input['quantity_tons'])
            quality_pref = tool_input.get('quality_preference', 'premium')
            
            # Filter credits by quality tier
            matching_credits = [
                credit for credit in self.marketplace_data['available_credits']
                if credit['quality_tier'] == quality_pref
                and credit['min_quantity_tons'] <= quantity_tons
                and credit['inventory_available_tons'] >= quantity_tons
            ]
            
            # If no exact match, broaden search
            if not matching_credits:
                matching_credits = [
                    credit for credit in self.marketplace_data['available_credits']
                    if credit['min_quantity_tons'] <= quantity_tons
                    and credit['inventory_available_tons'] >= quantity_tons
                ]
            
            # Sort by rating and price
            matching_credits.sort(key=lambda x: (-x['rating'], x['price_per_ton_usd']))
            
            result = {
                "quantity_requested_tons": quantity_tons,
                "credits_found": len(matching_credits),
                "top_recommendations": matching_credits[:3],
                "market_status": self.marketplace_data['marketplace_status']
            }
            
            print(f"  ✅ Found {len(matching_credits)} matching credits")
            return result
        
        elif tool_name == "calculate_credit_cost":
            credit_id = tool_input['credit_id']
            quantity_tons = float(tool_input['quantity_tons'])
            
            # Find credit
            credit = None
            for c in self.marketplace_data['available_credits']:
                if c['id'] == credit_id:
                    credit = c
                    break
            
            if not credit:
                return {"error": "Credit not found"}
            
            # Calculate base cost
            base_cost = credit['price_per_ton_usd'] * quantity_tons
            
            # Apply bulk discount
            discount_pct = 0
            for tier in self.marketplace_data['bulk_discounts']:
                if tier['min_quantity_tons'] <= quantity_tons <= tier['max_quantity_tons']:
                    discount_pct = tier['discount_pct']
                    break
            
            discount_amount = base_cost * (discount_pct / 100)
            final_cost = base_cost - discount_amount
            
            result = {
                "credit_id": credit_id,
                "credit_name": credit['name'],
                "quantity_tons": quantity_tons,
                "price_per_ton_usd": credit['price_per_ton_usd'],
                "base_cost_usd": round(base_cost, 2),
                "bulk_discount_pct": discount_pct,
                "discount_amount_usd": round(discount_amount, 2),
                "final_cost_usd": round(final_cost, 2),
                "certification": credit['certification'],
                "co_benefits": credit['co_benefits']
            }
            
            print(f"  ✅ Calculated cost: ${final_cost:.2f}")
            return result
        
        return {"error": "Unknown tool"}
    
    async def execute(self, input_data: Dict) -> Dict:
        """Main execution method"""
        
        user_message = f"""Analyze regulatory compliance for these routes:
{json.dumps(input_data, indent=2)}

For each route:
1. Identify applicable regulations based on origin/destination
2. Check compliance with emission limits
3. Calculate regulatory costs (taxes, ETS payments)
4. Identify available subsidies
5. **IMPORTANT**: If route exceeds limits, query carbon marketplace and recommend credit purchase
6. Calculate total compliance cost including carbon credits if needed

Return structured JSON with complete analysis."""

        try:
            model_with_tools = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                tools=self.get_tools(),
                generation_config={"temperature": 0.1},
                system_instruction=self.get_system_prompt()
            )
            
            chat = model_with_tools.start_chat()
            print(f"  📤 Sending data to Policy Agent...")
            response = chat.send_message(user_message)
            
            # Agent loop
            iteration = 0
            max_iterations = 15  # More iterations for complex marketplace queries
            
            while iteration < max_iterations:
                iteration += 1
                print(f"  🔄 Iteration {iteration}/{max_iterations}")
                
                has_function_call = False
                try:
                    if (response.candidates and 
                        len(response.candidates) > 0 and 
                        response.candidates[0].content.parts):
                        
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'function_call') and part.function_call and part.function_call.name:
                                has_function_call = True
                                break
                except Exception as e:
                    print(f"  ⚠️  Error checking for function calls: {e}")
                
                if has_function_call:
                    print(f"  🔧 Model wants to call functions...")
                    function_calls = []
                    
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call') and part.function_call and part.function_call.name:
                            function_call = part.function_call
                            result = self.execute_tool(function_call)
                            
                            function_response = content_types.FunctionResponse(
                                name=function_call.name,
                                response={"result": result}
                            )
                            function_calls.append(function_response)
                    
                    response = chat.send_message(function_calls)
                else:
                    # Done
                    print(f"  ✅ Policy Agent completed")
                    final_text = response.text
                    
                    try:
                        result_data = json.loads(final_text)
                    except:
                        import re
                        json_match = re.search(r'\{.*\}', final_text, re.DOTALL)
                        if json_match:
                            try:
                                result_data = json.loads(json_match.group())
                            except:
                                result_data = {"routes_analyzed": [], "analysis": final_text}
                        else:
                            result_data = {"routes_analyzed": [], "analysis": final_text}
                    
                    return {
                        "agent": "policy",
                        "data": result_data,
                        "raw_response": final_text,
                        "conversation_length": iteration
                    }
            
            return {"agent": "policy", "error": "Max iterations reached"}
            
        except Exception as e:
            print(f"  ❌ Error in Policy Agent: {e}")
            import traceback
            print(traceback.format_exc())
            return {"agent": "policy", "error": str(e)}