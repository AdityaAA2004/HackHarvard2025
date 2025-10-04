# Priority Optimization Guide

## 📊 Overview

The system supports 4 optimization priorities that determine how routes are ranked and recommended:

| Priority | Weight Distribution | Use Case |
|----------|-------------------|----------|
| **cost** | 70% cost, 15% time, 15% emissions | Budget-conscious shipping, non-urgent cargo |
| **speed** | 15% cost, 70% time, 15% emissions | Time-sensitive deliveries, perishables |
| **carbon** | 15% cost, 15% time, 70% emissions | Sustainability goals, ESG compliance |
| **balanced** | 33% cost, 33% time, 34% emissions | Equal consideration of all factors |

---

## 🎯 Priority: `cost`

### Weighting
- **Cost: 70%** (dominant factor)
- Time: 15%
- Emissions: 15%

### Behavior
The optimizer will select the route with the **lowest total cost**, including:
- Base shipping cost
- Regulatory compliance costs (ETS, carbon taxes)
- Carbon credit purchases (if route exceeds limits)
- Minus any subsidies (green corridor incentives)

### Example Scenario

**Shanghai → Berlin, 10 tons**

```
Route Options:
1. Sea + Rail: $1,900 total (includes $100 subsidy)
   - 20 days, 450kg CO2
   - Score: 0.95 ⭐ RECOMMENDED

2. Sea + Truck: $2,500 total
   - 18 days, 680kg CO2
   - Score: 0.78

3. Air Direct: $8,150 total (includes $150 carbon offset)
   - 2 days, 4,200kg CO2
   - Score: 0.15

Decision: Choose Sea + Rail ($6,250 savings vs air)
```

### When to Use
✅ Non-urgent cargo  
✅ Budget constraints  
✅ Long-term contracts where cost matters most  
✅ Bulk shipments with flexible timelines  

---

## ⚡ Priority: `speed`

### Weighting
- Cost: 15%
- **Time: 70%** (dominant factor)
- Emissions: 15%

### Behavior
The optimizer will select the route with the **shortest transit time**, even if it costs significantly more or produces higher emissions.

### Example Scenario

**Shanghai → Berlin, 10 tons**

```
Route Options:
1. Air Direct: $8,150 total
   - 2 days, 4,200kg CO2
   - Score: 0.98 ⭐ RECOMMENDED

2. Sea + Truck: $2,500 total
   - 18 days, 680kg CO2
   - Score: 0.35

3. Sea + Rail: $1,900 total
   - 20 days, 450kg CO2
   - Score: 0.30

Decision: Choose Air Direct (18 days faster)
```

### When to Use
✅ Time-critical deliveries  
✅ Perishable goods  
✅ Just-in-time manufacturing  
✅ Emergency shipments  
✅ High-value, low-weight cargo where speed justifies cost  

---

## 🌱 Priority: `carbon`

### Weighting
- Cost: 15%
- Time: 15%
- **Emissions: 70%** (dominant factor)

### Behavior
The optimizer will select the route with the **lowest CO2 emissions**, prioritizing environmental impact over cost and time.

### Example Scenario

**Shanghai → Berlin, 10 tons**

```
Route Options:
1. Sea + Rail: $1,900 total
   - 20 days, 450kg CO2
   - Score: 0.94 ⭐ RECOMMENDED

2. Sea + Truck: $2,500 total
   - 18 days, 680kg CO2
   - Score: 0.67

3. Air Direct: $8,150 total
   - 2 days, 4,200kg CO2
   - Score: 0.08

Decision: Choose Sea + Rail (89% lower emissions vs air)
```

### When to Use
✅ Corporate sustainability commitments  
✅ ESG reporting requirements  
✅ Carbon-neutral shipping programs  
✅ Green marketing initiatives  
✅ Meeting customer sustainability expectations  

---

## ⚖️ Priority: `balanced`

### Weighting
- **Cost: 33%** (equal)
- **Time: 33%** (equal)
- **Emissions: 34%** (equal)

### Behavior
The optimizer will select the route that provides the **best overall value** across all three factors, with no single metric dominating.

### Example Scenario

**Shanghai → Berlin, 10 tons**

```
Route Options:
1. Sea + Rail: $1,900 total
   - 20 days, 450kg CO2
   - Score: 0.87 ⭐ RECOMMENDED
   (Good cost, acceptable time, excellent emissions)

2. Sea + Truck: $2,500 total
   - 18 days, 680kg CO2
   - Score: 0.71
   (Moderate cost, good time, moderate emissions)

3. Air Direct: $8,150 total
   - 2 days, 4,200kg CO2
   - Score: 0.41
   (Poor cost, excellent time, poor emissions)

Decision: Choose Sea + Rail (best overall balance)
```

### When to Use
✅ Standard shipping operations  
✅ When no single factor is critical  
✅ Long-term strategic planning  
✅ Mixed cargo portfolios  
✅ Default recommendation mode  

---

## 🧮 Score Calculation

### Normalization Process

For each metric (cost, time, emissions):

1. **Find range:** `min` and `max` values across all routes
2. **Normalize:** Convert to 0-1 scale where 1 = best
   ```
   score = 1 - (value - min) / (max - min)
   ```
3. **Apply weights:** Multiply by priority weight
4. **Sum:** Total weighted score

### Example Calculation

**Route: Sea + Rail**
- Total cost: $1,900 (min: $1,900, max: $8,150)
- Transit time: 20 days (min: 2, max: 20)
- Emissions: 450kg (min: 450, max: 4,200)

