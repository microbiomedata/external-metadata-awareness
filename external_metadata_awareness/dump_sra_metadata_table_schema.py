from google.cloud import bigquery
import json
import yaml

# Use the same values as your working script
PROJECT_ID = "nmdc-377118"
DATASET_ID = "nih-sra-datastore.sra"  # Keep this as in your working script
TABLE_ID = "metadata"

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# Correct way to reference the table
table_ref = bigquery.TableReference.from_string(f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")

# Fetch table metadata
table = client.get_table(table_ref)

# Extract schema
schema_json = [
    {"name": field.name, "type": field.field_type, "mode": field.mode}
    for field in table.schema
]

# Save schema as JSON
with open("schema.json", "w") as f:
    json.dump(schema_json, f, indent=2)
print("Schema saved as schema.json")

# Convert to YAML
schema_yaml = yaml.dump(schema_json, default_flow_style=False)

# Save schema as YAML
with open("schema.yaml", "w") as f:
    f.write(schema_yaml)
print("Schema saved as schema.yaml")
