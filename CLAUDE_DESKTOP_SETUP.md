# Claude Desktop Setup Guide
**Testing MCP Phase 1 with Claude Desktop**

## Step 1: Locate Claude Desktop Config File

### Windows
Open File Explorer and navigate to:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Or paste this in the Run dialog (Win+R):
```
%APPDATA%\Claude
```

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

---

## Step 2: Update Configuration

**IMPORTANT:** You need to adjust paths for your Windows environment since the project is in WSL.

### Option A: Run from WSL (Recommended if you have WSL integration)

Open the config file and add:

```json
{
  "mcpServers": {
    "singapore-legal-rag": {
      "command": "wsl",
      "args": [
        "python3",
        "-m",
        "backend.mcp.servers.legal_mcp_server"
      ],
      "cwd": "/home/claude/legal-advisory-v5",
      "env": {
        "PYTHONPATH": "/home/claude/legal-advisory-v5"
      }
    }
  }
}
```

### Option B: Copy Project to Windows (Alternative)

If WSL integration doesn't work, copy the project to Windows:

1. **Copy project from WSL to Windows:**
```bash
# In WSL terminal
cp -r /home/claude/legal-advisory-v5 /mnt/c/Users/Samee/legal-advisory-v5
```

2. **Install dependencies on Windows:**
```bash
# In Windows PowerShell or Command Prompt
cd C:\Users\Samee\legal-advisory-v5
pip install -r requirements.txt
```

3. **Configure Claude Desktop** (Windows paths):
```json
{
  "mcpServers": {
    "singapore-legal-rag": {
      "command": "python",
      "args": [
        "-m",
        "backend.mcp.servers.legal_mcp_server"
      ],
      "cwd": "C:\\Users\\Samee\\legal-advisory-v5",
      "env": {
        "PYTHONPATH": "C:\\Users\\Samee\\legal-advisory-v5"
      }
    }
  }
}
```

---

## Step 3: Restart Claude Desktop

1. **Quit Claude Desktop completely** (not just close window)
   - Windows: Right-click system tray icon → Quit
   - macOS: Cmd+Q

2. **Start Claude Desktop again**

3. **Check for MCP server in settings:**
   - Look for a hammer/tools icon (🔨) in the interface
   - Or check settings for "Connected Servers"
   - You should see "singapore-legal-rag" listed

---

## Step 4: Test Queries

### Test 1: Search Logic Tree
```
Search for rules about "summary judgment" in Order 21
```

**Expected:** Claude uses `search_logic_tree` tool and returns matching nodes with citations.

---

### Test 2: Calculate Costs
```
Calculate costs for a High Court default judgment with a claim amount of $50,000
```

**Expected:** Claude uses:
1. `extract_case_information` to extract: court_level="High Court", case_type="default_judgment_liquidated", claim_amount=50000
2. `calculate_order21_costs` to compute costs
3. Returns: Total costs $4,000, calculation basis, audit trail

---

### Test 3: Validate Citation
```
Is "Order 21, Rule 1" a valid citation under Singapore Rules of Court 2021?
```

**Expected:** Claude uses `validate_legal_citation` tool and confirms it's valid.

---

### Test 4: Rule Analysis
```
Explain Order 21, Rule 4 regarding offers to settle and ADR
```

**Expected:** Claude uses:
1. `search_logic_tree` to find Rule 4
2. `get_rule_context` to get full context
3. Retrieves resource `legal://rules/ORDER_21_RULE_4`
4. Provides structured analysis with WHAT/WHICH/IF-THEN/MODALITY/GIVEN/WHY

---

### Test 5: Complex Query
```
I have a District Court case with a default judgment for $30,000.
What are my costs, and what rules apply?
```

**Expected:** Claude uses multiple tools:
1. `extract_case_information` → extracts case details
2. `calculate_order21_costs` → calculates costs
3. `search_logic_tree` → finds applicable rules
4. Returns comprehensive answer with costs and rule citations

---

## Step 5: Verify Tools Are Working

In Claude Desktop, you should see:

1. **Tool Usage Indicators:**
   - Small icons showing tools being invoked
   - Tool names like `calculate_order21_costs`
   - Loading states during tool execution

2. **Tool Results:**
   - Structured responses with citations
   - Calculation breakdowns
   - Rule references

3. **Multiple Tool Calls:**
   - Complex queries trigger 2-3 tool calls
   - Sequential workflow (extract → calculate → validate)

---

## Troubleshooting

### Issue 1: MCP Server Not Appearing

**Symptoms:** No "singapore-legal-rag" in settings

