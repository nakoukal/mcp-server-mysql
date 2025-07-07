#!/usr/bin/env python3
"""
mysql-mcp-server MCP Server - FastMCP Implementation
==================================================

Official implementation using MCP Python SDK with FastMCP.
Provides only database operations as MCP tools:

TOOLS:
- query_data: Execute safe database queries
- list_tables: List available tables  
- get_schema: Get table schema information

RESOURCES:
- mysql://status: Server health check
- mysql://tables: Tables list

Transport: stdio, sse, streamable-http
"""

import asyncio
import os
import logging
from typing import List, Optional, Any, Dict
from dataclasses import dataclass
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP
import aiomysql

# === CONFIGURATION ===
from dotenv import load_dotenv
load_dotenv()

# Environment variables
db_host = os.getenv('DB_HOST', 'localhost')
db_port = int(os.getenv('DB_PORT', '3306'))
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', '')
db_name = os.getenv('DB_NAME', 'test')
debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Logging setup
logging.basicConfig(
    level=logging.DEBUG if debug_mode else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mysql-mcp")

# === GLOBAL CONTEXT ===
_global_context: Optional['MysqlContext'] = None

@dataclass
class MysqlContext:
    """Global context for MySQL operations."""
    pool: aiomysql.Pool

@asynccontextmanager
async def get_context() -> AsyncIterator[MysqlContext]:
    """Get or create global MySQL context."""
    global _global_context
    
    if _global_context is None:
        logger.info("🔄 Initializing MySQL context...")
        
        # Create MySQL connection pool
        pool = await aiomysql.create_pool(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            db=db_name,
            charset='utf8mb4',
            autocommit=True,
            minsize=1,
            maxsize=10
        )
        
        _global_context = MysqlContext(pool=pool)
        logger.info("✅ MySQL context initialized")
    
    yield _global_context

# === FASTMCP SERVER ===
mcp = FastMCP("mysql-mcp-server")

# === MCP TOOLS ===
@mcp.tool()
async def query_data(query: str, limit: int = 100) -> Dict[str, Any]:
    """
    Execute a safe database query.
    
    Args:
        query: SQL query to execute (read-only operations only)
        limit: Maximum number of rows to return
        
    Returns:
        Query results with metadata
    """
    async with get_context() as ctx:
        try:
            # Safety check - only allow SELECT queries
            query_upper = query.strip().upper()
            if not query_upper.startswith('SELECT'):
                return {
                    "status": "error",
                    "message": "Only SELECT queries are allowed for safety",
                    "rows": [],
                    "count": 0
                }
            
            logger.info(f"📊 Executing query: {query[:100]}...")
            
            async with ctx.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    # Add LIMIT if not present
                    if 'LIMIT' not in query_upper:
                        query = f"{query} LIMIT {limit}"
                    
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
                    
                    # Convert rows to list of dicts
                    result_rows = [dict(row) for row in rows]
                    
                    return {
                        "status": "success",
                        "message": "Query executed successfully",
                        "rows": result_rows,
                        "count": len(result_rows)
                    }
            
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "rows": [],
                "count": 0
            }

@mcp.tool()
async def list_tables() -> Dict[str, Any]:
    """
    List all available database tables.
    
    Returns:
        List of tables with basic information
    """
    async with get_context() as ctx:
        try:
            logger.info("📋 Listing database tables...")
            
            async with ctx.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute("SHOW TABLES")
                    rows = await cursor.fetchall()
                    
                    # Extract table names
                    tables = []
                    for row in rows:
                        # MySQL returns table names in different formats
                        table_name = list(row.values())[0] if row else None
                        if table_name:
                            tables.append(table_name)
                    
                    return {
                        "status": "success",
                        "message": "Tables retrieved successfully",
                        "tables": tables,
                        "count": len(tables)
                    }
            
        except Exception as e:
            error_msg = f"Failed to list tables: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "tables": [],
                "count": 0
            }

@mcp.tool()
async def get_schema(table_name: str) -> Dict[str, Any]:
    """
    Get detailed schema information for a specific table.
    
    Args:
        table_name: Name of the table to analyze
        
    Returns:
        Table schema with column details
    """
    async with get_context() as ctx:
        try:
            logger.info(f"🔍 Getting schema for table: {table_name}")
            
            async with ctx.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    # Get table structure
                    await cursor.execute(f"DESCRIBE {table_name}")
                    columns = await cursor.fetchall()
                    
                    # Convert to more readable format
                    schema_info = []
                    for col in columns:
                        schema_info.append({
                            "field": col["Field"],
                            "type": col["Type"],
                            "null": col["Null"],
                            "key": col["Key"],
                            "default": col["Default"],
                            "extra": col["Extra"]
                        })
                    
                    return {
                        "status": "success",
                        "message": f"Schema for {table_name} retrieved successfully",
                        "table": table_name,
                        "columns": schema_info,
                        "count": len(schema_info)
                    }
            
        except Exception as e:
            error_msg = f"Failed to get schema for {table_name}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "table": table_name,
                "columns": [],
                "count": 0
            }

# === MCP RESOURCES ===
@mcp.resource("mysql://status")
async def get_status() -> str:
    """Get MySQL server health status."""
    try:
        async with get_context() as ctx:
            async with ctx.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
            return "✅ MySQL server is healthy and ready"
    except Exception as e:
        return f"❌ MySQL server error: {str(e)}"

@mcp.resource("mysql://tables")
async def get_tables_resource() -> str:
    """Get list of all database tables as text resource."""
    try:
        result = await list_tables()
        if result["status"] == "success":
            tables = result.get("tables", [])
            if tables:
                return "\n".join([f"📊 {table}" for table in tables])
            else:
                return "📋 No tables found in database"
        else:
            return f"❌ Error: {result['message']}"
    except Exception as e:
        return f"❌ Failed to get tables: {str(e)}"

# === MAIN EXECUTION ===
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MySQL MCP Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE/HTTP (default: 8000)"
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting minimalist MySQL MCP server...")
    logger.info(f"📊 Transport: {args.transport}")
    logger.info(f"🔌 Port: {args.port}")
    
    if args.transport == "streamable-http":
        # Streamable HTTP transport for web integration
        logger.info(f"🌐 Starting HTTP transport on 0.0.0.0:{args.port}...")
        mcp.run(transport="streamable-http")
    elif args.transport == "sse":
        # SSE transport for real-time applications  
        logger.info(f"📡 Starting SSE transport on 0.0.0.0:{args.port}...")
        mcp.run(transport="sse")
    else:
        # STDIO transport for command-line tools (default)
        logger.info("📝 Starting STDIO transport...")
        mcp.run(transport="stdio")
