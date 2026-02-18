#!/usr/bin/env python3
"""
mysql-mcp-server MCP Server - FastMCP Implementation
==================================================

Official implementation using MCP Python SDK with FastMCP.
Provides only database operations as MCP tools:

TOOLS:
- query_data: Execute safe database queries (SELECT only)
- execute_write: Execute write queries (INSERT, UPDATE, DELETE) with transaction support
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
db_name = os.getenv('DB_NAME')  # Optional - server can start without default database
debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Logging setup - CRITICAL: Must write to stderr for STDIO transport
import sys
logging.basicConfig(
    level=logging.DEBUG if debug_mode else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,  # Explicitly write to stderr for STDIO compatibility
    force=True
)
logger = logging.getLogger("mysql-mcp")

# === GLOBAL CONTEXT ===
_global_context: Optional['MysqlContext'] = None

@dataclass
class MysqlContext:
    """Global context for MySQL operations."""
    pool: aiomysql.Pool

async def cleanup_global_context():
    """Cleanup global context and close all connections."""
    global _global_context
    if _global_context is not None:
        logger.info("🧹 Cleaning up global MySQL context...")
        _global_context.pool.close()
        await _global_context.pool.wait_closed()
        _global_context = None
        logger.info("✅ Global context cleaned up")

@asynccontextmanager
async def get_context(database_name: Optional[str] = None) -> AsyncIterator[MysqlContext]:
    """Get or create MySQL context, optionally for a specific database."""
    global _global_context
    
    # If specific database requested, create a temporary context
    if database_name and database_name != db_name:
        logger.info(f"🔄 Creating temporary context for database: {database_name}")
        
        pool = await aiomysql.create_pool(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            db=database_name,
            charset='utf8mb4',
            autocommit=True,
            minsize=1,
            maxsize=5
        )
        
        temp_context = MysqlContext(pool=pool)
        try:
            yield temp_context
        finally:
            pool.close()
            await pool.wait_closed()
        return
    
    # Use or create global context
    if _global_context is None:
        if db_name is None:
            # If no default database is set and no specific database requested, connect without DB
            logger.info("🔄 Initializing MySQL context without default database...")
            pool = await aiomysql.create_pool(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                charset='utf8mb4',
                autocommit=True,
                minsize=1,
                maxsize=10
            )
        else:
            # Connect to default database
            logger.info(f"🔄 Initializing MySQL context with default database: {db_name}...")
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
async def change_database(database_name: str) -> Dict[str, Any]:
    """
    Change the active database for all subsequent operations.
    
    Args:
        database_name: Name of the database to switch to
        
    Returns:
        Status of the database change operation
    """
    global _global_context, db_name
    
    try:
        logger.info(f"🔄 Changing database to: {database_name}")
        
        # Close existing pool if exists
        if _global_context is not None:
            _global_context.pool.close()
            await _global_context.pool.wait_closed()
            _global_context = None
        
        # Update global database name
        db_name = database_name
        
        # Create new pool with new database
        pool = await aiomysql.create_pool(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            db=database_name,
            charset='utf8mb4',
            autocommit=True,
            minsize=1,
            maxsize=10
        )
        
        _global_context = MysqlContext(pool=pool)
        
        # Test connection
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT DATABASE()")
                current_db = await cursor.fetchone()
        
        return {
            "status": "success",
            "message": f"Successfully changed to database: {database_name}",
            "current_database": current_db[0] if current_db else database_name
        }
        
    except Exception as e:
        error_msg = f"Failed to change database to {database_name}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "current_database": None
        }

@mcp.tool()
async def query_data(query: str, limit: int = 100, database: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a SQL query and return the results.
    
    Args:
        query: SQL query to execute
        limit: Maximum number of rows to return (default: 100)
        database: Optional database name to use for this query (uses current if not specified)
        
    Returns:
        Dictionary containing query results and metadata
    """
    logger.info(f"🔍 Executing query with limit {limit}")
    logger.debug(f"Query: {query}")
    
    try:
        # Safety check - only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            return {
                "success": False,
                "error": "Only SELECT queries are allowed for safety",
                "query": query,
                "database": database or "current"
            }
        
        # Use specific database for this query or fall back to global
        async with get_context(database) as ctx:
            async with ctx.pool.acquire() as conn:
                # Switch to specific database for this connection if provided
                if database:
                    async with conn.cursor() as cursor:
                        await cursor.execute(f"USE `{database}`")
                
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    # Add LIMIT clause if not present and limit is specified
                    # But don't add LIMIT to SHOW commands as they don't support it
                    query_upper = query.upper().strip()
                    if (limit > 0 and 
                        "LIMIT" not in query_upper and 
                        not query_upper.startswith("SHOW") and
                        not query_upper.startswith("DESCRIBE") and
                        not query_upper.startswith("EXPLAIN")):
                        query = f"{query.rstrip(';')} LIMIT {limit}"
                    
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
                    
                    # If it's a SHOW command and limit is specified, manually limit results
                    if query_upper.startswith("SHOW") and limit > 0:
                        rows = rows[:limit]
                    
                    # Get column information
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    # Get current database using a regular cursor
                    async with conn.cursor() as db_cursor:
                        await db_cursor.execute("SELECT DATABASE()")
                        current_db = await db_cursor.fetchone()
                        current_database = current_db[0] if current_db and len(current_db) > 0 else database or "unknown"
                    
                    result = {
                        "success": True,
                        "rows": rows,
                        "row_count": len(rows),
                        "columns": columns,
                        "database": current_database,
                        "query": query
                    }
                    
                    logger.info(f"✅ Query executed successfully. Returned {len(rows)} rows from database '{current_database}'")
                    return result
                
    except Exception as e:
        error_msg = f"Query failed: {type(e).__name__}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "query": query,
            "database": database or "current"
        }

