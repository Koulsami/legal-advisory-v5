# Local Testing Guide

## 🧪 Test Your Backend Locally

This guide shows you how to test your Legal Advisory System backend locally using the test frontend.

---

## Quick Start (2 Steps)

### Step 1: Start the Backend

In WSL terminal:

```bash
cd /home/claude/legal-advisory-v5
./run_backend_local.sh
```

You should see:
```
🚀 Starting backend server...
   API will be available at: http://localhost:8000
   API docs: http://localhost:8000/docs
   Health check: http://localhost:8000/health

📄 Open test_frontend.html in your browser to test!
```

**Keep this terminal open** - the server is running!

---

### Step 2: Open the Test Frontend

**Option A: From Windows**

1. Open Windows Explorer
2. Navigate to: `\\wsl$\Ubuntu\home\claude\legal-advisory-v5\`
3. Double-click `test_frontend.html`
4. Your browser should open with the test interface

**Option B: From WSL**

```bash
# Copy to Windows Downloads folder
cp /home/claude/legal-advisory-v5/test_frontend.html /mnt/c/Users/Samee/Downloads/

# Then open from Windows Downloads in your browser
```

**Option C: Direct path in browser**

Open your browser and paste:
```
file:///home/claude/legal-advisory-v5/test_frontend.html
```

---

## Using the Test Frontend

### Interface Overview

The test page has two panels:

**Left Panel - Input:**
- Natural language query input
- Example queries (click to load)
- Structured input fields (court level, amount)
- Two calculate buttons

**Right Panel - Results:**
- **Formatted tab**: Pretty display of results
- **JSON Response tab**: Raw API response
- **Debug Info tab**: Request/response for debugging

---

### Test Queries

Click the example buttons or type:

**1. High Court Default Judgment - $50k**
```
Calculate costs for a High Court default judgment with $50,000
```

**Expected:** $4,000 (range: $3,000 - $5,000)

**2. District Court Summary Judgment - $80k**
```
District Court summary judgment for $80,000
```

**Expected:** $4,875 (range: $3,250 - $6,500)

**3. Magistrates Court - $15k**
```
Magistrates Court default judgment for $15,000
```

**Expected:** ~$900 (range varies)

**4. High Court Trial - $100k**
```
High Court contested trial of 3 days with claim of $100,000
```

**Expected:** Higher costs with trial day adjustments

---

## Tracing Code Flow

### 1. API Endpoint Flow

**Frontend → Backend:**

```
test_frontend.html
  │
  ├─ fetch('http://localhost:8000/calculate')
  │
  └─ POST { "query": "Calculate costs..." }
```

**Backend Processing:**

```
backend/api/routes.py
  │
  ├─ @app.post("/calculate")
  │   └─ direct_calculate(request)
  │
  ├─ Pattern Extraction
  │   └─ backend/common_services/pattern_extractor.py
  │       └─ extract_all(query)
  │
  ├─ Order 21 Calculation
  │   └─ backend/modules/order_21/order21_module.py
  │       └─ calculate(filled_fields)
  │
  └─ Return DirectCalculationResponse
```

### 2. File Locations

| Component | File Path |
|-----------|-----------|
| API Endpoint | `backend/api/routes.py` line 407-466 |
| Pattern Extractor | `backend/common_services/pattern_extractor.py` |
| Order 21 Module | `backend/modules/order_21/order21_module.py` |
| Order 21 Logic Tree | `backend/modules/order_21/tree_data.py` |
| Test Frontend | `test_frontend.html` |

### 3. Debug with Logs

The backend logs show each step:

```bash
# Watch logs in real-time
./run_backend_local.sh

# In another terminal, make a request, then check logs:
tail -f logs/backend.log  # if logging to file
```

Example log output:
```
INFO: Direct calculation request: Calculate costs for High Court...
INFO: Extracted fields: {'court_level': 'High Court', 'claim_amount': 50000, ...}
INFO: Calculation result: Total=$4000
```

---

## API Documentation

While the backend is running, visit:

**Interactive API Docs:**
```
http://localhost:8000/docs
```

This shows:
- All available endpoints
- Request/response schemas
- "Try it out" feature to test directly

**Alternative docs:**
```
http://localhost:8000/redoc
```

---

## Test Different Scenarios

### Scenario 1: Extract Different Courts

```javascript
// High Court
"Calculate costs for a High Court default judgment with $50,000"

