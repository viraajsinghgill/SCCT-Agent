import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from engine.db_engine import db_engine

print("Testing Snowflake Cortex functions...")
models = ['llama3.1-70b', 'mistral-large2', 'snowflake-arctic', 'llama3-8b']
for m in models:
    try:
        sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{m}', 'Respond with one word: READY') AS resp;"
        df = db_engine.execute_query(sql)
        print(f"Model {m}: {df.iloc[0]['resp']}")
        break
    except Exception as e:
        print(f"Model {m} failed: {e}")
