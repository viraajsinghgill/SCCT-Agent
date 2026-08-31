import re, os, sys

# Parse .env
env_path = '.env'
creds = {}
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        m = re.match(r'\$env:(\w+)\s*=\s*"([^"]+)"', line)
        if m:
            creds[m.group(1)] = m.group(2).strip()

print("Parsed credentials:")
for k, v in creds.items():
    safe_v = v if 'PASSWORD' not in k else '***'
    print(f"  {k} = {safe_v}")

# Try different account format variants
import snowflake.connector

account_raw = creds.get('SNOWFLAKE_ACCOUNT', 'IH68908')
user = creds.get('SNOWFLAKE_USER', 'vgill')
pwd  = creds.get('SNOWFLAKE_PASSWORD', '')
role = creds.get('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
wh   = creds.get('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
db   = creds.get('SNOWFLAKE_DATABASE', 'VS_SUPPLY_CHAIN_DB')
sch  = creds.get('SNOWFLAKE_SCHEMA', 'GOLD')

# Candidates to try (from Snowflake URL https://app.snowflake.com/central-india.azure/ow47655/)
candidates = [
    account_raw,                              # IH68908
    f"{account_raw}",    # IH68908.central-india.azure
    "ow47655",                                # org name only
    "ow47655.IH68908",                        # org.locator
    f"ow47655-{account_raw}",                 # org-locator
]

print()
for acct in candidates:
    try:
        print(f"Trying account: {acct} ...", end=' ', flush=True)
        conn = snowflake.connector.connect(
            account=acct, user=user, password=pwd, role=role,
            warehouse=wh, database=db, schema=sch,
            login_timeout=10, network_timeout=10
        )
        cur = conn.cursor()
        cur.execute("SELECT CURRENT_ACCOUNT(), CURRENT_ROLE()")
        row = cur.fetchone()
        conn.close()
        print(f"SUCCESS! account={row[0]}, role={row[1]}")
        print(f"\n>>> WORKING ACCOUNT STRING: {acct!r}")
        sys.exit(0)
    except Exception as e:
        print(f"FAIL: {str(e)[:80]}")

print("\nAll account format attempts failed. Check credentials or network.")
