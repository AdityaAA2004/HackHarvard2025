# Multi-Agent Carbon Routing API

AI-powered carbon-optimized shipping route recommendation system using Claude LLM.

## 🏗️ Architecture

```
User Request
    ↓
FastAPI (app.py)
    ↓
Orchestrator
    ↓
┌─────────────────────────────┐
│   4 Specialized Agents      │
│  (Powered by Claude LLM)    │
├─────────────────────────────┤
│  1. Route Agent             │
│  2. Carbon Agent            │
│  3. Policy Agent            │
│  4. Optimizer Agent         │
└─────────────────────────────┘
    ↓
JSON Response
```

## 📁 Project Structure

```
backend/
├── app.py                      # FastAPI entry point
├── orchestrator.py             # Multi-agent coordinator
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── .env.example               # Environment variables template
│
├── agents/
│   ├── route_agent.py         # Finds shipping routes
│   ├── carbon_agent.py        # Calculates emissions
│   ├── policy_agent.py        # Checks compliance
│   └── optimizer_agent.py     # Makes final decision
│
├── api/
│   └── routes.py              # API endpoints
│
└── data/
    ├── routes.json            # Route database
    ├── emissions.json         # Emission factors
    ├── regulations.json       # Policy database
    └── locations.json         # Location data
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Claude API Key (from Anthropic)
- Docker (optional)

### Option 1: Local Development

1. **Clone and setup:**
```bash
git clone <repo>
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your CLAUDE_API_KEY
```

3. **Add JSON data files:**
Place the data files in the `data/` directory:
- `routes.json`
- `emissions.json`
- `regulations.json`
- `locations.json`

4. **Run the server:**
```bash
python app.py
```

5. **Access API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

### Option 2: Docker

1. **Build and run:**
```bash
# Create .env file with CLAUDE_API_KEY
cp .env.example .env

# Build and start
docker-compose up --build
```

2. **Access API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## 📡 API Endpoints

### POST /api/optimize-route
Optimize shipping route using multi-agent system.

**Request:**
```json
{
  "origin": "Shanghai",
  "destination": "Berlin",
  "weight": 10.0,
  "priority": "balanced"
}
```

**Priority Options:**
- `cost` - Minimize total cost
- `speed` - Minimize transit time
- `carbon` - Minimize emissions
- `balanced` - Optimize across all factors

**Response:**
```json
{
  "success": true,
  "recommendation": {
    "recommended_route": {...},
    "alternatives": [...],
    "trade_off_analysis": {...}
  },
  "agent_conversation": [
    {"agent": "route", "message": "..."},
    {"agent": "carbon", "message": "..."},
    {"agent": "policy", "message": "..."},
    {"agent": "optimizer", "message": "..."}
  ]
}
```

### GET /api/health
Health check endpoint.

### GET /api/available-locations
Get list of supported locations.

## 🤖 Agent Details

### 1. Route Agent
- **Role:** Logistics expert
- **Tools:** `search_routes`, `get_location_info`
- **Output:** 3-5 viable route options with segments

### 2. Carbon Agent
- **Role:** Environmental scientist
- **Tools:** `get_emission_factor`, `calculate_segment_emissions`, `get_offset_costs`
- **Output:** Emissions analysis and categorization

### 3. Policy Agent
- **Role:** Compliance expert
- **Tools:** `get_location_region`, `find_regulations_by_region`, `check_regulation_compliance`
- **Output:** Regulatory costs and subsidies

### 4. Optimizer Agent
- **Role:** Strategic coordinator
- **Tools:** None (uses Claude reasoning)
- **Output:** Final recommendation with trade-off analysis

## 🔧 Configuration

### Environment Variables
```bash
CLAUDE_API_KEY=sk-ant-...          # Required: Your Claude API key
API_HOST=0.0.0.0                   # Optional: API host
API_PORT=8000                       # Optional: API port
ENVIRONMENT=development             # Optional: Environment
```

## 🧪 Testing

```bash
# Test with curl
curl -X POST http://localhost:8000/api/optimize-route \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Shanghai",
    "destination": "Berlin",
    "weight": 10,
    "priority": "balanced"
  }'
```

## 📊 Cost Estimation

**Claude Sonnet 4.5 Pricing:**
- Input: $3 per million tokens
- Output: $15 per million tokens

**Estimated per request:** ~$0.10-0.15
- Route Agent: ~$0.02
- Carbon Agent: ~$0.02
- Policy Agent: ~$0.03
- Optimizer Agent: ~$0.04

## 🐛 Troubleshooting

**Issue: API Key Error**
```bash
# Verify API key is set
echo $CLAUDE_API_KEY

# Check .env file exists
cat .env
```

**Issue: Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Issue: Data Files Not Found**
```bash
# Verify data directory structure
ls -la data/
# Should contain: routes.json, emissions.json, regulations.json, locations.json
```

## 📝 Development

**Add new agent:**
1. Create `agents/new_agent.py`
2. Implement agent with Claude API
3. Add to orchestrator
4. Update API routes if needed

**Modify agent prompts:**
Edit the `get_system_prompt()` method in each agent file.

**Add new tools:**
Add to `get_tools()` and implement in `execute_tool()`.

## 🚢 Deployment

**Production checklist:**
- [ ] Set strong CLAUDE_API_KEY
- [ ] Update CORS origins in app.py
- [ ] Set ENVIRONMENT=production
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Add rate limiting
- [ ] Enable HTTPS

## 📄 License

MIT License

## 🤝 Support

For issues and questions:
- Open an issue on GitHub
- Check API docs at `/docs`
- Review agent conversation logs