**Balanced Priority:**
```python
# Normalize
cost_score = 1 - (1900 - 1900) / (8150 - 1900) = 1.0
time_score = 1 - (20 - 2) / (20 - 2) = 0.0
emission_score = 1 - (450 - 450) / (4200 - 450) = 1.0

# Apply weights (33%, 33%, 34%)
final_score = 0.33 * 1.0 + 0.33 * 0.0 + 0.34 * 1.0
            = 0.67
```

**Cost Priority:**
```python
# Same normalized scores
# Apply weights (70%, 15%, 15%)
final_score = 0.70 * 1.0 + 0.15 * 0.0 + 0.15 * 1.0
            = 0.85  # Higher because cost is excellent
```

---

## 📈 Trade-off Analysis

The optimizer provides detailed trade-off analysis showing:

### Cost Range
```json
{
  "min": 1900,
  "max": 8150,
  "savings_vs_worst": 6250,
  "spread_pct": 76.7
}
```

### Time Range
```json
{
  "min": 2,
  "max": 20,
  "delay_vs_fastest": 18,
  "spread_pct": 90.0
}
```

### Emissions Range
```json
{
  "min": 450,
  "max": 4200,
  "reduction_vs_worst_pct": 89.3,
  "spread_pct": 89.3
}
```

### Key Insights
The system automatically generates insights like:
- "Recommended route saves $6,250 (76%) vs most expensive"
- "89% lower emissions than air freight"
- "18 days slower than air (acceptable for non-urgent cargo)"
- "Qualifies for $100 green corridor subsidy"
- "Compliant with all regulations without additional offsets"

---

## 🎛️ Using Priorities in API

### Request Format

```bash
curl -X POST http://localhost:8000/api/optimize-route \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Shanghai",
    "destination": "Berlin",
    "weight": 10,
    "priority": "balanced"
  }'
```

### Changing Priority

Simply change the `priority` field:

**Cost-optimized:**
```json
{"priority": "cost"}
```

**Speed-optimized:**
```json
{"priority": "speed"}
```

**Carbon-optimized:**
```json
{"priority": "carbon"}
```

**Balanced:**
```json
{"priority": "balanced"}
```

---

## 🔍 Priority Comparison Matrix

| Scenario | cost | speed | carbon | balanced |
|----------|------|-------|--------|----------|
| **Recommended Route** | Sea+Rail | Air | Sea+Rail | Sea+Rail |
| **Total Cost** | $1,900 | $8,150 | $1,900 | $1,900 |
| **Transit Days** | 20 | 2 | 20 | 20 |
| **CO2 Emissions** | 450kg | 4,200kg | 450kg | 450kg |
| **Score** | 0.95 | 0.98 | 0.94 | 0.87 |
| **Trade-off** | Slowest but cheapest | Fastest but expensive | Slowest but greenest | Best overall |

---

## 💡 Best Practices

### For Shippers

1. **Default to balanced** for most shipments
2. **Use cost** for bulk, non-urgent cargo (e.g., raw materials)
3. **Use speed** for perishables or urgent replenishment
4. **Use carbon** for sustainability reporting periods

### For Logistics Managers

1. **Mix priorities** across shipment portfolio
2. **Use cost** for 60-70% of volume (bulk shipments)
3. **Use speed** for 10-15% of volume (urgent orders)
4. **Use carbon** for 10-15% of volume (sustainability showcase)
5. **Use balanced** for 10-20% of volume (standard orders)

### For Sustainability Officers

1. **Start with balanced** to understand baseline
2. **Switch to carbon** to see maximum emission reduction
3. **Analyze trade-offs** (cost and time impact)
4. **Set targets** (e.g., 50% of routes on carbon priority by 2025)

---

## 🧪 Testing Different Priorities

Run the same route with all priorities to compare:

```bash
# Test Cost Priority
curl -X POST http://localhost:8000/api/optimize-route \
  -d '{"origin":"Shanghai","destination":"Berlin","weight":10,"priority":"cost"}'

# Test Speed Priority  
curl -X POST http://localhost:8000/api/optimize-route \
  -d '{"origin":"Shanghai","destination":"Berlin","weight":10,"priority":"speed"}'

# Test Carbon Priority
curl -X POST http://localhost:8000/api/optimize-route \
  -d '{"origin":"Shanghai","destination":"Berlin","weight":10,"priority":"carbon"}'

# Test Balanced Priority
curl -X POST http://localhost:8000/api/optimize-route \
  -d '{"origin":"Shanghai","destination":"Berlin","weight":10,"priority":"balanced"}'
```

Compare the `recommended_route`, `score`, and `reasoning` fields to see how each priority affects the decision.

---

## 📊 Priority Impact Summary

| Priority | Recommended Route Type | Typical Cost | Typical Time | Typical Emissions |
|----------|----------------------|--------------|--------------|-------------------|
| **cost** | Sea + Rail/Truck | Lowest | Longest | Low-Medium |
| **speed** | Air Direct | Highest | Shortest | Highest |
| **carbon** | Sea + Rail | Low | Long | Lowest |
| **balanced** | Sea + Rail/Truck | Low-Medium | Medium-Long | Low-Medium |

**Key Takeaway:** The priority system ensures the optimizer recommends routes that align with your business objectives, whether that's minimizing costs, meeting delivery deadlines, achieving sustainability goals, or finding the best overall balance.