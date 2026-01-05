# Telemetry System - Ready to Track! 📊

## ✅ Telemetry System Status

**Status:** ✅ Integrated and Ready  
**Location:** Phase 2 Smart Routing  
**Files:** `app/cost_tracker.py`, `view_telemetry.py`

---

## 📁 What Gets Logged

### 1. Cost Logs (`./data/cost_log.jsonl`)

Every query creates a log entry:

```json
{
  "timestamp": "2026-01-05T15:55:00",
  "user_id": "john@example.com",
  "query": "What is PMI?",
  "route": "template",
  "response_type": "template",
  "tokens_used": {"input": 0, "output": 0, "total": 0},
  "cost": 0.0,
  "metadata": {"template_id": "what_is_pmi"}
}
```

**Tracks:**
- ✅ Timestamp
- ✅ User ID
- ✅ Query text (truncated for privacy)
- ✅ Route taken (template/tool/langgraph/gpt_reasoning)
- ✅ Response type (intent)
- ✅ Token usage
- ✅ Cost in USD
- ✅ Metadata (template ID, intent, etc.)

---

### 2. User Insights (`./data/user_insights.json`)

Per-user personalization data:

```json
{
  "john@example.com": {
    "budget_signals": [
      {"amount": 500000, "timestamp": "2026-01-05T15:55:00"}
    ],
    "location_interests": ["austin", "dallas"],
    "preferences": {
      "cares_about_schools": true,
      "wants_pool": true
    },
    "interaction_count": 15,
    "first_seen": "2026-01-01T10:00:00",
    "last_seen": "2026-01-05T15:55:00"
  }
}
```

**Tracks:**
- ✅ Budget signals (extracted from queries)
- ✅ Location interests
- ✅ Preferences (schools, pools, garages, etc.)
- ✅ Interaction count
- ✅ First/last seen timestamps

---

## 🔍 View Telemetry

### Command:
```bash
py view_telemetry.py
```

### Output:
```
📈 SYSTEM STATISTICS
   Total Queries: 150
   Unique Users: 12
   Total Cost: $2.45
   Avg Cost/Query: $0.0163

🔀 Route Distribution:
   template: 65 (43.3%)
   langgraph: 75 (50.0%)
   tool: 10 (6.7%)

💰 Cost Optimization:
   Optimized Queries: 75
   Estimated Savings: $1.50
   Optimization Rate: 50.0%

📊 COST TELEMETRY LOGS (Last 10)
   [1] 2026-01-05T15:55:00
       User: john@example.com
       Query: What is PMI?
       Route: template
       Cost: $0.0000

🧠 USER INSIGHTS
   👤 User: john@example.com
      Interactions: 15
      Avg Budget: $750,000
      Locations: austin, dallas
      Preferences: {'cares_about_schools': True}
```

---

## 🧪 Test Telemetry

### Step 1: Make Queries in Streamlit

Try these in your running Streamlit app:

```
1. "What is PMI?" → Template (FREE) → Logged
2. "What is HOA?" → Template (FREE) → Logged
3. "Find homes in Austin under 500k" → LangGraph ($0.02) → Logged
```

### Step 2: View Telemetry

```bash
py view_telemetry.py
```

You'll see:
- ✅ 3 queries logged
- ✅ 2 template routes (FREE)
- ✅ 1 langgraph route ($0.02)
- ✅ Total cost: $0.02
- ✅ Optimization rate: 67%
- ✅ User insights extracted (budget: $500k, location: austin)

---

## 📊 Metrics Available

### System-Wide:
- Total queries
- Total cost
- Unique users
- Route distribution
- Optimization rate
- Cost savings

### Per-User:
- Query count
- Total cost
- Average cost per query
- Budget signals
- Location interests
- Preferences

---

## 🎯 Why This Matters

### 1. Cost Control
- See exactly where money is being spent
- Identify expensive queries
- Optimize routing strategies

### 2. User Understanding
- Know what users care about (budget, location, schools)
- Personalize future interactions
- Pre-fill search parameters

### 3. System Optimization
- Track optimization rate
- Measure cost savings
- Identify patterns for new templates

### 4. Business Intelligence
- User engagement metrics
- Popular query types
- Peak usage times

---

## 🚀 Next Steps

### Immediate:
1. Make some queries in Streamlit
2. Run `py view_telemetry.py`
3. See telemetry in action!

### Future Enhancements:
- Build Streamlit dashboard for telemetry
- Add real-time cost monitoring
- Create alerts for high-cost queries
- Export reports (CSV, PDF)
- Add time-series analysis

---

## ✅ Telemetry System Ready!

Your enterprise-grade observability is **live and tracking**! 🎉

**Make a query to see it in action:**
- Open Streamlit (already running)
- Ask: "What is PMI?"
- Run: `py view_telemetry.py`
- See the magic! ✨
