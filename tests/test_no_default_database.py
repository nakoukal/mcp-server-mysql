#!/usr/bin/env python3
"""
Test script without default database - testing when DB_NAME is not set
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Temporarily remove DB_NAME from environment to test without default DB
if 'DB_NAME' in os.environ:
    original_db_name = os.environ['DB_NAME']
    del os.environ['DB_NAME']
else:
    original_db_name = None

from mysql_server import list_databases, list_tables, get_schema, cleanup_global_context

async def test_without_default_database():
    """Test functionality when no default database is configured"""
    print("🧪 Testing MCP Server WITHOUT Default Database")
    print("=" * 55)
    
    # Test 1: List databases should always work
    print("\n1️⃣ Testing list_databases (should always work)...")
    databases_result = await list_databases()
    print(f"📋 Available databases: {databases_result}")
    
    if databases_result["status"] == "success" and databases_result["databases"]:
        available_dbs = databases_result["databases"]
        test_db = available_dbs[0]  # Use first available database
        
        # Test 2: list_tables without database parameter (should fail)
        print("\n2️⃣ Testing list_tables without database parameter (should fail)...")
        tables_result_no_db = await list_tables()
        print(f"📊 Result: {tables_result_no_db}")
        
        # Test 3: list_tables with database parameter (should work)
        print(f"\n3️⃣ Testing list_tables with database='{test_db}' (should work)...")
        tables_result_with_db = await list_tables(database=test_db)
        print(f"📊 Result: {tables_result_with_db}")
        
        if (tables_result_with_db["status"] == "success" and 
            tables_result_with_db["tables"]):
            
            first_table = tables_result_with_db["tables"][0]
            
            # Test 4: get_schema without database parameter (should fail)
            print(f"\n4️⃣ Testing get_schema for '{first_table}' without database (should fail)...")
            schema_result_no_db = await get_schema(first_table)
            print(f"🏗️ Result: {schema_result_no_db}")
            
            # Test 5: get_schema with database parameter (should work)
            print(f"\n5️⃣ Testing get_schema for '{first_table}' with database='{test_db}' (should work)...")
            schema_result_with_db = await get_schema(first_table, database=test_db)
            print(f"🏗️ Result: {schema_result_with_db}")
    
    print("\n🏁 No-default-database tests completed!")

async def main():
    """Main test function with proper cleanup."""
    try:
        await test_without_default_database()
    finally:
        # Cleanup global context
        await cleanup_global_context()
        
        # Restore original DB_NAME if it existed
        if original_db_name is not None:
            os.environ['DB_NAME'] = original_db_name

if __name__ == "__main__":
    print("🚀 Starting no-default-database tests...")
    asyncio.run(main())
