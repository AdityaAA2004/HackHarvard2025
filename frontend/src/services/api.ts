// API Service for backend communication

const API_URL = import.meta.env.VITE_API_URL || 'http://backend:8000';

export interface RouteRequest {
  origin: string;
  destination: string;
  weight: number;
  priority: 'cost' | 'speed' | 'carbon' | 'balanced';
}

export interface CarbonCredit {
  id: string;
  name: string;
  type: string;
  price_per_ton_usd: number;
  quality_tier: string;
  certification: string;
  rating: number;
}

export interface CarbonCreditSolution {
  needed: boolean;
  overage_kg?: number;
  recommended_credit?: CarbonCredit;
  cost_usd?: number;
  reasoning?: string;
}

export interface RouteCompliance {
  route_id: string;
  compliance_status: string;
  regulations_applicable: any[];
  regulatory_costs: any;
  subsidies_available: any;
  carbon_credit_solution?: CarbonCreditSolution;
  total_compliance_cost: number;
}

export interface RouteEmissions {
  route_id: string;
  total_emissions_kg: number;
  category: string;
  breakdown_by_segment: any[];
  offset_cost_usd?: number;
}

export interface RouteOption {
  id: string;
  name: string;
  modes: string[];
  segments: any[];
  base_cost_usd: number;
  transit_days: number;
  reliability_score: number;
}

export interface RecommendedRoute extends RouteOption {
  total_cost_usd: number;
  total_emissions_kg: number;
  compliance_status: string;
  regulatory_cost_usd?: number;
  score?: number;
  reasoning?: string;
  carbon_credit_solution?: CarbonCreditSolution;
}

export interface TradeOffAnalysis {
  cost_range: {
    min: number;
    max: number;
    savings_vs_worst: number;
    spread_pct?: number;
  };
  time_range: {
    min: number;
    max: number;
    delay_vs_fastest: number;
    spread_pct?: number;
  };
  emissions_range: {
    min: number;
    max: number;
    reduction_vs_worst_pct: number;
    spread_pct?: number;
  };
  key_insights: string[];
}

export interface AgentMessage {
  agent: 'route' | 'carbon' | 'policy' | 'optimizer';
  message: string;
  data?: any;
}

export interface OptimizationResponse {
  success: boolean;
  recommendation?: {
    routes?: {
      routes_found: RouteOption[];
      analysis?: string;
    };
    emissions?: {
      routes_analyzed: RouteEmissions[];
      analysis?: string;
    };
    compliance?: {
      routes_analyzed: RouteCompliance[];
      analysis?: string;
    };
    recommended_route?: RecommendedRoute;
    alternatives?: RecommendedRoute[];
    trade_off_analysis?: TradeOffAnalysis;
  };
  agent_conversation?: AgentMessage[];
  request?: RouteRequest;
  error?: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  agents: string[];
}

export interface LocationsResponse {
  locations: string[];
  count: number;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  async optimizeRoute(request: RouteRequest): Promise<OptimizationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/optimize-route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error optimizing route:', error);
      throw error;
    }
  }

  async checkHealth(): Promise<HealthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }

  async getAvailableLocations(): Promise<LocationsResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/available-locations`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching locations:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();