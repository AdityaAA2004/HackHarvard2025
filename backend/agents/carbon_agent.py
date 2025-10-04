"""
Carbon Agent - Calculates emissions (Gemini-powered)
"""
import google.generativeai as genai
from google.generativeai.types import content_types
import json
from typing import Dict
from pathlib import Path


class CarbonAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Load emissions data
        data_dir = Path(__file__).parent.parent / "data"
        with open(data_dir / 'emissions.json') as f:
            self.emissions_data = json.load(f)
    
    def get_system_prompt(self) -> str:
        return """You are the Carbon Agent, an environmental scientist specializing in carbon footprint analysis.

Your responsibilities:
- Calculate total CO2 emissions for each route
- Compare emissions across different transport modes
- Categorize routes by emission levels (low/medium/high)
- Calculate carbon offset costs if needed

Use the emission calculation tools to analyze routes.

Output your analysis as structured JSON with this format:
{
  "routes_analyzed": [
    {
      "route_id": "route_id",
      "total_emissions_kg": 450.5,
      "category": "low",
      "breakdown_by_segment": [...],
      "offset_cost_usd": 11.25
    }
  ],
  "analysis": "Your environmental analysis here"
}"""

    def get_tools(self):
        """Define function declarations for Gemini"""
        
        return {
            'function_declarations': [
                {
                    'name': 'get_emission_factor',
                    'description': 'Get CO2 emission factor for a transport mode',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'mode': {
                                'type_': 'STRING',
                                'description': 'Transport mode: sea, rail, truck, or air'
                            }
                        },
                        'required': ['mode']
                    }
                },
                {
                    'name': 'calculate_segment_emissions',
                    'description': 'Calculate emissions for a route segment',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'mode': {
                                'type_': 'STRING',
                                'description': 'Transport mode'
                            },
                            'distance_km': {
                                'type_': 'NUMBER',
                                'description': 'Distance in kilometers'
                            },
                            'weight_tons': {
                                'type_': 'NUMBER',
                                'description': 'Cargo weight in tons'
                            }
                        },
                        'required': ['mode', 'distance_km', 'weight_tons']
                    }
                },
                {
                    'name': 'get_offset_costs',
                    'description': 'Get carbon offset cost for emissions',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'emissions_kg': {
                                'type_': 'NUMBER',
                                'description': 'Total emissions in kg CO2'
                            },
                            'quality': {
                                'type_': 'STRING',
                                'description': 'Offset quality: standard, premium, or verified_gold'
                            }
                        },
                        'required': ['emissions_kg', 'quality']
                    }
                }
            ]
        }
    
    def execute_tool(self, function_call) -> Dict:
        """Execute tool calls"""
        tool_name = function_call.name
        tool_input = dict(function_call.args)
        
        print(f"  🔧 Executing tool: {tool_name} with input: {tool_input}")
        
        if tool_name == "get_emission_factor":
            mode = tool_input['mode']
            factor = self.emissions_data['emission_factors'].get(mode)
            if factor:
                print(f"  ✅ Found emission factor for {mode}")
                return factor
            return {"error": "Mode not found"}
        
        elif tool_name == "calculate_segment_emissions":
            mode = tool_input['mode']
            distance = float(tool_input['distance_km'])
            weight = float(tool_input['weight_tons'])
            
            factor_data = self.emissions_data['emission_factors'].get(mode)
            if not factor_data:
                return {"error": "Mode not found"}
            
            # Calculate: (gCO2/ton-km) * distance * weight / 1000 = kg CO2
            emissions_kg = (factor_data['gCO2_per_ton_km'] * distance * weight) / 1000
            
            print(f"  ✅ Calculated {emissions_kg:.2f} kg CO2")
            return {
                "mode": mode,
                "distance_km": distance,
                "weight_tons": weight,
                "emissions_kg": round(emissions_kg, 2),
                "emission_factor": factor_data['gCO2_per_ton_km']
            }
        
        elif tool_name == "get_offset_costs":
            emissions_kg = float(tool_input['emissions_kg'])
            quality = tool_input.get('quality', 'standard')
            
            pricing = self.emissions_data['carbon_offset_pricing'].get(quality)
            if not pricing:
                return {"error": "Quality level not found"}
            
            # Convert kg to tons and calculate cost
            emissions_tons = emissions_kg / 1000
            cost = emissions_tons * pricing['usd_per_ton_co2']
            
            print(f"  ✅ Calculated offset cost: ${cost:.2f}")
            return {
                "emissions_kg": emissions_kg,
                "quality": quality,
                "cost_usd": round(cost, 2),
                "certification": pricing['certification']
            }
        
        return {"error": "Unknown tool"}
    
    async def execute(self, route_data: Dict) -> Dict:
        """Main execution method"""
        
        user_message = f"""Analyze the carbon footprint for the following routes:
{json.dumps(route_data, indent=2)}

Use the tools to:
1. Get emission factors for each transport mode
2. Calculate emissions for each route segment
3. Sum total emissions per route
4. Calculate carbon offset costs
5. Categorize routes by emission level

Return structured JSON with your analysis."""

        try:
            model_with_tools = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                tools=self.get_tools(),
                generation_config={"temperature": 0.1},
                system_instruction=self.get_system_prompt()
            )
            
            chat = model_with_tools.start_chat()
            print(f"  📤 Sending routes to Carbon Agent...")
            response = chat.send_message(user_message)
            
            # Agent loop
            iteration = 0
            max_iterations = 10
            
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
                    print(f"  ✅ Carbon Agent completed")
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
                        "agent": "carbon",
                        "data": result_data,
                        "raw_response": final_text,
                        "conversation_length": iteration
                    }
            
            return {"agent": "carbon", "error": "Max iterations reached"}
            
        except Exception as e:
            print(f"  ❌ Error in Carbon Agent: {e}")
            import traceback
            print(traceback.format_exc())
            return {"agent": "carbon", "error": str(e)}