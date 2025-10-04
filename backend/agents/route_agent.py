"""
Route Agent - Finds optimal shipping routes (Gemini-powered)
"""
import google.generativeai as genai
from google.generativeai.types import content_types
import json
from typing import Dict, List
from pathlib import Path


class RouteAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Load route and location data
        data_dir = Path(__file__).parent.parent / "data"
        with open(data_dir / 'routes.json') as f:
            self.routes_data = json.load(f)
        with open(data_dir / 'locations.json') as f:
            self.locations_data = json.load(f)
    
    def get_system_prompt(self) -> str:
        return """You are the Route Agent, a logistics expert specializing in finding optimal shipping routes.

Your responsibilities:
- Find 3-5 viable route options between locations
- Consider distance, transit time, and base costs
- Use available infrastructure (ports, airports, rail terminals)
- Provide multi-modal transport combinations

When the user asks you to search routes, use the search_routes function.
When checking infrastructure, use the get_location_info function.

Output your analysis as structured JSON with this format:
{
  "routes_found": [
    {
      "id": "route_id",
      "name": "Route Name",
      "modes": ["sea", "rail"],
      "segments": [...],
      "total_cost_usd": 2000,
      "transit_days": 17,
      "reliability_score": 0.92
    }
  ],
  "analysis": "Your reasoning here"
}"""

    def get_tools(self):
        """Define function declarations for Gemini using correct format"""
        
        search_routes_func = {
            'function_declarations': [
                {
                    'name': 'search_routes',
                    'description': 'Search for available routes between origin and destination',
                    'parameters': {
                        'type_': 'OBJECT',
                        'properties': {
                            'origin': {
                                'type_': 'STRING',
                                'description': 'Origin city'
                            },
                            'destination': {
                                'type_': 'STRING',
                                'description': 'Destination city'
                            }
                        },
                        'required': ['origin', 'destination']
                    }
                },
                {
                    'name': 'get_location_info',
                    'description': 'Get infrastructure details for a location (ports, airports, rail)',
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
                }
            ]
        }
        
        return search_routes_func
    
    def execute_tool(self, function_call) -> Dict:
        """Execute tool calls"""
        tool_name = function_call.name
        tool_input = dict(function_call.args)
        
        print(f"  🔧 Executing tool: {tool_name} with input: {tool_input}")
        
        if tool_name == "search_routes":
            for route in self.routes_data['routes']:
                if (route['origin'] == tool_input['origin'] and 
                    route['destination'] == tool_input['destination']):
                    print(f"  ✅ Found route with {len(route['options'])} options")
                    return route
            print(f"  ❌ No routes found for {tool_input}")
            return {"error": "No routes found", "searched": tool_input}
        
        elif tool_name == "get_location_info":
            location = self.locations_data['locations'].get(tool_input['location'])
            if location:
                print(f"  ✅ Found location info for {tool_input['location']}")
                return location
            print(f"  ❌ Location not found: {tool_input['location']}")
            return {"error": "Location not found", "searched": tool_input['location']}
        
        return {"error": "Unknown tool"}
    
    async def execute(self, user_input: Dict) -> Dict:
        """Main execution method"""
        
        user_message = f"""Find optimal shipping routes for:
Origin: {user_input['origin']}
Destination: {user_input['destination']}
Weight: {user_input['weight']} tons
Priority: {user_input['priority']}

Use the search_routes function to find available routes, then analyze them.
Return your findings as structured JSON."""

        try:
            # Create model with tools
            model_with_tools = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                tools=self.get_tools(),
                generation_config={
                    "temperature": 0.1,
                },
                system_instruction=self.get_system_prompt()
            )
            
            # Start chat
            chat = model_with_tools.start_chat()
            
            print(f"  📤 Sending initial message to Gemini...")
            response = chat.send_message(user_message)
            
            # Agent loop with function calling
            iteration = 0
            max_iterations = 10
            
            while iteration < max_iterations:
                iteration += 1
                print(f"  🔄 Iteration {iteration}/{max_iterations}")
                
                # Check if model wants to call functions
                has_function_call = False
                
                # Safely check for function calls
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
                    has_function_call = False
                
                if has_function_call:
                    print(f"  🔧 Model wants to call functions...")
                    function_calls = []
                    
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call') and part.function_call and part.function_call.name:
                            function_call = part.function_call
                            
                            # Execute the function
                            result = self.execute_tool(function_call)
                            
                            # Create function response
                            function_response = content_types.FunctionResponse(
                                name=function_call.name,
                                response={"result": result}
                            )
                            
                            function_calls.append(function_response)
                    
                    # Send function results back to model
                    print(f"  📤 Sending function results back to model...")
                    response = chat.send_message(function_calls)
                else:
                    # Model is done, extract final response
                    print(f"  ✅ Model completed, extracting response...")
                    final_text = response.text
                    
                    # Try to parse JSON
                    try:
                        result_data = json.loads(final_text)
                        print(f"  ✅ Successfully parsed JSON response")
                    except Exception as e:
                        print(f"  ⚠️  Failed to parse JSON: {e}")
                        # If not valid JSON, try to extract JSON from text
                        import re
                        json_match = re.search(r'\{.*\}', final_text, re.DOTALL)
                        if json_match:
                            try:
                                result_data = json.loads(json_match.group())
                                print(f"  ✅ Extracted and parsed JSON from response")
                            except:
                                print(f"  ❌ Could not parse extracted JSON")
                                result_data = {"routes_found": [], "analysis": final_text}
                        else:
                            print(f"  ❌ No JSON found in response")
                            result_data = {"routes_found": [], "analysis": final_text}
                    
                    return {
                        "agent": "route",
                        "data": result_data,
                        "raw_response": final_text,
                        "conversation_length": iteration
                    }
            
            print(f"  ⚠️  Reached max iterations")
            return {"agent": "route", "error": "Max iterations reached"}
            
        except Exception as e:
            print(f"  ❌ Error in Route Agent: {e}")
            import traceback
            print(traceback.format_exc())
            return {"agent": "route", "error": str(e)}