// District Court (should be 65% of High Court)
"Calculate costs for a District Court default judgment with $50,000"

// Magistrates Court (should be 45% of High Court)
"Calculate costs for a Magistrates Court default judgment with $50,000"
```

**Compare the results** - District should be ~65% and Magistrates ~45% of High Court.

### Scenario 2: Extract Different Case Types

```javascript
// Default judgment
"High Court default judgment for $50,000"

// Summary judgment
"High Court summary judgment for $50,000"

// Contested trial
"High Court contested trial for $50,000"
```

### Scenario 3: Test Extraction

```javascript
// Explicit details
"Calculate costs for a High Court default judgment with claim amount of $50,000"

// Implicit details (should still extract)
"I won a High Court case for $50,000. What are my costs?"

// Missing information (should error)
"Calculate costs for a High Court case"
// Expected error: "Could not extract claim amount"
```

---

## Debugging Tips

### Issue: "Cannot connect to API"

**Check:**
1. Backend server is running (`./run_backend_local.sh`)
2. No errors in terminal where backend is running
3. Port 8000 is not in use by another app

**Test:**
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "5.0.0",
  "components": {...}
}
```

### Issue: "Calculation failed"

**Check the Debug Info tab** in test frontend:
- Look at the request sent
- Look at the error response
- Check what was extracted

**Common issues:**
- No claim amount in query
- Typo in court level name
- Invalid case type

### Issue: Wrong calculation results

**Check:**
1. What was extracted (Debug tab → extracted_info)
2. Calculation steps in response
3. Rules applied

**Compare with:**
- `backend/modules/order_21/tree_data.py` for expected costs
- Order 21 rules documentation

---

## Testing the Full Flow

### End-to-End Test

1. **Start backend**
   ```bash
   ./run_backend_local.sh
   ```

2. **Check health**
   - Visit: http://localhost:8000/health
   - Should show: `"status": "healthy"`

3. **Open test frontend**
   - Double-click `test_frontend.html`
   - Status should show: "Connected" (green)

4. **Try calculation**
   - Click example: "High Court - $50k"
   - Click "Calculate Costs"
   - Should see: $4,000 result

5. **Check all tabs**
   - **Formatted**: Pretty results
   - **JSON Response**: Raw data
   - **Debug Info**: Request/response

6. **Try more scenarios**
   - Different courts
   - Different amounts
   - Different case types

---

## Advanced: Trace Specific Functions

### To trace Pattern Extractor:

**Edit:** `backend/common_services/pattern_extractor.py`

**Add debug prints:**
```python
def extract_all(self, text, context):
    print(f"🔍 Extracting from: {text}")
    result = {...}
    print(f"✅ Extracted: {result}")
    return result
```

### To trace Order 21 Calculation:

**Edit:** `backend/modules/order_21/order21_module.py`

**Add debug prints in `calculate()` method:**
```python
def calculate(self, filled_fields):
    print(f"📊 Calculating with: {filled_fields}")
    result = {...}
    print(f"💰 Result: ${result['total_costs']}")
    return result
```

**Then restart backend** and calculations will show these prints!

---

## Performance Testing

### Test response times:

In browser console (F12 → Console):

```javascript
console.time('calculation');
await fetch('http://localhost:8000/calculate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'High Court default judgment $50,000'})
});
console.timeEnd('calculation');
```

**Expected:** < 100ms (very fast - no AI needed!)

---

## Next Steps

Once local testing works:

1. ✅ Backend calculates correctly
2. ✅ Frontend displays results
3. 🚀 Deploy to Railway (backend)
4. 🚀 Deploy to Netlify (frontend)
5. 🎉 Production ready!

---

**Questions?** Check:
- Backend logs in terminal
- Browser console (F12)
- Debug Info tab in test frontend

**Happy testing!** 🧪
