"""
Compare IDMC REST API v2 vs v3 for mapping information
Fetches mapping 'm_arausch_DPR_DISTINCT_ISIN3' using both APIs and shows differences
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

LOGIN_URL = "https://dm1-em.informaticacloud.com/ma/api/v2/user/login"
MAPPING_NAME = "m_arausch_DPR_DISTINCT_ISIN3"


def login():
    """Login to IDMC and return session info for both v2 and v3 APIs"""
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

    server_url = data["serverUrl"]
    base_api_url = data.get("baseApiUrl", server_url)
    session_id = data["icSessionId"]

    print(f"✓ Logged in successfully")
    print(f"  Server URL (v2): {server_url}")
    print(f"  Base API URL (v3): {base_api_url}")
    print()

    return server_url, base_api_url, session_id


def get_mapping_v2(server_url, session_id, mapping_name):
    """Fetch mapping using REST API v2"""
    print(f"=== REST API v2 ===")

    # List all mappings
    resp = requests.get(
        f"{server_url}/api/v2/mapping",
        headers={"icSessionId": session_id, "Content-Type": "application/json"},
    )
    resp.raise_for_status()
    mappings = resp.json()

    # Find the specific mapping
    target_mapping = None
    for mapping in mappings:
        if mapping.get("name") == mapping_name:
            target_mapping = mapping
            break

    if not target_mapping:
        print(f"✗ Mapping '{mapping_name}' not found in v2 API")
        return None

    # Get detailed mapping info
    mapping_id = target_mapping["id"]
    resp = requests.get(
        f"{server_url}/api/v2/mapping/{mapping_id}",
        headers={"icSessionId": session_id, "Content-Type": "application/json"},
    )
    resp.raise_for_status()
    detailed_mapping = resp.json()

    print(f"✓ Found mapping via v2 API")
    print(f"  Endpoint: GET {server_url}/api/v2/mapping/{mapping_id}")

    return detailed_mapping


def get_mapping_v3(base_api_url, session_id, mapping_name):
    """Fetch mapping using Platform API v3"""
    print(f"=== Platform API v3 ===")

    try:
        # Try to list all objects first (without type filter)
        resp = requests.get(
            f"{base_api_url}/public/core/v3/objects",
            headers={"INFA-SESSION-ID": session_id, "Content-Type": "application/json"},
            params={"limit": 100},
        )

        if resp.status_code != 200:
            print(f"✗ v3 API returned status {resp.status_code}")
            print(f"  Response: {resp.text[:500]}")
            return None

        objects_data = resp.json()
        print(f"  Total objects returned: {len(objects_data.get('objects', []))}")

        # Show available object types for debugging
        types_found = set()
        for obj in objects_data.get("objects", []):
            types_found.add(obj.get("type", "unknown"))
        print(f"  Object types found: {', '.join(sorted(types_found))}")

        # Find the specific mapping by name
        target_mapping = None
        for obj in objects_data.get("objects", []):
            if obj.get("name") == mapping_name:
                target_mapping = obj
                print(f"  Found mapping with type: {obj.get('type')}")
                break

        if not target_mapping:
            # Try searching with pagination
            print(f"  Searching through all objects...")
            offset = 0
            page_size = 100
            max_pages = 10  # Limit search to prevent infinite loops

            for page in range(max_pages):
                resp = requests.get(
                    f"{base_api_url}/public/core/v3/objects",
                    headers={"INFA-SESSION-ID": session_id, "Content-Type": "application/json"},
                    params={"limit": page_size, "offset": offset},
                )

                if resp.status_code != 200:
                    break

                objects_data = resp.json()
                objects = objects_data.get("objects", [])

                if not objects:
                    break

                for obj in objects:
                    if obj.get("name") == mapping_name:
                        target_mapping = obj
                        print(f"  Found on page {page + 1}")
                        break

                if target_mapping:
                    break

                offset += page_size

            if not target_mapping:
                print(f"✗ Mapping '{mapping_name}' not found in v3 API")
                return None

        print(f"✓ Found mapping via v3 API")
        print(f"  Endpoint: GET {base_api_url}/public/core/v3/objects")

        return target_mapping
    except Exception as e:
        print(f"✗ Error accessing v3 API: {e}")
        return None


def compare_apis(v2_data, v3_data):
    """Compare the data returned by v2 and v3 APIs"""
    print()
    print("=" * 80)
    print("COMPARISON: REST API v2 vs Platform API v3")
    print("=" * 80)
    print()

    # Fields in v2
    v2_fields = set(v2_data.keys()) if v2_data else set()
    v3_fields = set(v3_data.keys()) if v3_data else set()

    print("📊 FIELD COMPARISON:")
    print()

    # Common fields
    common_fields = v2_fields & v3_fields
    if common_fields:
        print(f"✓ Common fields ({len(common_fields)}):")
        for field in sorted(common_fields):
            print(f"  - {field}")
        print()

    # v2-only fields
    v2_only = v2_fields - v3_fields
    if v2_only:
        print(f"📌 Fields ONLY in v2 ({len(v2_only)}):")
        for field in sorted(v2_only):
            print(f"  - {field}")
        print()

    # v3-only fields
    v3_only = v3_fields - v2_fields
    if v3_only:
        print(f"📌 Fields ONLY in v3 ({len(v3_only)}):")
        for field in sorted(v3_only):
            print(f"  - {field}")
        print()

    print("=" * 80)
    print()

    # Show sample values for comparison
    print("📋 SAMPLE DATA COMPARISON:")
    print()

    if v2_data:
        print("--- REST API v2 Sample ---")
        sample_fields = ["id", "name", "description", "createTime", "updateTime", "status"]
        for field in sample_fields:
            if field in v2_data:
                value = v2_data[field]
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {field}: {value}")
        print()

    if v3_data:
        print("--- Platform API v3 Sample ---")
        sample_fields = ["id", "name", "description", "createTime", "updateTime", "path"]
        for field in sample_fields:
            if field in v3_data:
                value = v3_data[field]
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {field}: {value}")
        print()


def save_results(v2_data, v3_data):
    """Save full results to JSON files"""
    output_dir = "C:/Users/arausch/Documents/VS_Studio/MCP_IDMC/output"
    os.makedirs(output_dir, exist_ok=True)

    if v2_data:
        v2_file = f"{output_dir}/mapping_v2_response.json"
        with open(v2_file, "w", encoding="utf-8") as f:
            json.dump(v2_data, f, indent=2)
        print(f"✓ Saved v2 response to: {v2_file}")

    if v3_data:
        v3_file = f"{output_dir}/mapping_v3_response.json"
        with open(v3_file, "w", encoding="utf-8") as f:
            json.dump(v3_data, f, indent=2)
        print(f"✓ Saved v3 response to: {v3_file}")

    print()


def main():
    print()
    print("=" * 80)
    print(f"Fetching mapping: {MAPPING_NAME}")
    print("=" * 80)
    print()

    # Login
    server_url, base_api_url, session_id = login()

    # Fetch from v2 API
    v2_data = get_mapping_v2(server_url, session_id, MAPPING_NAME)
    print()

    # Fetch from v3 API
    v3_data = get_mapping_v3(base_api_url, session_id, MAPPING_NAME)
    print()

    # If v2 worked but v3 failed to find by name, try accessing by ID directly
    if v2_data and not v3_data:
        mapping_id = v2_data.get("id")
        if mapping_id:
            print(f"=== Trying v3 API with direct ID access ===")
            try:
                resp = requests.get(
                    f"{base_api_url}/public/core/v3/objects/{mapping_id}",
                    headers={"INFA-SESSION-ID": session_id, "Content-Type": "application/json"},
                )
                if resp.status_code == 200:
                    v3_data = resp.json()
                    print(f"✓ Successfully fetched via direct ID access")
                    print(f"  Endpoint: GET {base_api_url}/public/core/v3/objects/{mapping_id}")
                else:
                    print(f"✗ Direct ID access returned status {resp.status_code}")
                    print(f"  Response: {resp.text[:500]}")
            except Exception as e:
                print(f"✗ Error with direct ID access: {e}")
            print()

    # Compare
    if v2_data or v3_data:
        compare_apis(v2_data, v3_data)
        save_results(v2_data, v3_data)
    else:
        print("✗ Could not fetch mapping from either API")


if __name__ == "__main__":
    main()
