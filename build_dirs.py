# SCCT Agent Builder
import os, sys, json

os.makedirs('ontology', exist_ok=True)
os.makedirs('snowflake_sql', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('engine', exist_ok=True)
os.makedirs('mcp_server', exist_ok=True)
os.makedirs('skills/supply-chain-ontology', exist_ok=True)
os.makedirs('skills/metric-governance-validator', exist_ok=True)
os.makedirs('tests', exist_ok=True)
print('Directories created successfully.')
