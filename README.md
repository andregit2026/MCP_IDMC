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
python server.py
```

### 4. Register in Claude Code

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "idmc": {
      "command": "python",
      "args": ["C:/path/to/MCP_IDMC/server.py"],
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
FastMCP server (server.py)
     │
     │  IDMC REST API  /api/v2/mapping
     │                 /api/v2/job
     │                 /api/v2/activity/activityLog
     │                 /api/v2/activity/activityMonitor
     ▼
Informatica IDMC (CDI)
```

---

## IDMC pod configuration

The server is pre-configured for the `dm1-em` pod:

| Setting | Value |
|---|---|
| Login URL | `https://dm1-em.informaticacloud.com/ma/api/v2/user/login` |
| CDI API base | `<serverUrl>/api/v2/` (returned at login) |
| CAI base URL | `https://emc1-cai.dm1-em.informaticacloud.com/active-bpel/rt/` |

To use a different pod, update `LOGIN_URL` and `CAI_BASE_URL` in `server.py`.

---

## Requirements

- Python 3.10+
- `fastmcp`, `mcp`, `requests`
- An active Informatica IDMC account with CDI access
