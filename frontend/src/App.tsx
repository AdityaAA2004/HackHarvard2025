import { useState, useEffect } from 'react';
import { Ship, Plane, Truck, Train, Leaf, AlertCircle, CheckCircle, TrendingUp, Clock, DollarSign, Award, Sparkles } from 'lucide-react';
import { apiService, type RouteRequest, type OptimizationResponse, type RecommendedRoute, type AgentMessage } from './services/api';

const icons = {
  ship: Ship,
  plane: Plane,
  truck: Truck,
  train: Train
};

type TransportMode = 'ship' | 'train' | 'plane' | 'truck' | 'air' | 'sea' | 'rail';

export default function CarbonRoutingOrchestrator() {
  const [step, setStep] = useState('input');
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    weight: '',
    priority: 'balanced'
  });
  const [locations, setLocations] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiResponse, setApiResponse] = useState<OptimizationResponse | null>(null);
  
  type AgentKey = 'route' | 'carbon' | 'policy' | 'optimizer';
  const [agentMessages, setAgentMessages] = useState<AgentMessage[]>([]);
  const [currentAgent, setCurrentAgent] = useState<AgentKey | null>(null);

  const agents = {
    route: { name: 'Route Agent', icon: TrendingUp, color: 'bg-blue-500' },
    carbon: { name: 'Carbon Agent', icon: Leaf, color: 'bg-green-500' },
    policy: { name: 'Policy Agent', icon: AlertCircle, color: 'bg-purple-500' },
    optimizer: { name: 'Optimizer Agent', icon: CheckCircle, color: 'bg-orange-500' }
  };

  // Fetch available locations on mount
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const data = await apiService.getAvailableLocations();
        setLocations(data.locations);
      } catch (err) {
        console.error('Failed to fetch locations:', err);
      }
    };
    fetchLocations();
  }, []);

  const handleSubmit = async () => {
    if (!formData.origin || !formData.destination || !formData.weight) {
      setError('Please fill in all fields');
      return;
    }

    setError(null);
    setStep('processing');
    setAgentMessages([]);
    setIsLoading(true);

    try {
      const request: RouteRequest = {
        origin: formData.origin,
        destination: formData.destination,
        weight: parseFloat(formData.weight),
        priority: formData.priority as 'cost' | 'speed' | 'carbon' | 'balanced'
      };

      const response = await apiService.optimizeRoute(request);
      setApiResponse(response);

      // Simulate agent conversation display
      if (response.agent_conversation) {
        for (const msg of response.agent_conversation) {
          await new Promise(resolve => setTimeout(resolve, 800));
          setCurrentAgent(msg.agent);
          setAgentMessages(prev => [...prev, msg]);
        }
      }

      await new Promise(resolve => setTimeout(resolve, 1000));
      setStep('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to optimize route');
      setStep('input');
    } finally {
      setIsLoading(false);
    }
  };

  const getModeIcon = (mode: TransportMode | string) => {
    const modeMap: Record<string, TransportMode> = {
      'sea': 'ship',
      'air': 'plane',
      'rail': 'train',
      'truck': 'truck'
    };
    const iconKey = modeMap[mode] || mode;
    const Icon = icons[iconKey as keyof typeof icons];
    return Icon ? <Icon className="w-5 h-5" /> : null;
  };

  const getRecommendedRoute = (): RecommendedRoute | null => {
    return apiResponse?.recommendation?.recommended_route || null;
  };

  const getAlternatives = (): RecommendedRoute[] => {
    return apiResponse?.recommendation?.alternatives || [];
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Leaf className="w-10 h-10 text-green-400" />
            <h1 className="text-4xl font-bold">Multi-Agent Carbon Routing</h1>
          </div>
          <p className="text-slate-400 text-lg">AI agents collaborate to optimize your supply chain for cost, speed, and sustainability</p>
        </div>

        {error && (
          <div className="max-w-2xl mx-auto mb-6 bg-red-900/50 border border-red-500 rounded-lg p-4 text-red-200">
            {error}
          </div>
        )}

        {step === 'input' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-slate-800 rounded-xl p-8 border border-slate-700">
              <h2 className="text-2xl font-semibold mb-6">Shipment Details</h2>
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Origin</label>
                    <input
                      type="text"
                      value={formData.origin}
                      onChange={(e) => setFormData({...formData, origin: e.target.value})}
                      placeholder="Shanghai"
                      list="origin-locations"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:border-green-500"
                    />
                    <datalist id="origin-locations">
                      {locations.map(loc => (
                        <option key={loc} value={loc} />
                      ))}
                    </datalist>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Destination</label>
                    <input
                      type="text"
                      value={formData.destination}
                      onChange={(e) => setFormData({...formData, destination: e.target.value})}
                      placeholder="Berlin"
                      list="destination-locations"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:border-green-500"
                    />
                    <datalist id="destination-locations">
                      {locations.map(loc => (
                        <option key={loc} value={loc} />
                      ))}
                    </datalist>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Weight (tons)</label>
                  <input
                    type="number"
                    value={formData.weight}
                    onChange={(e) => setFormData({...formData, weight: e.target.value})}
                    placeholder="10"
                    min="0"
                    step="0.1"
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:border-green-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Priority</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:border-green-500"
                  >
                    <option value="cost">Cost Optimized</option>
                    <option value="speed">Speed Optimized</option>
                    <option value="carbon">Carbon Optimized</option>
                    <option value="balanced">Balanced</option>
                  </select>
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={isLoading}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-semibold py-4 rounded-lg transition-colors"
                >
                  {isLoading ? 'Processing...' : 'Start Agent Orchestration'}
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 'processing' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-slate-800 rounded-xl p-8 border border-slate-700">
              <h2 className="text-2xl font-semibold mb-6 text-center">Agent Discussion in Progress</h2>
              
              <div className="space-y-4 mb-8">
                {agentMessages.map((msg, idx) => {
                  const agent = agents[msg.agent];
                  const AgentIcon = agent.icon;
                  
                  return (
                    <div key={idx} className="flex gap-4 items-start animate-fadeIn">
                      <div className={`${agent.color} p-3 rounded-lg shrink-0`}>
                        <AgentIcon className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold mb-1">{agent.name}</div>
                        <div className="text-slate-300 whitespace-pre-line">{msg.message}</div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {currentAgent && (
                <div className="flex items-center justify-center gap-3 text-slate-400">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>{agents[currentAgent].name} is thinking...</span>
                </div>
              )}
            </div>
          </div>
        )}

        {step === 'results' && (
          <div className="space-y-8">
            {getRecommendedRoute() && (
              <div className="bg-gradient-to-r from-green-900/50 to-green-800/50 border-2 border-green-500 rounded-xl p-8">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="text-green-400 text-sm font-semibold mb-2">RECOMMENDED ROUTE</div>
                    <h3 className="text-3xl font-bold">{getRecommendedRoute()!.name}</h3>
                  </div>
                  <div className="flex gap-2">
                    {getRecommendedRoute()!.modes.map((mode, idx) => (
                      <div key={idx} className="bg-green-700 p-3 rounded-lg">
                        {getModeIcon(mode)}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-6 mb-6">
                  <div>
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <DollarSign className="w-4 h-4" />
                      <span className="text-sm">Total Cost</span>
                    </div>
                    <div className="text-2xl font-bold">{formatCurrency(getRecommendedRoute()!.total_cost_usd)}</div>
                    {getRecommendedRoute()!.regulatory_cost_usd !== undefined && getRecommendedRoute()!.regulatory_cost_usd !== 0 && (
                      <div className="text-xs text-slate-400 mt-1">
                        {getRecommendedRoute()!.regulatory_cost_usd! > 0 ? '+' : ''}{formatCurrency(getRecommendedRoute()!.regulatory_cost_usd!)} regulatory
                      </div>
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">Transit Time</span>
                    </div>
                    <div className="text-2xl font-bold">{getRecommendedRoute()!.transit_days} days</div>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <Leaf className="w-4 h-4" />
                      <span className="text-sm">CO2 Emissions</span>
                    </div>
                    <div className="text-2xl font-bold">{getRecommendedRoute()!.total_emissions_kg}kg</div>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm">Compliance</span>
                    </div>
                    <div className="text-sm font-semibold text-green-400">{getRecommendedRoute()!.compliance_status}</div>
                  </div>
                </div>

                {/* Carbon Credit Solution */}
                {getRecommendedRoute()!.carbon_credit_solution?.needed && (
                  <div className="bg-purple-900/30 border border-purple-500/50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Award className="w-5 h-5 text-purple-400" />
                      <h4 className="font-semibold text-purple-300">Carbon Credit Solution</h4>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <div className="text-slate-400">Overage</div>
                        <div className="font-semibold">{getRecommendedRoute()!.carbon_credit_solution!.overage_kg}kg CO2</div>
                      </div>
                      {getRecommendedRoute()!.carbon_credit_solution!.recommended_credit && (
                        <>
                          <div>
                            <div className="text-slate-400">Recommended Credit</div>
                            <div className="font-semibold">{getRecommendedRoute()!.carbon_credit_solution!.recommended_credit.name}</div>
                            <div className="text-xs text-purple-400">{getRecommendedRoute()!.carbon_credit_solution!.recommended_credit.certification}</div>
                          </div>
                          <div>
                            <div className="text-slate-400">Credit Cost</div>
                            <div className="font-semibold">{formatCurrency(getRecommendedRoute()!.carbon_credit_solution!.cost_usd || 0)}</div>
                            <div className="text-xs text-slate-400">
                              {getRecommendedRoute()!.carbon_credit_solution!.recommended_credit.quality_tier} tier
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                    {getRecommendedRoute()!.carbon_credit_solution!.reasoning && (
                      <div className="mt-3 text-sm text-purple-200">
                        {getRecommendedRoute()!.carbon_credit_solution!.reasoning}
                      </div>
                    )}
                  </div>
                )}

                {getRecommendedRoute()!.reasoning && (
                  <div className="mt-4 text-sm text-slate-300">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4 text-green-400" />
                      <span className="font-semibold">Why this route?</span>
                    </div>
                    <p>{getRecommendedRoute()!.reasoning}</p>
                  </div>
                )}
              </div>
            )}

            {getAlternatives().length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4">Alternative Options</h3>
                <div className="grid grid-cols-2 gap-6">
                  {getAlternatives().map((route, idx) => (
                    <div key={idx} className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                      <div className="flex items-start justify-between mb-4">
                        <h4 className="text-lg font-semibold">{route.name}</h4>
                        <div className="flex gap-2">
                          {route.modes.map((mode, i) => (
                            <div key={i} className="bg-slate-700 p-2 rounded">
                              {getModeIcon(mode)}
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Cost:</span>
                          <span className="font-semibold">{formatCurrency(route.total_cost_usd)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Time:</span>
                          <span className="font-semibold">{route.transit_days} days</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Emissions:</span>
                          <span className="font-semibold">{route.total_emissions_kg}kg CO2</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Status:</span>
                          <span className="text-xs text-slate-300">{route.compliance_status}</span>
                        </div>
                        {route.carbon_credit_solution?.needed && (
                          <div className="pt-3 border-t border-slate-700">
                            <div className="flex items-center gap-1 text-purple-400 mb-1">
                              <Award className="w-3 h-3" />
                              <span className="text-xs">Carbon Credits Required</span>
                            </div>
                            <div className="text-xs text-slate-400">
                              {formatCurrency(route.carbon_credit_solution.cost_usd || 0)} for {route.carbon_credit_solution.overage_kg}kg offset
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {apiResponse?.recommendation?.trade_off_analysis && (
              <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                <h3 className="text-xl font-semibold mb-4">Trade-off Analysis</h3>
                <div className="grid grid-cols-3 gap-6 mb-4">
                  <div>
                    <div className="text-sm text-slate-400 mb-2">Cost Range</div>
                    <div className="text-lg font-semibold">
                      {formatCurrency(apiResponse.recommendation.trade_off_analysis.cost_range.min)} - {formatCurrency(apiResponse.recommendation.trade_off_analysis.cost_range.max)}
                    </div>
                    <div className="text-xs text-green-400 mt-1">
                      Save {formatCurrency(apiResponse.recommendation.trade_off_analysis.cost_range.savings_vs_worst)} vs worst
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-400 mb-2">Time Range</div>
                    <div className="text-lg font-semibold">
                      {apiResponse.recommendation.trade_off_analysis.time_range.min} - {apiResponse.recommendation.trade_off_analysis.time_range.max} days
                    </div>
                    <div className="text-xs text-orange-400 mt-1">
                      +{apiResponse.recommendation.trade_off_analysis.time_range.delay_vs_fastest} days vs fastest
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-400 mb-2">Emissions Range</div>
                    <div className="text-lg font-semibold">
                      {apiResponse.recommendation.trade_off_analysis.emissions_range.min} - {apiResponse.recommendation.trade_off_analysis.emissions_range.max}kg
                    </div>
                    <div className="text-xs text-green-400 mt-1">
                      {apiResponse.recommendation.trade_off_analysis.emissions_range.reduction_vs_worst_pct}% reduction vs worst
                    </div>
                  </div>
                </div>
                {apiResponse.recommendation.trade_off_analysis.key_insights && (
                  <div>
                    <div className="text-sm font-semibold mb-2">Key Insights</div>
                    <ul className="space-y-1">
                      {apiResponse.recommendation.trade_off_analysis.key_insights.map((insight, idx) => (
                        <li key={idx} className="text-sm text-slate-300 flex items-start gap-2">
                          <span className="text-green-400 mt-1">•</span>
                          <span>{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <button
              onClick={() => {
                setStep('input');
                setApiResponse(null);
                setAgentMessages([]);
                setFormData({ origin: '', destination: '', weight: '', priority: 'balanced' });
              }}
              className="w-full max-w-md mx-auto block bg-slate-700 hover:bg-slate-600 text-white font-semibold py-3 rounded-lg transition-colors"
            >
              Start New Analysis
            </button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}