**Solutions:**
1. Check config file JSON syntax (use JSONLint.com)
2. Ensure file is saved in correct location
3. Restart Claude Desktop completely (quit from system tray)
4. Check Claude Desktop logs:
   - Windows: `%APPDATA%\Claude\logs\`
   - macOS: `~/Library/Logs/Claude/`
   - Linux: `~/.config/Claude/logs/`

---

### Issue 2: Tool Invocations Fail

**Symptoms:** Claude tries to use tools but gets errors

**Solutions:**

1. **Test server manually:**
```bash
# In WSL or terminal
cd /home/claude/legal-advisory-v5
python3 -m backend.mcp.servers.legal_mcp_server
```

Should output:
```
🚀 Starting Legal MCP Server...
✅ Legal MCP Server initialized
   - Logic tree nodes: 38
   - Registered modules: ['ORDER_21']
```

Press Ctrl+C to stop.

2. **Check dependencies:**
```bash
pip list | grep -E "mcp|fastmcp"
```

Should show:
```
fastmcp      2.13.0.1
mcp          0.9.0 (or similar)
```

3. **Check Python path:**
```bash
python3 -c "import backend.mcp.servers.legal_mcp_server; print('OK')"
```

Should print `OK`.

---

### Issue 3: "Module not found" Errors

**Symptoms:** Import errors in logs

**Solutions:**

1. **Set PYTHONPATH in config:**
```json
"env": {
  "PYTHONPATH": "/home/claude/legal-advisory-v5"
}
```

2. **Or copy project to Windows** (see Option B above)

---

### Issue 4: WSL Integration Not Working

**Symptoms:** `wsl` command not found

**Solutions:**

1. **Check WSL is installed:**
```powershell
wsl --list --verbose
```

2. **Use Option B** (copy to Windows) instead

---

## Expected Performance

| Operation | Typical Time |
|-----------|-------------|
| Tool discovery | <1 second |
| Search logic tree | 1-2 seconds |
| Calculate costs | 1-2 seconds |
| Validate citation | <1 second |
| Extract information | 1-2 seconds |
| Complete query (multi-tool) | 3-5 seconds |

---

## Visual Indicators in Claude Desktop

When MCP is working correctly, you'll see:

1. **Tool Discovery:**
   - Claude mentions using available tools
   - Tool names appear in responses

2. **Tool Execution:**
   - Loading indicators during execution
   - Tool results integrated into response

3. **Citations:**
   - Specific rule references (Order 21, Rule X)
   - Calculation breakdowns
   - Audit trails

---

## Example Successful Session

**You:** Calculate costs for a High Court default judgment of $75,000

**Claude (with MCP):**
> I'll help you calculate the costs. Let me extract the case information and compute the costs under Order 21.
>
> *[Uses extract_case_information tool]*
> *[Uses calculate_order21_costs tool]*
>
> **Cost Calculation Result:**
> - **Total Costs:** $4,500
> - **Cost Range:** $3,500 - $5,500
> - **Court Level:** High Court
> - **Calculation Basis:** Appendix 1, Section B, Para 1 ($60,001-$100,000)
>
> **Calculation Steps:**
> 1. Identified case type: default_judgment_liquidated
> 2. Retrieved base costs from Appendix 1, Section B, Para 1
> 3. High Court base costs: $4,500 (range: $3,500 - $5,500)
> 4. Final costs: $4,500 (no adjustment for High Court)
>
> **Assumptions:**
> - Costs calculated on standard basis unless specified otherwise
> - Costs are subject to taxation if disputed
>
> **Rules Applied:**
> - ORDER_21_APPENDIX_1
> - ORDER_21_APPENDIX_1_SECTION_B
> - ORDER_21_RULE_3_HIGH_COURT
>
> The calculation has high confidence as it's based on deterministic rules from Singapore Rules of Court 2021.

---

## Next Steps After Testing

Once MCP is working in Claude Desktop:

1. ✅ **Test all 5 tools** with different queries
2. ✅ **Test multi-tool workflows** (complex queries)
3. ✅ **Document any issues** you encounter
4. ✅ **Test edge cases** (invalid citations, missing info, etc.)

Then we can:
- Add HTTP transport for production deployment
- Integrate with FastAPI backend
- Deploy to Railway with MCP enabled

---

## Quick Reference: Config File Location

| OS | Path |
|----|------|
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

---

## Support Resources

- **MCP Official Docs:** https://modelcontextprotocol.io/
- **MCP Inspector:** https://github.com/modelcontextprotocol/inspector
- **FastMCP Docs:** https://github.com/jlowin/fastmcp
- **Local Docs:** `MCP_PHASE1_README.md`, `MCP_HIGH_LEVEL_DESIGN.md`

---

**Good luck with testing! Let me know if you encounter any issues.**
