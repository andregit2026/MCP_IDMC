"""
IDMC MCP Server
Exposes Informatica CAI processes and Data Integration (CDI) APIs as MCP tools.

CAI base URL:       https://emc1-cai.dm1-em.informaticacloud.com/active-bpel/rt/
CDI REST API v2:    <serverUrl>/api/v2/  (serverUrl returned at login)
Platform API v3:    <baseApiUrl>/public/core/v3/  (baseApiUrl returned at login)
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


def _v3_session() -> tuple[str, str]:
    """
    Login to IDMC and return (baseApiUrl, sessionId) for Platform API v3 calls.
    Session is valid for ~2 hours. Same session can be used for v2 and v3 APIs.
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
    # v3 uses baseApiUrl (instead of serverUrl) and same session ID
    base_api_url = data.get("baseApiUrl", data["serverUrl"])
    return base_api_url, data["icSessionId"]


def _cdi_headers(session_id: str) -> dict:
    return {"icSessionId": session_id, "Content-Type": "application/json"}


def _v3_headers(session_id: str) -> dict:
    return {"INFA-SESSION-ID": session_id, "Content-Type": "application/json"}


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


# ---------------------------------------------------------------------------
# Platform API v3 - Organization & Asset Management
# ---------------------------------------------------------------------------

@mcp.tool()
def list_objects(object_type: str = None, limit: int = 100) -> dict:
    """
    Lists organization assets (mappings, connections, schedules, etc.).
    Useful for discovering assets to export or finding object dependencies.

    object_type: Optional filter by type (e.g., "DTEMPLATE" for mappings, "Connection")
    limit: Maximum number of objects to return (default 100)
    """
    base_url, session_id = _v3_session()
    params = {"limit": limit}
    if object_type:
        params["type"] = object_type

    resp = requests.get(
        f"{base_url}/public/core/v3/objects",
        headers=_v3_headers(session_id),
        params=params,
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def get_object_dependencies(object_id: str) -> dict:
    """
    Gets dependencies for a specific asset (impact analysis).
    Returns objects that depend on this object and objects this object depends on.

    object_id: The ID of the object to analyze dependencies for
    """
    base_url, session_id = _v3_session()
    resp = requests.get(
        f"{base_url}/public/core/v3/objects/{object_id}/dependencies",
        headers=_v3_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def list_projects() -> dict:
    """
    Lists all projects in the organization.
    Returns project details including name, description, and creation info.
    """
    base_url, session_id = _v3_session()
    resp = requests.get(
        f"{base_url}/public/core/v3/projects",
        headers=_v3_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def get_project(project_id: str = None, project_name: str = None) -> dict:
    """
    Gets details of a specific project by ID or name.

    project_id: The project ID (use this OR project_name, not both)
    project_name: The project name (use this OR project_id, not both)
    """
    base_url, session_id = _v3_session()

    if project_id:
        url = f"{base_url}/public/core/v3/projects/{project_id}"
    elif project_name:
        url = f"{base_url}/public/core/v3/projects/name/{project_name}"
    else:
        return {"error": "Must provide either project_id or project_name"}

    resp = requests.get(url, headers=_v3_headers(session_id))
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def list_project_folders(project_id: str) -> dict:
    """
    Lists all folders within a specific project.

    project_id: The ID of the project
    """
    base_url, session_id = _v3_session()
    resp = requests.get(
        f"{base_url}/public/core/v3/projects/{project_id}/folders",
        headers=_v3_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def get_license_info() -> dict:
    """
    Returns license details for the organization.
    Shows license entitlements, usage, and expiration information.
    """
    base_url, session_id = _v3_session()
    resp = requests.get(
        f"{base_url}/public/core/v3/license",
        headers=_v3_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def list_roles() -> dict:
    """
    Lists all roles in the organization.
    Returns both system roles and custom roles with their privileges.
    """
    base_url, session_id = _v3_session()
    resp = requests.get(
        f"{base_url}/public/core/v3/roles",
        headers=_v3_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def get_role(role_id: str = None, role_name: str = None) -> dict:
    """
    Gets details of a specific role by ID or name.

    role_id: The role ID (use this OR role_name, not both)
    role_name: The role name (use this OR role_id, not both)
    """
    base_url, session_id = _v3_session()

    if role_id:
        url = f"{base_url}/public/core/v3/roles/{role_id}"
    elif role_name:
        url = f"{base_url}/public/core/v3/roles/name/{role_name}"
    else:
        return {"error": "Must provide either role_id or role_name"}

    resp = requests.get(url, headers=_v3_headers(session_id))
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


@mcp.tool()
def list_schedules() -> dict:
    """
    Lists all schedules in the organization.
    Returns schedule details including frequency, tasks, and status.
    """
    base_url, session_id = _v3_session()
    resp = requests.get(
        f"{base_url}/public/core/v3/schedule",
        headers=_v3_headers(session_id),
    )
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}", "detail": resp.text}


if __name__ == "__main__":
    mcp.run()
