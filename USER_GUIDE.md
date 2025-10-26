# User Guide
## Legal Advisory System v5.0

**Version:** 5.0
**Last Updated:** October 26, 2025
**Status:** Production Ready

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the API](#using-the-api)
4. [Example Scenarios](#example-scenarios)
5. [Understanding Responses](#understanding-responses)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Introduction

The Legal Advisory System v5.0 is a hybrid AI legal advisory platform that combines:
- **100% accurate legal calculations** based on Singapore Rules of Court
- **AI-enhanced natural language understanding** for easy interaction
- **Conversational interface** for progressive information gathering

### What Can It Do?

Currently, the system specializes in **Order 21 (Costs)** calculations including:
- Default judgments (liquidated and unliquidated claims)
- Summary judgments
- Contested trials (varying durations)
- Court level adjustments (High, District, Magistrates Courts)

### Key Benefits

✅ **Accuracy**: 100% accurate calculations based on official regulations
✅ **Ease of Use**: Natural language input - just describe your case
✅ **Speed**: Instant responses with detailed explanations
✅ **Transparency**: Complete citations and calculation breakdowns
✅ **Safety**: AI cannot corrupt calculations (hybrid architecture)

---

## Getting Started

### Prerequisites

- Python 3.12 or higher
- pip package manager
- (Optional) curl for API testing

### Installation

```bash
# Clone the repository
git clone https://github.com/Koulsami/legal-advisory-v5.git
cd legal-advisory-v5

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Starting the Server

```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the API server
uvicorn backend.api.routes:app --reload

# Server will be available at http://localhost:8000
```

### Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

---

## Using the API

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API health |
| `/sessions` | POST | Create new session |
| `/sessions/{id}` | GET | Get session details |
| `/messages` | POST | Send message |
| `/modules` | GET | List available modules |
| `/statistics` | GET | Get system statistics |

### Basic Workflow

1. **Create a session** - Start a conversation
2. **Send messages** - Provide case details
3. **Receive responses** - Get calculations and questions
4. **Continue conversation** - Answer follow-up questions
5. **Get final result** - Receive complete calculation

### Interactive Documentation

Visit these URLs when the server is running:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Example Scenarios

### Scenario 1: Simple Query (All Information Provided)

**Goal:** Get costs for a straightforward default judgment

**Request:**
```bash
# 1. Create session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'

# Response: {"session_id": "abc123...", "status": "active"}

# 2. Send complete query
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123...",
    "message": "I need costs for a High Court default judgment for $50,000 liquidated claim"
  }'
```

**Expected Response:**
```json
{
  "session_id": "abc123...",
  "message": "Based on the information provided, here are the cost calculations...",
  "status": "complete",
  "completeness_score": 1.0,
  "result": {
    "calculation": {
      "total_costs": 4000.0,
      "citation": "Order 21 Appendix 1 Part A(1)(a)",
      "breakdown": {...}
    }
  }
}
```

---

### Scenario 2: Conversational Flow (Progressive Information)

**Goal:** Provide information step-by-step

**Conversation:**

```bash
# Message 1: General request
"I need help calculating legal costs"
# System asks: What type of case? Court level? Claim amount?

# Message 2: Provide case type
"It's for a default judgment"
# System asks: Court level? Claim amount? Liquidated or unliquidated?

# Message 3: Provide more details
"High Court, liquidated claim"
# System asks: What is the claim amount?

# Message 4: Final detail
"$75,000"
# System provides: Complete calculation with breakdown
```

---

### Scenario 3: Contested Trial

**Goal:** Calculate costs for a multi-day trial

**Request:**
```bash
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "xyz789...",
    "message": "What are the costs for a 4-day contested trial in District Court for $120,000?"
  }'
```

**Key Details:**
- Trial duration: 4 days (3-5 day category)
- Court: District Court
- Amount: $120,000

**Expected Result:**
- Base costs for 3-5 day trial
- District Court adjustment (reduced from High Court rates)
- Complete breakdown with citations

---

### Scenario 4: Unliquidated Claim

**Goal:** Calculate costs for an unliquidated claim

**Request:**
```bash
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "def456...",
    "message": "Magistrates Court default judgment, unliquidated claim of $15,000"
  }'
