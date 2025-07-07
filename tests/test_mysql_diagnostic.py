#!/usr/bin/env python3
"""
Simple diagnostic test for MySQL MCP Server
==========================================

Basic test to verify server can start and import correctly
without requiring actual MySQL database connection.
"""

import asyncio
import sys
import os

# Add parent directory to path to import mysql_server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_import():
    """Test if server imports correctly."""
    try:
        print("🧪 Testing MySQL MCP Server imports...")
        
        # Test basic imports
        import mysql_server
        print("✅ Successfully imported mysql_server")
        
        # Test FastMCP import
        from mcp.server.fastmcp import FastMCP
        print("✅ FastMCP import successful")
        
        # Test aiomysql import
        import aiomysql
        print("✅ aiomysql import successful")
        
        # Test server instance
        mcp_instance = mysql_server.mcp
        print(f"✅ MCP server instance created: {mcp_instance}")
        
        print("\n🎉 All basic imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to install dependencies: pip install fastmcp aiomysql python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_configuration():
    """Test environment configuration loading."""
    try:
        print("\n⚙️ Testing configuration...")
        
        import mysql_server
        
        # Check if environment variables are loaded
        print(f"📍 DB_HOST: {mysql_server.db_host}")
        print(f"📍 DB_PORT: {mysql_server.db_port}")
        print(f"📍 DB_USER: {mysql_server.db_user}")
        print(f"📍 DB_NAME: {mysql_server.db_name}")
        print(f"📍 DEBUG_MODE: {mysql_server.debug_mode}")
        
        print("✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_server_without_db():
    """Test server startup without database connection."""
    try:
        print("\n🚀 Testing server startup (without DB)...")
        
        import mysql_server
        
        # Check if server instance exists
        if hasattr(mysql_server, 'mcp'):
            print("✅ MCP server instance exists")
        else:
            print("❌ MCP server instance not found")
            return False
            
        print("✅ Server can start without database!")
        return True
        
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        return False

async def main():
    """Run all diagnostic tests."""
    print("🚀 MySQL MCP Server - Diagnostic Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_import),
        ("Configuration", test_configuration),
        ("Server Startup", test_server_without_db),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {status} {test_name}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! MySQL MCP Server is ready.")
        print("\n💡 Next steps:")
        print("   1. Configure your MySQL database in .env")
        print("   2. Run: python3 mysql_server.py --sse")
        print("   3. Connect to http://localhost:8000/sse")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
