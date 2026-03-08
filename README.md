# MCP_IDMC — Informatica IDMC MCP Server

A [FastMCP](https://gofastmcp.com) server that exposes **Informatica Intelligent Data Management Cloud (IDMC) Data Integration** APIs as MCP tools, allowing AI agents (Claude, etc.) to query, run, and monitor CDI mappings through natural language.

---

## Tools

### Data Integration (CDI)

| Tool | Description |
|---|---|
| `list_mappings` | Lists all Data Integration mappings in the org |
| `get_mapping(mapping_id)` | Gets full metadata for a specific mapping |
| `run_mapping_task(task_id)` | Triggers a mapping task by its task ID |
| `get_job_status()` | Returns the status of all currently running jobs |
| `get_activity_log(task_id, row_limit)` | Returns completed run history for a task |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env`:

```env
IDMC_USER=your@email.com
IDMC_PASS=yourpassword
```

### 3. Run the server

```bash
python src/server.py
```

### 4. Register in Claude Code

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "idmc": {
      "command": "python",
      "args": ["C:/path/to/MCP_IDMC/src/server.py"],
      "env": {
        "IDMC_USER": "your@email.com",
        "IDMC_PASS": "yourpassword"
      }
    }
  }
}
```

---

## How it works

The server authenticates against the IDMC REST API (`/ma/api/v2/user/login`) and uses the returned `serverUrl` and `icSessionId` for all subsequent CDI calls. Sessions are valid for ~2 hours.

```
AI Agent (Claude)
     │
     │  MCP tool call
     ▼
FastMCP server (src/server.py)
     │
     │  IDMC REST API  /api/v2/mapping
     │                 /api/v2/job
     │                 /api/v2/activity/activityLog
     │                 /api/v2/activity/activityMonitor
     ▼
Informatica IDMC (CDI)
```

---

## Project Structure

```
MCP_IDMC/
├── src/
│   └── server.py              # Main MCP server application
├── scripts/
│   └── generate_mapping_report.py  # Generate HTML reports from mapping exports
├── json/
│   └── mapping_sample.json    # Sample mapping metadata
├── output/
│   └── *.html                 # Generated HTML analysis reports
├── .env                       # Your IDMC credentials (not in git)
├── .env.example              # Template for credentials
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Scripts

### Mapping Report Generator

Generate a beautiful HTML analysis report from an exported IDMC mapping.

**Usage:**

1. Export your mapping from IDMC (Export > Mapping)
2. Extract the export package
3. Update paths in `scripts/generate_mapping_report.py`:
   - Path to the API mapping JSON (from `get_mapping()` or saved locally)
   - Path to the exported `@3.bin` file (usually in `Explore/[Project]/[Folder]/[Mapping].DTEMPLATE.zip/bin/@3.bin`)
4. Run the script:
   ```bash
   python scripts/generate_mapping_report.py
   ```
5. Find the generated HTML report in `output/`

The report includes:
- General mapping information (creator, timestamps, status)
- Transformation summary with counts by type
- Detailed transformation breakdown (Sources, Expressions, Aggregators, Targets)
- Visual data flow diagram
- Mapping purpose description

---

## IDMC pod configuration

The server is pre-configured for the `dm1-em` pod:

| Setting | Value |
|---|---|
| Login URL | `https://dm1-em.informaticacloud.com/ma/api/v2/user/login` |
| CDI API base | `<serverUrl>/api/v2/` (returned at login) |
| CAI base URL | `https://emc1-cai.dm1-em.informaticacloud.com/active-bpel/rt/` |

To use a different pod, update `LOGIN_URL` and `CAI_BASE_URL` in `src/server.py`.

---

## Requirements

- Python 3.10+
- `fastmcp`, `mcp`, `requests`
- An active Informatica IDMC account with CDI access
