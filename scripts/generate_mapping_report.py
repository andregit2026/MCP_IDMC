import json
from datetime import datetime

# Read the mapping template file
with open('C:/Users/arausch/Documents/VS_Studio/MCP_IDMC/mapping_sample.json', 'r') as f:
    api_data = json.load(f)

# Read the exported template file
with open('C:/Users/arausch/Downloads/m_arausch_DPR_DISTINCT_ISIN3-1772994711887/Explore/Moduna/arausch/extracted/bin/@3.bin', 'r') as f:
    export_data = json.load(f)

# Extract general info
name = api_data.get('name', 'N/A')
description = api_data.get('description', 'N/A')
created_by = api_data.get('createdBy', 'N/A')
updated_by = api_data.get('updatedBy', 'N/A')
create_time = api_data.get('createTime', 'N/A')
update_time = api_data.get('updateTime', 'N/A')
valid = api_data.get('valid', False)
document_type = api_data.get('documentType', 'N/A')
mapping_id = api_data.get('id', 'N/A')

# Extract transformations
template = export_data['content']
transformations = template.get('transformations', [])

# ============================================================================
# IDMC Data Integration Transformation Type Mapping
# ============================================================================
# Maps Informatica's internal $$class IDs to transformation type names.
# Class IDs are discovered from exported mapping .bin files.
#
# Known transformation types in IDMC Data Integration:
# - Source: Reads and extracts data from source objects
# - Target: Loads data into target systems
# - Expression: Row-wise manipulation and calculations (passive)
# - Filter: Filters rows based on conditions (active)
# - Aggregator: Performs aggregate calculations (SUM, AVG, COUNT, etc.)
# - Router: Filters data into multiple groups based on multiple conditions
# - Joiner: Joins data from two sources
# - Lookup: Retrieves related data from lookup tables
# - Sorter: Sorts data based on fields
# - Union: Merges data from multiple pipelines
# - Normalizer: Denormalizes data structures
# - Rank: Ranks data based on criteria
# - Sequence Generator: Generates unique numeric values
# - Transaction Control: Defines commit/rollback transactions
# - Update Strategy: Flags rows for INSERT/DELETE/UPDATE/REJECT
#
# Note: Additional transformation types may exist. To discover their class IDs,
# export a mapping containing that transformation and examine the $$class value
# in the @3.bin file's metadata.
# ============================================================================

type_map = {
    # Confirmed mappings from exported templates
    7: 'SOURCE',
    8: 'EXPRESSION',
    9: 'AGGREGATOR',
    10: 'TARGET',

    # Additional transformation types (class IDs to be discovered):
    # 11: 'FILTER',          # TBD - needs class ID from export
    # 12: 'ROUTER',          # TBD - needs class ID from export
    # 13: 'JOINER',          # TBD - needs class ID from export
    # 14: 'LOOKUP',          # TBD - needs class ID from export
    # 15: 'SORTER',          # TBD - needs class ID from export
    # 16: 'UNION',           # TBD - needs class ID from export
    # 17: 'NORMALIZER',      # TBD - needs class ID from export
    # 18: 'RANK',            # TBD - needs class ID from export
    # 19: 'SEQUENCE_GENERATOR',  # TBD - needs class ID from export
    # 20: 'TRANSACTION_CONTROL', # TBD - needs class ID from export
    # 21: 'UPDATE_STRATEGY',     # TBD - needs class ID from export
}

# Group transformations by type
sources = []
expressions = []
aggregators = []
targets = []

for tx in transformations:
    tx_class = tx.get('$$class')
    tx_type = type_map.get(tx_class, f'UNKNOWN({tx_class})')
    tx_name = tx.get('name', 'unnamed')

    tx_info = {
        'name': tx_name,
        'type': tx_type,
        'details': []
    }

    if tx_type == 'SOURCE':
        data_adapter = tx.get('dataAdapter', {})
        obj = data_adapter.get('object', {})
        obj_name = obj.get('name', 'N/A')
        tx_info['object'] = obj_name
        sources.append(tx_info)

    elif tx_type == 'EXPRESSION':
        annotations = tx.get('annotations', [])
        comments = []
        for ann in annotations:
            body = ann.get('body', '')
            if body:
                comments.append(body)
        tx_info['comments'] = comments
        expressions.append(tx_info)

    elif tx_type == 'AGGREGATOR':
        group_by = tx.get('groupByFieldsList', {})
        fields = group_by.get('fields', [])
        group_by_fields = [f.get('fieldName', 'unknown') for f in fields]

        agg_fields = tx.get('fields', [])
        aggregate_expressions = []
        for f in agg_fields:
            field_name = f.get('name', 'unknown')
            expr = f.get('expression', '')
            aggregate_expressions.append({'field': field_name, 'expression': expr})

        tx_info['group_by_fields'] = group_by_fields
        tx_info['aggregate_expressions'] = aggregate_expressions
        aggregators.append(tx_info)

    elif tx_type == 'TARGET':
        data_adapter = tx.get('dataAdapter', {})
        obj = data_adapter.get('object', {})
        obj_name = obj.get('name', 'N/A')
        tx_info['object'] = obj_name
        targets.append(tx_info)

