#!/usr/bin/env python3
"""
Test script truly without default database - completely isolates from environment
"""

import asyncio
import sys
import os

# Completely remove DB_NAME from environment before importing
original_env = dict(os.environ)
if 'DB_NAME' in os.environ:
    del os.environ['DB_NAME']

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_truly_without_default_db():
    """Test with completely fresh import without DB_NAME"""
    print("🧪 Testing MCP Server TRULY WITHOUT Default Database")
    print("=" * 60)
    print(f"DB_NAME in environment: {'DB_NAME' in os.environ}")
    
    # Import after removing DB_NAME from environment
    from mysql_server import list_databases, list_tables, get_schema, cleanup_global_context, db_name
    
    print(f"db_name variable value: {repr(db_name)}")
    
    # Test 1: List databases should always work
    print("\n1️⃣ Testing list_databases (should always work)...")
    databases_result = await list_databases()
    print(f"📋 Available databases: {databases_result}")
    
    if databases_result["status"] == "success" and databases_result["databases"]:
        available_dbs = databases_result["databases"]
        test_db = available_dbs[0]  # Use first available database
        
        # Test 2: list_tables without database parameter (should fail if no default)
        print("\n2️⃣ Testing list_tables without database parameter...")
        tables_result_no_db = await list_tables()
        print(f"📊 Result: {tables_result_no_db}")
        
        # Test 3: list_tables with database parameter (should work)
        print(f"\n3️⃣ Testing list_tables with database='{test_db}' (should work)...")
        tables_result_with_db = await list_tables(database=test_db)
        print(f"📊 Result: {tables_result_with_db}")
        
        if (tables_result_with_db["status"] == "success" and 
            tables_result_with_db["tables"]):
            
            first_table = tables_result_with_db["tables"][0]
            
            # Test 4: get_schema without database parameter (should fail if no default)
            print(f"\n4️⃣ Testing get_schema for '{first_table}' without database...")
            schema_result_no_db = await get_schema(first_table)
            print(f"🏗️ Result: {schema_result_no_db}")
            
            # Test 5: get_schema with database parameter (should work)
            print(f"\n5️⃣ Testing get_schema for '{first_table}' with database='{test_db}' (should work)...")
            schema_result_with_db = await get_schema(first_table, database=test_db)
            print(f"🏗️ Result: {schema_result_with_db}")
    
    print("\n🏁 True no-default-database tests completed!")
    
    # Cleanup
    await cleanup_global_context()

if __name__ == "__main__":
    print("🚀 Starting true no-default-database tests...")
    try:
        asyncio.run(test_truly_without_default_db())
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)
