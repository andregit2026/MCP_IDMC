"""
IDMC MCP Server
Exposes Informatica CAI processes and Data Integration (CDI) APIs as MCP tools.

CAI base URL:  https://emc1-cai.dm1-em.informaticacloud.com/active-bpel/rt/
CDI REST API:  <serverUrl>/api/v2/  (serverUrl returned at login)
"""

import base64
import os
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("IDMC Server")

CAI_BASE_URL = "https://emc1-cai.dm1-em.informaticacloud.com/active-bpel/rt"
LOGIN_URL = "https://dm1-em.informaticacloud.com/ma/api/v2/user/login"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cai_auth() -> dict:
    """Basic auth header for CAI process calls."""
    user = os.environ["IDMC_USER"]
    password = os.environ["IDMC_PASS"]
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def _cdi_session() -> tuple[str, str]:
    """
    Login to IDMC and return (serverUrl, icSessionId) for CDI REST API calls.
    Session is valid for ~2 hours.
    """
    resp = requests.post(
        LOGIN_URL,
        json={
            "@type": "login",
            "username": os.environ["IDMC_USER"],
            "password": os.environ["IDMC_PASS"],
        },
    )
    resp.raise_for_status()
    data = resp.json()
    return data["serverUrl"], data["icSessionId"]


def _cdi_headers(session_id: str) -> dict:
    return {"icSessionId": session_id, "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# CAI tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_customer_by_email(email: str) -> dict:
    """
    Looks up a customer record in Informatica IDMC by email address.
    Returns customer_id and name on success, or an error dict on failure.
    """
    url = f"{CAI_BASE_URL}/GetCustomerByEmail"
    response = requests.post(url, json={"email": email}, headers=_cai_auth())
    if response.status_code == 200:
        return response.json()
    return {"error": f"HTTP {response.status_code}", "detail": response.text}


# ---------------------------------------------------------------------------
# CDI - Data Integration tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_mappings() -> dict:
    """
    Lists all Data Integration mappings in the IDMC org.
    Returns a list of mappings with id, name, description, and status.
    """
    server_url, session_id = _cdi_session()
    resp = requests.get(
        f"{server_url}/api/v2/mapping",
        headers=_cdi_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def get_mapping(mapping_id: str) -> dict:
    """
    Gets details of a specific Data Integration mapping by its ID.
    Returns full mapping metadata including parameters and deployment status.
    """
    server_url, session_id = _cdi_session()
    resp = requests.get(
        f"{server_url}/api/v2/mapping/{mapping_id}",
        headers=_cdi_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def run_mapping_task(task_id: str) -> dict:
    """
    Runs a Data Integration mapping task by its task ID.
    Returns runId and taskName. Use get_job_status(run_id) to monitor progress.
    task_id: the ID of the mapping task (mttask), not the mapping itself.
    """
    server_url, session_id = _cdi_session()
    resp = requests.post(
        f"{server_url}/api/v2/job",
        json={"@type": "job", "taskId": task_id, "taskType": "MTT"},
        headers=_cdi_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def get_job_status() -> dict:
    """
    Returns the status of all currently running Data Integration jobs.
    Use this to monitor mapping tasks after triggering them with run_mapping_task.
    """
    server_url, session_id = _cdi_session()
    resp = requests.get(
        f"{server_url}/api/v2/activity/activityMonitor?details=true",
        headers=_cdi_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def get_activity_log(task_id: str, row_limit: int = 20) -> dict:
    """
    Returns the activity log (completed run history) for a Data Integration task.
    task_id: the mapping task ID to retrieve logs for.
    row_limit: max number of log entries to return (default 20).
    """
    server_url, session_id = _cdi_session()
    resp = requests.get(
        f"{server_url}/api/v2/activity/activityLog",
        params={"taskId": task_id, "rowLimit": row_limit},
        headers=_cdi_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


if __name__ == "__main__":
    mcp.run()