# Generate HTML
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Mapping Analysis</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .content {{
            padding: 30px;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .info-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 5px;
        }}

        .info-card .label {{
            font-weight: bold;
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}

        .info-card .value {{
            color: #333;
            font-size: 1.1em;
        }}

        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}

        .status-valid {{
            background: #d4edda;
            color: #155724;
        }}

        .status-invalid {{
            background: #f8d7da;
            color: #721c24;
        }}

        .section {{
            margin-top: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}

        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}

        .stat-box .number {{
            font-size: 2.5em;
            font-weight: bold;
            display: block;
        }}

        .stat-box .label {{
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
        }}

        .transformation-list {{
            display: grid;
            gap: 20px;
        }}

        .transformation-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 5px solid;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .transformation-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}

        .transformation-card.source {{ border-left-color: #28a745; }}
        .transformation-card.expression {{ border-left-color: #ffc107; }}
        .transformation-card.aggregator {{ border-left-color: #17a2b8; }}
        .transformation-card.target {{ border-left-color: #dc3545; }}

        .transformation-card .tx-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}

        .transformation-card .tx-type {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 0.85em;
            margin-right: 15px;
            text-transform: uppercase;
        }}

        .tx-type.source {{ background: #28a745; color: white; }}
        .tx-type.expression {{ background: #ffc107; color: #333; }}
        .tx-type.aggregator {{ background: #17a2b8; color: white; }}
        .tx-type.target {{ background: #dc3545; color: white; }}

        .transformation-card .tx-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}

        .transformation-card .tx-details {{
            margin-top: 10px;
            color: #666;
        }}

        .transformation-card .detail-item {{
            margin: 8px 0;
            padding-left: 15px;
            border-left: 2px solid #ddd;
        }}

        .transformation-card .detail-label {{
            font-weight: bold;
            color: #555;
        }}

        .flow-diagram {{
            background: #f8f9fa;
            border: 2px dashed #667eea;
            border-radius: 8px;
            padding: 30px;
            margin-top: 30px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }}

        .flow-diagram pre {{
            margin: 0;
            color: #333;
            line-height: 2;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{name}</h1>
            <p class="subtitle">IDMC Data Integration Mapping Analysis</p>
        </div>

        <div class="content">
            <!-- General Information -->
            <div class="section">
                <h2 class="section-title">General Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <div class="label">Mapping ID</div>
                        <div class="value">{mapping_id}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Document Type</div>
                        <div class="value">{document_type}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Status</div>
                        <div class="value">
                            <span class="status-badge {'status-valid' if valid else 'status-invalid'}">
                                {'VALID' if valid else 'INVALID'}
                            </span>
                        </div>
                    </div>
                    <div class="info-card">
                        <div class="label">Description</div>
                        <div class="value">{description if description else 'N/A'}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Created By</div>
                        <div class="value">{created_by}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Updated By</div>
                        <div class="value">{updated_by}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Created</div>
                        <div class="value">{create_time}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Last Updated</div>
                        <div class="value">{update_time}</div>
                    </div>
                </div>
            </div>

            <!-- Transformation Summary -->
            <div class="section">
                <h2 class="section-title">Transformation Summary</h2>
                <div class="summary-stats">
                    <div class="stat-box">
                        <span class="number">{len(sources)}</span>
                        <span class="label">Source</span>
                    </div>
                    <div class="stat-box">
                        <span class="number">{len(expressions)}</span>
                        <span class="label">Expression</span>
                    </div>
                    <div class="stat-box">
                        <span class="number">{len(aggregators)}</span>
                        <span class="label">Aggregator</span>
                    </div>
                    <div class="stat-box">
                        <span class="number">{len(targets)}</span>
                        <span class="label">Target</span>
                    </div>
                    <div class="stat-box">
                        <span class="number">{len(transformations)}</span>
                        <span class="label">Total</span>
                    </div>
                </div>
            </div>

            <!-- Detailed Transformations -->
            <div class="section">
                <h2 class="section-title">Detailed Transformations</h2>
                <div class="transformation-list">
'''

# Add sources
for src in sources:
    html += f'''
                    <div class="transformation-card source">
                        <div class="tx-header">
                            <span class="tx-type source">Source</span>
                            <span class="tx-name">{src['name']}</span>
                        </div>
                        <div class="tx-details">
                            <div class="detail-item">
                                <span class="detail-label">Object:</span> {src['object']}
                            </div>
                        </div>
                    </div>
'''

# Add expressions
for exp in expressions:
    html += f'''
                    <div class="transformation-card expression">
                        <div class="tx-header">
                            <span class="tx-type expression">Expression</span>
                            <span class="tx-name">{exp['name']}</span>
                        </div>
                        <div class="tx-details">
'''
    if exp.get('comments'):
        for comment in exp['comments']:
            html += f'''
                            <div class="detail-item">
                                <span class="detail-label">Comment:</span> {comment}
                            </div>
'''
    html += '''
                        </div>
                    </div>
'''

# Add aggregators
for agg in aggregators:
    html += f'''
                    <div class="transformation-card aggregator">
                        <div class="tx-header">
                            <span class="tx-type aggregator">Aggregator</span>
                            <span class="tx-name">{agg['name']}</span>
                        </div>
                        <div class="tx-details">
'''
    if agg.get('group_by_fields'):
        html += '''
                            <div class="detail-item">
                                <span class="detail-label">Group By Fields:</span><br>
'''
        for field in agg['group_by_fields']:
            html += f'                                &nbsp;&nbsp;• {field}<br>\n'
        html += '''
                            </div>
'''
    if agg.get('aggregate_expressions'):
        html += '''
                            <div class="detail-item">
                                <span class="detail-label">Aggregate Expressions:</span><br>
'''
        for expr in agg['aggregate_expressions']:
            html += f'                                &nbsp;&nbsp;• {expr["field"]}: {expr["expression"]}<br>\n'
        html += '''
                            </div>
'''
    html += '''
                        </div>
                    </div>
'''

# Add targets
for tgt in targets:
    html += f'''
                    <div class="transformation-card target">
                        <div class="tx-header">
                            <span class="tx-type target">Target</span>
                            <span class="tx-name">{tgt['name']}</span>
                        </div>
                        <div class="tx-details">
                            <div class="detail-item">
                                <span class="detail-label">Object:</span> {tgt['object']}
                            </div>
                        </div>
                    </div>
'''

html += f'''
                </div>
            </div>

            <!-- Data Flow -->
            <div class="section">
                <h2 class="section-title">Data Flow Diagram</h2>
                <div class="flow-diagram">
                    <pre>
{sources[0]['name']} ({sources[0]['object']})
    ↓
{expressions[0]['name']} (Extract ISIN field only)
    ↓
{aggregators[0]['name']} (Group by ISIN - get distinct values)
    ↓
    ├─→ {targets[0]['name']} (Write to {targets[0]['object']})
    └─→ {aggregators[1]['name']} (Count records)
          ↓
        {targets[1]['name']} (Write to {targets[1]['object']})
                    </pre>
                </div>
            </div>

            <!-- Purpose -->
            <div class="section">
                <h2 class="section-title">Mapping Purpose</h2>
                <div class="info-card">
                    <p style="font-size: 1.1em; line-height: 1.8; color: #333;">
                        This mapping reads a list of <strong>ISIN</strong> (International Securities Identification Numbers)
                        from a CSV file, extracts only the ISIN column, creates a list of distinct/unique ISIN values,
                        and outputs:
                    </p>
                    <ol style="margin-top: 15px; margin-left: 20px; font-size: 1.05em; line-height: 1.8; color: #333;">
                        <li>The distinct ISIN list to a file (<strong>Distinct_ISIN_list</strong>)</li>
                        <li>The total count of records to a staging database table (<strong>STAGING/DPR_DUMMY_TARGET</strong>)</li>
                    </ol>
                    <p style="margin-top: 15px; font-size: 1.05em; line-height: 1.8; color: #333;">
                        The mapping performs <strong>deduplication</strong> of ISIN values and provides both
                        the cleaned data and metrics about the processing.
                    </p>
                </div>
            </div>
        </div>

        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | IDMC Mapping Analysis Tool
        </div>
    </div>
</body>
</html>'''

# Save HTML file
output_dir = 'C:/Users/arausch/Documents/VS_Studio/MCP_IDMC/output'
import os
os.makedirs(output_dir, exist_ok=True)
output_file = f'{output_dir}/m_arausch_DPR_DISTINCT_ISIN3_analysis.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'HTML analysis report created: {output_file}')