```

**Key Points:**
- Unliquidated claims may have different cost structures
- Lower court levels (Magistrates) have reduced costs
- System provides appropriate citations

---

## Understanding Responses

### Response Structure

Every message response contains:

```json
{
  "session_id": "unique-session-id",
  "message": "Natural language response with explanation",
  "status": "complete|gathering_info|error",
  "completeness_score": 0.0-1.0,
  "result": {
    "calculation": {...},
    "citations": [...],
    "recommendations": [...]
  },
  "questions": ["Follow-up question 1", "Follow-up question 2"],
  "confidence_score": 0.0-1.0
}
```

### Status Values

| Status | Meaning | Next Step |
|--------|---------|-----------|
| `gathering_info` | System needs more information | Answer the questions provided |
| `analyzing` | System is processing | Wait for next response |
| `complete` | Calculation complete | Review result |
| `error` | Something went wrong | Check error message |

### Completeness Score

- **0.0-0.3**: Just started, need much more info
- **0.4-0.6**: About halfway there
- **0.7-0.9**: Almost complete, need 1-2 more details
- **1.0**: All information received, calculation complete

---

## Best Practices

### 1. Provide Information Clearly

**Good:**
- "High Court default judgment for $50,000 liquidated claim"
- "District Court contested trial, 3 days, claim amount $80,000"
- "Summary judgment in Magistrates Court for $20,000"

**Less Ideal:**
- "I need costs" (too vague)
- "Calculate for my case" (no details)
- "How much will it cost?" (need specifics)

### 2. Use Specific Terms

The system understands legal terminology:
- **Case types:** default judgment, summary judgment, contested trial
- **Court levels:** High Court, District Court, Magistrates Court
- **Claim types:** liquidated, unliquidated
- **Trial duration:** 1-2 days, 3-5 days, 6+ days

### 3. Include Amounts

Always specify the claim amount:
- ✅ "$50,000"
- ✅ "$120,000"
- ✅ "SGD 75,000"
- ❌ "A large amount"
- ❌ "Not sure"

### 4. One Session Per Case

Create a new session for each distinct case:
- Each session maintains separate context
- Don't mix multiple cases in one session
- Sessions help track conversation history

### 5. Review Citations

Always check the citations provided:
- Citations reference specific Rules of Court sections
- Verify citations match your case type
- Use citations for documentation/justification

---

## Troubleshooting

### Problem: "Session not found"

**Cause:** Invalid or expired session ID

**Solution:**
1. Create a new session
2. Verify you're using the correct session ID
3. Check for typos in session ID

### Problem: "Insufficient information"

**Cause:** System needs more details

**Solution:**
1. Check the `questions` field in response
2. Answer the specific questions asked
3. Provide all required details (case type, court, amount)

### Problem: "Invalid claim amount"

**Cause:** Amount is negative, zero, or incorrectly formatted

**Solution:**
1. Provide positive dollar amount
2. Use format: "$50,000" or "50000"
3. Avoid special characters except $ and ,

### Problem: "Connection refused"

**Cause:** API server not running

**Solution:**
1. Start the server: `uvicorn backend.api.routes:app --reload`
2. Verify it's running: `curl http://localhost:8000/health`
3. Check for port conflicts (default: 8000)

### Problem: Unexpected results

**Cause:** Incorrect information or edge case

**Solution:**
1. Review the input you provided
2. Check the `result.breakdown` for calculation steps
3. Verify citations match your case
4. Create a new session and try again

---

## FAQ

### Q: How accurate are the calculations?

**A:** 100% accurate for supported case types. The system uses pre-built logic trees based on Singapore Rules of Court. AI enhances explanations but cannot modify calculations.

### Q: What case types are supported?

**A:** Currently Order 21 (Costs):
- Default judgments (liquidated/unliquidated)
- Summary judgments
- Contested trials (various durations)
- All court levels (High, District, Magistrates)

### Q: Can I use this for other jurisdictions?

**A:** No, currently only Singapore Rules of Court are implemented.

### Q: Is my data stored?

**A:** Sessions are stored in memory during the server's runtime. When the server restarts, all session data is cleared. No persistent storage is used in the current version.

### Q: Can multiple users use it simultaneously?

**A:** Yes, the system handles concurrent sessions. Each user should create their own session.

### Q: What if I provide wrong information?

**A:** Create a new session and start over with correct information. The system doesn't currently support editing previous messages.

### Q: How do I interpret the breakdown?

**A:** The `result.breakdown` shows:
- Base costs from the relevant schedule
- Court level adjustments
- Complexity factors
- Final total
- Citations for each component

### Q: Is there a rate limit?

**A:** Currently no rate limiting in the development version. Production deployment should implement rate limiting.

### Q: Can I integrate this into my application?

**A:** Yes, use the REST API. See `examples/api_client_example.py` for Python integration examples.

### Q: What's the difference between liquidated and unliquidated?

**A:**
- **Liquidated:** Claim amount is fixed/certain (e.g., unpaid invoice for $50,000)
- **Unliquidated:** Claim amount to be assessed (e.g., damages to be determined by court)

---

## Running the Demo

### Interactive Demo

```bash
# Run the interactive demo
python3 demo/interactive_demo.py

# Follow the prompts to see various scenarios
```

### API Examples (Shell)

```bash
# Make sure server is running first
uvicorn backend.api.routes:app --reload

# In another terminal, run examples
./examples/api_examples.sh
```

### API Examples (Python)

```bash
# Make sure server is running first
uvicorn backend.api.routes:app --reload

# In another terminal, run Python examples
python3 examples/api_client_example.py
```

---

## Getting Help

### Documentation Resources

- **README.md** - Project overview and quick start
- **PROJECT_STATUS.md** - Current implementation status
- **DOCS_INDEX.md** - Complete documentation index
- **API Documentation** - http://localhost:8000/docs (when server running)

### Support

- **GitHub Issues:** Report bugs or request features
- **API Documentation:** Built-in Swagger UI at `/docs`
- **Example Code:** Check `examples/` directory

---

## Next Steps

1. **Try the Interactive Demo**
   ```bash
   python3 demo/interactive_demo.py
   ```

2. **Explore the API**
   ```bash
   # Start server
   uvicorn backend.api.routes:app --reload

   # Visit API docs
   open http://localhost:8000/docs
   ```

3. **Build Your Integration**
   - Use `examples/api_client_example.py` as a template
   - Refer to API documentation for endpoints
   - Test with various scenarios

4. **Review the Code**
   - Check `backend/` for implementation
   - See `tests/` for comprehensive test examples
   - Read design docs in `docs/`

---

**Legal Advisory System v5.0**
© 2025 All Rights Reserved

For technical documentation, see [DOCS_INDEX.md](DOCS_INDEX.md)
