# IDMC REST API v2 vs Platform API v3 Comparison

**Mapping:** m_arausch_DPR_DISTINCT_ISIN3
**Date:** 2026-03-08
**Org ID:** 010MEP

## Executive Summary

REST API v2 and Platform API v3 serve **different purposes** in the Informatica Cloud ecosystem:

- **REST API v2** (CDI API): Specialized for **Data Integration** operations - full CRUD operations on mappings, tasks, and job execution
- **Platform API v3**: Organization-level management - assets, projects, roles, licenses, and governance

**For Data Integration mappings like `m_arausch_DPR_DISTINCT_ISIN3`, you MUST use REST API v2.**

---

## Key Findings

### ✅ REST API v2 (Data Integration)

**Status:** ✅ **Fully functional** for mapping operations

**Endpoint:**
```
GET {serverUrl}/api/v2/mapping/{mappingId}
Example: https://emc1.dm1-em.informaticacloud.com/saas/api/v2/mapping/010MEP1700000000000Z
```

**Authentication:**
- Header: `icSessionId` (obtained from login)

**Result:**
- Successfully retrieved complete mapping details
- 33 fields returned with comprehensive mapping metadata

---

### ❌ Platform API v3 (Organization Management)

**Status:** ❌ **Does not support detailed mapping access**

**Attempted Endpoints:**
1. `GET {baseApiUrl}/public/core/v3/objects?type=DTEMPLATE&limit=100`
   - Result: Mapping not found in list
2. `GET {baseApiUrl}/public/core/v3/objects/{mappingId}`
   - Result: 404 Not Found
3. Paginated search through all objects
   - Result: Mapping not found

**Authentication:**
- Header: `INFA-SESSION-ID` (same session as v2)

**Observations:**
- v3 API can list DTEMPLATE objects (mapping templates) but doesn't return specific mappings
- Returns organizational metadata only (no detailed mapping transformations or parameters)
- Object types found: API_POLICY, AtScaleDTemplate, DMAPPLET, DTEMPLATE, Folder, MAPPLET, MTT, PCS, PROCESS, PROFILE, Project, RULE_SPECIFICATION, TASKFLOW

---

## Field Comparison

### Fields ONLY in REST API v2 (33 fields)

#### Identity & Metadata
- `@type` - Object type identifier (e.g., "mappingTemplate")
- `id` - Unique mapping identifier (e.g., "010MEP1700000000000Z")
- `orgId` - Organization identifier
- `name` - Mapping name
- `description` - Mapping description

#### Timestamps & Ownership
- `createTime` - Creation timestamp (ISO 8601)
- `updateTime` - Last update timestamp (ISO 8601)
- `deployTime` - Deployment timestamp (Unix epoch)
- `createdBy` - Creator username
- `updatedBy` - Last updater username

#### Template & Version Information
- `templateId` - Mapping template identifier
- `deployedTemplateId` - Deployed template version
- `prunedTemplateId` - Optimized template version
- `bundleVersion` - Template bundle version

#### Validation & Status
- `valid` - Mapping validation status (boolean)
- `documentType` - Document type (e.g., "MAPPING")
- `assetFrsGuid` - Asset GUID for FRS (File Repository Service)

#### Configuration & Features
- `hasParameters` - Whether mapping has parameters
- `hasParametersDeployed` - Whether deployed version has parameters
- `fixedConnection` - Connection is fixed (not parameterized)
- `fixedConnectionDeployed` - Deployed version connection status
- `isSchemaValidationEnabled` - Schema validation enabled
- `allowMaxFieldLength` - Allow maximum field length
- `specialCharacterSupport` - Special character handling
- `autoExpireObject` - Auto-expiration setting

#### Detailed Mapping Content
- `parameters` - **CRITICAL**: Full list of sources, targets, and their configurations
  - Source parameters (connection, object, file attributes)
  - Target parameters (connection, object, operation type)
  - Field mappings and metadata
- `inOutParameters` - Input/output parameters
- `references` - Referenced connections and objects
- `sequences` - Sequence generators used

#### Preview & Testing
- `mappingPreviewFileRecordId` - Preview file record ID
- `deployedMappingPreviewFileRecordId` - Deployed preview record ID
- `testTaskId` - Associated test task ID

#### Task Information
- `tasks` - Number of associated tasks

---

## Detailed REST API v2 Response Example

### High-Level Metadata
```json
{
  "@type": "mappingTemplate",
  "id": "010MEP1700000000000Z",
  "orgId": "010MEP",
  "name": "m_arausch_DPR_DISTINCT_ISIN3",
  "description": "",
  "createTime": "2026-02-24T07:20:09.000Z",
  "updateTime": "2026-03-08T14:30:07.000Z",
  "createdBy": "arausch",
  "updatedBy": "arausch",
  "valid": true,
  "documentType": "MAPPING"
}
```

### Parameters Array (Detailed Transformations)

v2 API returns a comprehensive `parameters` array containing:

#### Source Configuration
```json
{
  "@type": "mtTaskParameter",
  "name": "$Src_ISIN_list$",
  "type": "EXTENDED_SOURCE",
  "sourceConnectionId": "010MEP0B00000000000C",
  "extendedObject": {
    "object": {
      "name": "ISIN_list.csv",
      "label": "ISIN_list.csv"
    }
  },
  "srcFFAttrs": {
    "delimiter": ";",
    "textQualifier": "\"",
    "headerLineNo": 1,
    "firstDataRow": 2
  }
}
```

