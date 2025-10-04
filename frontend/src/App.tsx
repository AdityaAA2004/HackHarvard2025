import { useState } from 'react';
import { Ship, Plane, Truck, Train, Leaf, AlertCircle, CheckCircle, TrendingUp, Clock, DollarSign } from 'lucide-react';

const icons = {
  ship: Ship,
  plane: Plane,
  truck: Truck,
  train: Train
};
type TransportMode = 'ship' | 'train' | 'plane' | 'truck';
export default function CarbonRoutingOrchestrator() {
  const [step, setStep] = useState('input');
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    weight: '',
    priority: 'balanced'
  });
  type AgentKey = keyof typeof agents;
  const [agentMessages, setAgentMessages] = useState<{ agent: AgentKey; message: string; delay: number; }[]>([]);
  const [currentAgent, setCurrentAgent] = useState<AgentKey | null>(null);

  const agents = {
    route: { name: 'Route Agent', icon: TrendingUp, color: 'bg-blue-500' },
    carbon: { name: 'Carbon Agent', icon: Leaf, color: 'bg-green-500' },
    policy: { name: 'Policy Agent', icon: AlertCircle, color: 'bg-purple-500' },
    optimizer: { name: 'Optimizer Agent', icon: CheckCircle, color: 'bg-orange-500' }
  };

  const mockAgentConversation: { agent: AgentKey; message: string; delay: number; }[] = [
    {
      agent: 'route',
      message: 'Analyzing route options from Shanghai to Berlin...',
      delay: 500
    },
    {
      agent: 'route',
      message: 'Found 3 viable routes:\n1. Sea Freight → Rail (20 days, $2,000)\n2. Air Freight Direct (2 days, $8,000)\n3. Sea Freight → Truck (18 days, $2,500)',
      delay: 1500
    },
    {
      agent: 'carbon',
      message: 'Calculating carbon footprint for each route...',
      delay: 800
    },
    {
      agent: 'carbon',
      message: 'Emissions Analysis:\n• Sea→Rail: 450kg CO2 ✅ (Lowest)\n• Air Direct: 4,200kg CO2 ❌ (9.3x higher)\n• Sea→Truck: 680kg CO2 ⚠️ (Medium)',
      delay: 1800
    },
    {
      agent: 'policy',
      message: 'Checking regulatory compliance across jurisdictions...',
      delay: 700
    },
    {
      agent: 'policy',
      message: 'Policy Review:\n• EU ETS applies to all routes\n• Air route requires carbon offset: €150\n• Rail route qualifies for green corridor subsidy: -€100\n• All routes compliant with regulations',
      delay: 1600
    },
    {
      agent: 'optimizer',
      message: 'Synthesizing inputs and balancing trade-offs...',
      delay: 900
    },
    {
      agent: 'optimizer',
      message: '🎯 FINAL RECOMMENDATION: Sea Freight → Rail\n\nRationale:\n• 89% lower emissions vs air freight\n• Cost-effective: $1,900 (with green subsidy)\n• Regulatory compliant with bonus credits\n• Trade-off: +18 days transit vs air (acceptable for non-urgent cargo)',
      delay: 2000
    }
  ];

  const results = {
    recommended: {
      name: 'Sea Freight → Rail',
      mode: ['ship', 'train'],
      cost: 1900,
      days: 20,
      emissions: 450,
      compliance: 'Full Compliance + Green Subsidy'
    },
    alternatives: [
      {
        name: 'Air Freight Direct',
        mode: ['plane'],
        cost: 8150,
        days: 2,
        emissions: 4200,
        compliance: 'Compliant (with offset)'
      },
      {
        name: 'Sea Freight → Truck',
        mode: ['ship', 'truck'],
        cost: 2500,
        days: 18,
        emissions: 680,
        compliance: 'Compliant'
      }
    ]
  };

  const handleSubmit = async () => {
    if (!formData.origin || !formData.destination || !formData.weight) {
      alert('Please fill in all fields');
      return;
    }
    
    setStep('processing');
    setAgentMessages([]);
    
    for (const msg of mockAgentConversation) {
      await new Promise(resolve => setTimeout(resolve, msg.delay));
      setCurrentAgent(msg.agent);
      setAgentMessages(prev => [...prev, msg]);
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    setStep('results');
  };

  const getModeIcon = (mode: TransportMode | string) => {

    const Icon = icons[mode as TransportMode];
    return <Icon className="w-5 h-5" />;
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
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:border-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Destination</label>
                    <input
                      type="text"
                      value={formData.destination}
                      onChange={(e) => setFormData({...formData, destination: e.target.value})}
                      placeholder="Berlin"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:border-green-500"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Weight (tons)</label>
                  <input
                    type="number"
                    value={formData.weight}
                    onChange={(e) => setFormData({...formData, weight: e.target.value})}
                    placeholder="10"
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
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-4 rounded-lg transition-colors"
                >
                  Start Agent Orchestration
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
            <div className="bg-gradient-to-r from-green-900/50 to-green-800/50 border-2 border-green-500 rounded-xl p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="text-green-400 text-sm font-semibold mb-2">RECOMMENDED ROUTE</div>
                  <h3 className="text-3xl font-bold">{results.recommended.name}</h3>
                </div>
                <div className="flex gap-2">
                  {results.recommended.mode.map((mode, idx) => (
                    <div key={idx} className="bg-green-700 p-3 rounded-lg">
                      {getModeIcon(mode)}
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-4 gap-6">
                <div>
                  <div className="flex items-center gap-2 text-slate-400 mb-2">
                    <DollarSign className="w-4 h-4" />
                    <span className="text-sm">Total Cost</span>
                  </div>
                  <div className="text-2xl font-bold">${results.recommended.cost}</div>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-slate-400 mb-2">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">Transit Time</span>
                  </div>
                  <div className="text-2xl font-bold">{results.recommended.days} days</div>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-slate-400 mb-2">
                    <Leaf className="w-4 h-4" />
                    <span className="text-sm">CO2 Emissions</span>
                  </div>
                  <div className="text-2xl font-bold">{results.recommended.emissions}kg</div>
                </div>
                <div>
                  <div className="flex items-center gap-2 text-slate-400 mb-2">
                    <CheckCircle className="w-4 h-4" />
                    <span className="text-sm">Compliance</span>
                  </div>
                  <div className="text-sm font-semibold text-green-400">{results.recommended.compliance}</div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-4">Alternative Options</h3>
              <div className="grid grid-cols-2 gap-6">
                {results.alternatives.map((route, idx) => (
                  <div key={idx} className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-start justify-between mb-4">
                      <h4 className="text-lg font-semibold">{route.name}</h4>
                      <div className="flex gap-2">
                        {route.mode.map((mode, i) => (
                          <div key={i} className="bg-slate-700 p-2 rounded">
                            {getModeIcon(mode)}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Cost:</span>
                        <span className="font-semibold">${route.cost}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Time:</span>
                        <span className="font-semibold">{route.days} days</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Emissions:</span>
                        <span className="font-semibold">{route.emissions}kg CO2</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Status:</span>
                        <span className="text-xs text-slate-300">{route.compliance}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={() => setStep('input')}
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