@mcp.tool()
async def execute_write(query: str, params: Optional[List[Any]] = None, database: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a write SQL query (INSERT, UPDATE, DELETE) with transaction support.
    The query runs inside a transaction and is automatically committed on success
    or rolled back on error.

    Args:
        query: SQL write query to execute (INSERT, UPDATE, DELETE)
        params: Optional list of parameters for parameterized queries (prevents SQL injection)
        database: Optional database name to use for this query (uses current if not specified)

    Returns:
        Dictionary containing execution result with affected_rows and last_insert_id
    """
    logger.info("✏️ Executing write query")
    logger.debug(f"Query: {query}")

    ALLOWED_PREFIXES = ("INSERT", "UPDATE", "DELETE", "REPLACE")

    query_stripped = query.strip()
    query_upper = query_stripped.upper()

    if not any(query_upper.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        return {
            "success": False,
            "error": f"Only {', '.join(ALLOWED_PREFIXES)} queries are allowed. Use query_data for SELECT.",
            "query": query,
            "database": database or "current",
            "affected_rows": 0,
            "last_insert_id": None,
        }

    try:
        async with get_context(database) as ctx:
            async with ctx.pool.acquire() as conn:
                if database:
                    async with conn.cursor() as cursor:
                        await cursor.execute(f"USE `{database}`")

                # Disable autocommit to use explicit transaction
                await conn.begin()
                try:
                    async with conn.cursor() as cursor:
                        if params:
                            await cursor.execute(query_stripped, params)
                        else:
                            await cursor.execute(query_stripped)

                        affected_rows = cursor.rowcount
                        last_insert_id = cursor.lastrowid

                    await conn.commit()

                    # Resolve current database name for response
                    async with conn.cursor() as db_cursor:
                        await db_cursor.execute("SELECT DATABASE()")
                        current_db_row = await db_cursor.fetchone()
                        current_database = current_db_row[0] if current_db_row else database or "unknown"

                    logger.info(f"✅ Write query executed successfully. Affected rows: {affected_rows}")
                    return {
                        "success": True,
                        "message": "Query executed successfully",
                        "query": query_stripped,
                        "database": current_database,
                        "affected_rows": affected_rows,
                        "last_insert_id": last_insert_id if last_insert_id else None,
                    }

                except Exception:
                    await conn.rollback()
                    raise

    except Exception as e:
        error_msg = f"Write query failed: {type(e).__name__}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "query": query,
            "database": database or "current",
            "affected_rows": 0,
            "last_insert_id": None,
        }


@mcp.tool()
async def list_databases() -> Dict[str, Any]:
    """
    List all available databases on the MySQL server.
    
    Returns:
        List of database names
    """
    try:
        logger.info("📋 Listing available databases...")
        
        async with get_context() as ctx:
            async with ctx.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SHOW DATABASES")
                    rows = await cursor.fetchall()
                    
                    # Extract database names, excluding system databases
                    databases = []
                    system_dbs = {'information_schema', 'performance_schema', 'mysql', 'sys'}
                    
                    for row in rows:
                        db_name = row[0]
                        if db_name not in system_dbs:
                            databases.append(db_name)
                    
                    return {
                        "status": "success",
                        "message": "Databases retrieved successfully",
                        "databases": databases,
                        "count": len(databases)
                    }
                    
    except Exception as e:
        error_msg = f"Failed to list databases: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "databases": [],
            "count": 0
        }

@mcp.tool()
async def list_tables(database: Optional[str] = None) -> Dict[str, Any]:
    """
    List all available tables in the specified database.
    
    Args:
        database: Database name to list tables from (required if no default database set)
        
    Returns:
        List of tables with basic information
    """
    try:
        # Determine target database
        if database:
            target_db = database
        elif db_name:
            target_db = db_name
        else:
            return {
                "status": "error",
                "message": "No database specified and no default database configured. Use 'database' parameter or set DB_NAME in environment.",
                "database": None,
                "tables": [],
                "count": 0
            }
            
        logger.info(f"📋 Listing tables in database: {target_db}")
        
        async with get_context(database) as ctx:
            async with ctx.pool.acquire() as conn:
                # Switch to specific database if provided
                if database:
                    async with conn.cursor() as cursor:
                        await cursor.execute(f"USE `{database}`")
                elif db_name:
                    # Ensure we're using the correct database
                    async with conn.cursor() as cursor:
                        await cursor.execute(f"USE `{db_name}`")
                
                async with conn.cursor() as cursor:
                    await cursor.execute("SHOW TABLES")
                    rows = await cursor.fetchall()
                    
                    # Extract table names
                    tables = [row[0] for row in rows]
                    
                    return {
                        "status": "success",
                        "message": f"Tables retrieved successfully from {target_db}",
                        "database": target_db,
                        "tables": tables,
                        "count": len(tables)
                    }
                    
    except Exception as e:
        error_msg = f"Failed to list tables: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "database": database or db_name or "unknown",
            "tables": [],
            "count": 0
        }

@mcp.tool()
async def get_schema(table_name: str, database: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed schema information for a specific table.
    
    Args:
        table_name: Name of the table to describe
        database: Database name containing the table (required if no default database set)
        
    Returns:
        Detailed schema information including columns and comments
    """
    try:
        # Determine target database
        if database:
            target_db = database
        elif db_name:
            target_db = db_name
        else:
            return {
                "status": "error",
                "message": "No database specified and no default database configured. Use 'database' parameter or set DB_NAME in environment.",
                "table": table_name,
                "database": None,
                "columns": [],
                "count": 0
            }
            
        logger.info(f"🔍 Getting schema for table: {table_name} in database: {target_db}")
        
        async with get_context(database) as ctx:
            async with ctx.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    # Get columns and column comments
                    await cursor.execute(
                        "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA, COLUMN_COMMENT "
                        "FROM information_schema.columns WHERE table_schema=%s AND table_name=%s",
                        (target_db, table_name)
                    )
                    columns = await cursor.fetchall()
                    
                    if not columns:
                        return {
                            "status": "error",
                            "message": f"Table '{table_name}' not found in database '{target_db}'",
                            "table": table_name,
                            "database": target_db,
                            "columns": [],
                            "count": 0
                        }
                    
                    schema_info = []
                    for col in columns:
                        schema_info.append({
                            "field": col["COLUMN_NAME"],
                            "type": col["COLUMN_TYPE"],
                            "null": col["IS_NULLABLE"],
                            "key": col["COLUMN_KEY"],
                            "default": col["COLUMN_DEFAULT"],
                            "extra": col["EXTRA"],
                            "comment": col["COLUMN_COMMENT"]
                        })
                    
                    # Get table comment
                    await cursor.execute(
                        "SELECT TABLE_COMMENT FROM information_schema.tables WHERE table_schema=%s AND table_name=%s",
                        (target_db, table_name)
                    )
                    table_row = await cursor.fetchone()
                    table_comment = table_row["TABLE_COMMENT"] if table_row else ""
                    
                    return {
                        "status": "success",
                        "message": f"Schema for {table_name} retrieved successfully",
                        "table": table_name,
                        "database": target_db,
                        "table_comment": table_comment,
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
            "database": database or db_name or "unknown",
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
        return f"❌ Failed to get tables: {str(e)}"# === MAIN EXECUTION ===
if __name__ == "__main__":
    import argparse
    import signal
    
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
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("� Received shutdown signal, cleaning up...")
        asyncio.create_task(cleanup_global_context())
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("�🚀 Starting minimalist MySQL MCP server...")
    logger.info(f"📊 Transport: {args.transport}")
    logger.info(f"🔌 Port: {args.port}")
    
    try:
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
    except KeyboardInterrupt:
        logger.info("🛑 Server interrupted by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
    finally:
        # Cleanup on exit
        logger.info("🧹 Performing final cleanup...")
        try:
            asyncio.run(cleanup_global_context())
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
        logger.info("👋 MySQL MCP Server shutdown complete")
