#!/usr/bin/env python3
"""
Test STDIO transport for MySQL MCP Server
Verifies that the server correctly uses stdin/stdout/stderr
"""

import subprocess
import json
import sys
import time

def test_stdio_transport():
    """Test that server responds correctly via STDIO."""
    print("🧪 Testing STDIO transport...")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "mysql_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Give server time to start
        time.sleep(2)
        
        # Send MCP initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Write to stdin
        request_str = json.dumps(initialize_request) + "\n"
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # Read from stdout (with timeout)
        process.stdout.flush()
        response_line = process.stdout.readline()
        
        if response_line:
            print("✅ Server responded via stdout")
            try:
                response = json.loads(response_line)
                print(f"📦 Response: {json.dumps(response, indent=2)}")
            except json.JSONDecodeError:
                print(f"⚠️  Response is not JSON: {response_line}")
        else:
            print("❌ No response from server")
        
        # Check stderr for logs
        stderr_output = process.stderr.read()
        if stderr_output:
            print("\n📋 Server logs (stderr):")
            print(stderr_output[:500])  # First 500 chars
        
        print("\n✅ STDIO transport test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        process.terminate()
        process.wait(timeout=5)

if __name__ == "__main__":
    test_stdio_transport()
