#!/usr/bin/env python3
"""
MySQL MCP Server - Live Testing Script
=====================================

Test script to verify MySQL MCP server functionality with real database connection.
"""

import asyncio
import sys
import os
import json
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_database_connection():
    """Test basic database connection."""
    print("🔌 Testing Database Connection...")
    try:
        from mysql_server import get_context
        
        async with get_context() as ctx:
            async with ctx.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1 as test_value")
                    result = await cursor.fetchone()
                    print(f"✅ Database connection successful: {result}")
                    return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_list_tables():
    """Test list_tables tool."""
    print("\n📋 Testing list_tables tool...")
    try:
        from mysql_server import list_tables
        
        result = await list_tables()
        print(f"📊 Tables result: {json.dumps(result, indent=2)}")
        
        if result["status"] == "success":
            print(f"✅ Found {result['count']} tables")
            if result["tables"]:
                print("📋 Tables:")
                for table in result["tables"][:5]:  # Show first 5 tables
                    print(f"   - {table}")
            return True
        else:
            print(f"❌ Failed to list tables: {result['message']}")
            return False
    except Exception as e:
        print(f"❌ list_tables error: {e}")
        return False

async def test_get_schema():
    """Test get_schema tool."""
    print("\n🔍 Testing get_schema tool...")
    try:
        from mysql_server import list_tables, get_schema
        
        # First get a table to test
        tables_result = await list_tables()
        if tables_result["status"] == "success" and tables_result["tables"]:
            test_table = tables_result["tables"][0]
            print(f"📊 Testing schema for table: {test_table}")
            
            result = await get_schema(test_table)
            print(f"📋 Schema result: {json.dumps(result, indent=2)}")
            
            if result["status"] == "success":
                print(f"✅ Schema retrieved for {test_table}")
                print(f"📊 Found {result['count']} columns")
                if result["columns"]:
                    print("📋 Columns:")
                    for col in result["columns"][:3]:  # Show first 3 columns
                        print(f"   - {col['field']}: {col['type']}")
                return True
            else:
                print(f"❌ Failed to get schema: {result['message']}")
                return False
        else:
            print("⚠️ No tables found to test schema")
            return False
    except Exception as e:
        print(f"❌ get_schema error: {e}")
        return False

async def test_query_data():
    """Test query_data tool."""
    print("\n📊 Testing query_data tool...")
    try:
        from mysql_server import query_data
        
        # Test basic query
        test_query = "SELECT 1 as test_col, 'Hello MySQL' as message"
        print(f"🔍 Testing query: {test_query}")
        
        result = await query_data(test_query, limit=5)
        print(f"📋 Query result: {json.dumps(result, indent=2, default=str)}")
        
        if result["success"]:
            print(f"✅ Query executed successfully")
            print(f"📊 Returned {result['row_count']} rows")
            return True
        else:
            print(f"❌ Query failed: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ query_data error: {e}")
        return False

async def test_security_features():
    """Test security features."""
    print("\n🔒 Testing Security Features...")
    try:
        from mysql_server import query_data
        
        # Test 1: Try INSERT (should be blocked)
        print("🚫 Testing INSERT blocking...")
        result = await query_data("INSERT INTO dummy VALUES (1)", limit=5)
        if not result["success"] and "Only SELECT queries" in result["error"]:
            print("✅ INSERT queries properly blocked")
        else:
            print("❌ INSERT should be blocked")
            return False
        
        # Test 2: Try UPDATE (should be blocked)
        print("🚫 Testing UPDATE blocking...")
        result = await query_data("UPDATE dummy SET id = 1", limit=5)
        if not result["success"] and "Only SELECT queries" in result["error"]:
            print("✅ UPDATE queries properly blocked")
        else:
            print("❌ UPDATE should be blocked")
            return False
        
        # Test 3: Try DELETE (should be blocked)
        print("🚫 Testing DELETE blocking...")
        result = await query_data("DELETE FROM dummy", limit=5)
        if not result["success"] and "Only SELECT queries" in result["error"]:
            print("✅ DELETE queries properly blocked")
        else:
            print("❌ DELETE should be blocked")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Security test error: {e}")
        return False

async def test_resources():
    """Test MCP resources."""
    print("\n📋 Testing MCP Resources...")
    try:
        from mysql_server import get_status, get_tables_resource
        
        # Test status resource
        print("🔍 Testing mysql://status resource...")
        status = await get_status()
        print(f"📊 Status: {status}")
        
        # Test tables resource
        print("🔍 Testing mysql://tables resource...")
        tables = await get_tables_resource()
        print(f"📋 Tables resource: {tables}")
        
        return True
    except Exception as e:
        print(f"❌ Resources test error: {e}")
        return False

async def run_all_tests():
    """Run all tests."""
    print("🧪 MySQL MCP Server - Live Testing")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("List Tables", test_list_tables),
        ("Get Schema", test_get_schema),
        ("Query Data", test_query_data),
        ("Security Features", test_security_features),
        ("MCP Resources", test_resources),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {status} {test_name}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! MySQL MCP Server is fully functional.")
    elif passed > 0:
        print("⚠️ Some tests passed. Server is partially functional.")
    else:
        print("❌ All tests failed. Check database connection and configuration.")
    
    return passed == total

if __name__ == "__main__":
    import mysql_server
    
    async def main():
        try:
            success = await run_all_tests()
        finally:
            # Cleanup global context to prevent connection warnings
            await mysql_server.cleanup_global_context()
        return success
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