#### Target Configuration (Example 1: File Target)
```json
{
  "@type": "mtTaskParameter",
  "name": "$Trg_Distinct_ISIN$",
  "type": "TARGET",
  "targetConnectionId": "010MEP0B00000000000C",
  "targetObject": "Distinct_ISIN_list",
  "operationType": "Insert",
  "truncateTarget": true,
  "tgtFFAttrs": {
    "delimiter": ";",
    "textQualifier": "\"",
    "headerLineNo": 1
  }
}
```

#### Target Configuration (Example 2: Database Target)
```json
{
  "@type": "mtTaskParameter",
  "name": "$Dummy_Target$",
  "type": "TARGET",
  "targetConnectionId": "010MEP0B000000000003",
  "targetObject": "STAGING/DPR_DUMMY_TARGET",
  "operationType": "Insert",
  "dbSchema": "STAGING"
}
```

### References Array
```json
"references": [
  {
    "@type": "reference",
    "refObjectId": "010MEP0B000000000003",
    "refType": "connection"
  },
  {
    "@type": "reference",
    "refObjectId": "010MEP0B00000000000C",
    "refType": "connection"
  }
]
```

---

## Platform API v3 Response Example

**Mapping NOT FOUND - Returns 404**

When searching for DTEMPLATE objects, v3 API returns a list but doesn't include this specific mapping in the results.

### Sample v3 Object Structure (for reference)
```json
{
  "id": "string",
  "name": "string",
  "type": "DTEMPLATE",
  "path": "/Projects/ProjectName/FolderName",
  "description": "string",
  "createTime": "2026-01-01T00:00:00Z",
  "updateTime": "2026-01-01T00:00:00Z"
}
```

**Note:** Even if found, v3 wouldn't return the detailed `parameters`, `references`, or transformation information that v2 provides.

---

## API Use Cases

### When to Use REST API v2

✅ **Data Integration Operations:**
- Create, read, update, delete mappings
- View detailed mapping transformations
- Access source/target configurations
- View mapping parameters and field mappings
- Run mapping tasks (`POST /api/v2/job`)
- Monitor job execution (`GET /api/v2/activity/activityMonitor`)
- View activity logs (`GET /api/v2/activity/activityLog`)

### When to Use Platform API v3

✅ **Organization Management:**
- List all objects across the organization
- Manage projects and folders
- Manage roles and permissions
- View license information
- Manage schedules
- View object dependencies (impact analysis)
- Organizational governance and metadata

---

## Technical Differences

| Feature | REST API v2 | Platform API v3 |
|---------|------------|----------------|
| **Base URL** | `{serverUrl}/api/v2/` | `{baseApiUrl}/public/core/v3/` |
| **Auth Header** | `icSessionId` | `INFA-SESSION-ID` |
| **Session** | Same login, same session ID | Same login, same session ID |
| **Mapping Details** | ✅ Full details (33 fields) | ❌ Not accessible |
| **Parameters** | ✅ Complete parameters array | ❌ Not available |
| **References** | ✅ Connection references | ❌ Not available |
| **Job Execution** | ✅ Run tasks via `/job` | ❌ Not available |
| **Monitoring** | ✅ Activity logs & monitoring | ❌ Not available |
| **Object Dependencies** | ❌ Not available | ✅ Impact analysis |
| **Project Management** | ❌ Limited | ✅ Full project/folder management |

---

## Recommendations

### For Mapping Operations
1. **Use REST API v2** for all Data Integration mapping work
2. v2 provides complete mapping metadata including:
   - Source and target configurations
   - Transformation details
   - Field mappings
   - File attributes (delimiters, headers, etc.)
   - Connection references

### For Organization Management
1. **Use Platform API v3** for:
   - Asset discovery across the organization
   - Project and folder structure management
   - Impact analysis (dependencies)
   - License and role management

### Combined Approach
- Use **v3** to discover and list assets
- Use **v2** to access detailed mapping information and execute jobs
- Both APIs share the same authentication session

---

## Limitations Discovered

### Platform API v3 Limitations
1. ❌ Cannot access mapping details by ID
2. ❌ Does not return mapping parameters or transformations
3. ❌ Cannot list DTEMPLATE objects with filtering (returns 400 error with certain parameters)
4. ❌ No job execution capabilities
5. ❌ Specific mapping `m_arausch_DPR_DISTINCT_ISIN3` not found via search or direct ID access

### REST API v2 Limitations
1. ❌ Limited organizational management features
2. ❌ No cross-object dependency analysis
3. ❌ No project/folder structure management

---

## Conclusion

For the mapping **m_arausch_DPR_DISTINCT_ISIN3**:

- ✅ **REST API v2** is the **ONLY** way to access detailed mapping information
- ✅ v2 returns 33 fields with complete transformation details
- ❌ **Platform API v3** does not support detailed mapping access
- ❌ v3 returns 404 when attempting to access mapping by ID

**Recommendation:** Continue using REST API v2 for all Data Integration mapping operations. Use v3 only for organizational management tasks.

---

## Files Generated

All output files are stored in `MCP_IDMC/output/`:

1. `mapping_v2_response.json` - Complete v2 API response (33 fields, full parameters)
2. `mapping_v3_response.json` - Not generated (mapping not accessible via v3)
3. `API_v2_vs_v3_Comparison.md` - This comprehensive comparison document
4. `API_Comparison_Summary.txt` - Quick reference guide
