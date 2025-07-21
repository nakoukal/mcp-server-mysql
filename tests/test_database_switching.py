#!/usr/bin/env python3
"""
Test script for database switching functionality
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mysql_server import list_databases, change_database, list_tables, query_data, get_schema, cleanup_global_context

async def test_database_operations():
    """Test database switching functionality"""
    print("🧪 Testing Database Switching Functionality")
    print("=" * 50)
    
    # Test 1: List available databases
    print("\n1️⃣ Testing list_databases...")
    databases_result = await list_databases()
    print(f"📋 Available databases: {databases_result}")
    
    if databases_result["status"] == "success" and databases_result["databases"]:
        available_dbs = databases_result["databases"]
        print(f"✅ Found {len(available_dbs)} databases: {', '.join(available_dbs)}")
        
        # Test 2: Change database (if we have multiple databases)
        if len(available_dbs) > 1:
            target_db = available_dbs[0]  # Pick first available database
            print(f"\n2️⃣ Testing change_database to '{target_db}'...")
            
            change_result = await change_database(target_db)
            print(f"🔄 Change database result: {change_result}")
            
            if change_result["status"] == "success":
                print(f"✅ Successfully changed to database: {target_db}")
                
                # Test 3: List tables in new database
                print(f"\n3️⃣ Testing list_tables in '{target_db}'...")
                tables_result = await list_tables()
                print(f"📊 Tables in {target_db}: {tables_result}")
                
                # Test 4: Per-query database specification
                if len(available_dbs) > 1:
                    other_db = available_dbs[1]
                    print(f"\n4️⃣ Testing per-query database switch to '{other_db}'...")
                    
                    # List tables in different database without changing global context
                    per_query_result = await list_tables(database=other_db)
                    print(f"📊 Tables in {other_db} (per-query): {per_query_result}")
                    
                    # Test query with specific database
                    print(f"\n5️⃣ Testing query_data with database parameter...")
                    query_result = await query_data(
                        "SELECT * FROM User", 
                        limit=3, 
                        database=other_db
                    )
                    print(f"🔍 Query result from {other_db}: {query_result}")
                    
                    # Test SHOW command with database parameter
                    print(f"\n5️⃣b Testing SHOW TABLES with database parameter...")
                    show_result = await query_data(
                        "SHOW TABLES", 
                        limit=5, 
                        database=other_db
                    )
                    print(f"🔍 SHOW TABLES result from {other_db}: {show_result}")
                    if show_result['success']:
                        table_names = []
                        for row in show_result['rows'][:5]:
                            # Get table name from the row (key varies by database)
                            table_name = list(row.values())[0] if row else None
                            if table_name:
                                table_names.append(table_name)
                        print(f"📊 First 5 tables: {table_names}")
                    else:
                        print("📊 Error getting tables")
        
        # Test 6: Schema with database parameter
        if available_dbs:
            test_db = available_dbs[0]
            tables_for_schema = await list_tables(database=test_db)
            
            if (tables_for_schema["status"] == "success" and 
                tables_for_schema["tables"]):
                
                first_table = tables_for_schema["tables"][0]
                print(f"\n6️⃣ Testing get_schema for '{first_table}' in '{test_db}'...")
                
                schema_result = await get_schema(first_table, database=test_db)
                print(f"🏗️ Schema result: {schema_result}")
    
    else:
        print("❌ No databases found or error occurred")
    
    print("\n🏁 Database switching tests completed!")

async def main():
    """Main test function with proper cleanup."""
    try:
        await test_database_operations()
    finally:
        # Cleanup global context to prevent connection warnings
        await cleanup_global_context()

if __name__ == "__main__":
    print("🚀 Starting database switching tests...")
    asyncio.run(main())
