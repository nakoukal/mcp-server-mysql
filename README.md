# 🐬 MySQL MCP Server

[![MCP](https://img.shields.io/badge/Model%20Context%20Protocol-MCP-blue)](https://modelcontextprotocol.io/)
[![FastMCP](https://img.shields.io/badge/FastMCP-v0.2.0-green)](https://github.com/jlowin/fastmcp)
[![MySQL](https://img.shields.io/badge/MySQL-Compatible-orange)](https://mysql.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)

> **Production-ready MySQL MCP Server** providing safe database operations through Model Context Protocol.

## 🎯 About

This MCP server provides secure access to MySQL databases through the Model Context Protocol. Built with FastMCP and following security best practices, it offers read-only database operations with comprehensive error handling and logging.

### ✅ **Key Features:**
- 🔒 **Security First** - Only SELECT queries allowed, SQL injection protection
- 🚀 **High Performance** - Connection pooling with aiomysql
- 📊 **Rich Metadata** - Table schemas, column details, structured responses
- 🔍 **Smart Queries** - Automatic LIMIT injection, query validation
- 🐳 **Docker Ready** - Container builds and deployment
- 📈 **Multi-Transport** - stdio, SSE, and HTTP transports
- 🛡️ **Error Handling** - Structured error responses with logging

## 🛠️ MCP Tools

| Tool | Description | Safety Level |
|------|-------------|--------------|
| `list_databases` | List all available databases on the server | 🔒 Metadata |
| `change_database` | Change active database for all subsequent operations | 🔧 Configuration |
| `query_data` | Execute SELECT queries with automatic limits | 🔒 Read-only |
| `list_tables` | List all available database tables | 🔒 Metadata |
| `get_schema` | Get detailed table schema information | 🔒 Metadata |

### 🎯 Database Switching Features

#### **Two Approaches:**

1. **Global Database Change (Persistent)**
   ```python
   # Change active database for all subsequent operations
   await change_database("production_db")
   await list_tables()  # Lists tables from production_db
   await query_data("SELECT * FROM users LIMIT 5")  # Queries production_db
   ```

2. **Per-Query Database Selection (Temporary)**
   ```python
   # Specify database for individual operations without changing global context
   await list_tables(database="analytics_db")  # Temporary switch to analytics_db
   await query_data("SELECT COUNT(*) FROM logs", database="analytics_db")  # Query analytics_db
   await list_tables()  # Still uses original database
   ```

#### **Enhanced Tool Parameters:**
- `query_data(query: str, limit: int = 100, database: Optional[str] = None)`
- `list_tables(database: Optional[str] = None)`
- `get_schema(table_name: str, database: Optional[str] = None)`

## 📋 MCP Resources

| Resource | Description |
|----------|-------------|
| `mysql://status` | Database server health check |
| `mysql://tables` | Quick tables list as text |

## 🚀 Quick Start (lokálně bez Dockeru)

### 1. **Klonování repozitáře**

```bash
git clone <repo-url> mysql-mcp-server
cd mysql-mcp-server
```

### 2. **Vytvoření a aktivace virtuálního prostředí**

```bash
# Vytvoř virtuální prostředí (složka venv/ ve stejném adresáři)
python3 -m venv venv

# Aktivace na Linux/macOS
source venv/bin/activate

# Aktivace na Windows (PowerShell)
# venv\Scripts\Activate.ps1

# Ověření – měl by se zobrazit python z venv
which python
```

### 3. **Instalace závislostí**

```bash
# Instalace všech závislostí ze souboru requirements.txt
pip install -r requirements.txt
```

### 4. **Konfigurace**

Vytvoř soubor `.env` v kořenu projektu:
```bash
# MySQL MCP Server Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
DEBUG_MODE=false
```

### 5. **Spuštění serveru**

#### **Možnost A: Pomocí startovacího skriptu (doporučeno)**
```bash
# STDIO transport (výchozí – pro MCP klienty jako Claude Desktop)
./start_server.sh

# SSE transport pro webové aplikace a Langflow
./start_server.sh --transport sse --port 8000

# HTTP transport pro REST API
./start_server.sh --transport streamable-http --port 8000

# Nápověda
./start_server.sh --help
```

Startovací skript automaticky:
- ✅ Zkontroluje existenci virtuálního prostředí (`venv/`)
- ✅ Ověří konfigurační soubory
- ✅ Aktivuje virtuální prostředí
- ✅ Vypíše srozumitelné chybové zprávy
- ✅ Ošetří graceful shutdown (Ctrl+C)

#### **Možnost B: Přímé spuštění Pythonem**
```bash
# Nejprve aktivuj venv (pokud ještě není aktivní)
source venv/bin/activate

# Nápověda
python mysql_server.py --help

# STDIO transport (pro MCP klienty jako Claude Desktop)
python mysql_server.py

# SSE transport (pro Langflow, webové aplikace)
python mysql_server.py --transport sse --port 8000

# HTTP transport (pro REST API)
python mysql_server.py --transport streamable-http --port 8000
```

> **Poznámka:** Virtuální prostředí deaktivuješ příkazem `deactivate`.

### 4. **Langflow Integration**

For Langflow running in Docker container:

1. **Start server:**
   ```bash
   python3 mysql_server.py --transport sse --port 8000
   ```

2. **In Langflow MCP Connection component:**
   - **SSE URL**: `http://HOST_IP:8000/sse` (replace HOST_IP with your server IP)
   - **Transport**: `sse`

3. **Find your host IP:**
   ```bash
   hostname -I | awk '{print $1}'
   ```

## 🔧 Command Line Options

```bash
usage: mysql_server.py [-h] [--transport {stdio,sse,streamable-http}] [--port PORT]

MySQL MCP Server - Secure database operations via Model Context Protocol

options:
  -h, --help            show this help message and exit
  --transport {stdio,sse,streamable-http}
                        Transport mode (default: stdio)
  --port PORT           Port for SSE/HTTP transports (default: 8000)
```

### **Transport Types:**

- **`stdio`** (default): For desktop MCP clients (Claude Desktop, etc.)
- **`sse`**: For web applications and Langflow (Server-Sent Events)
- **`streamable-http`**: For REST API access and HTTP clients

## 💡 Usage Examples

### **Basic Queries**
```python
# List all tables
result = await mcp_client.call_tool("list_tables")
print(f"Found {result['count']} tables")

# Get table schema
schema = await mcp_client.call_tool("get_schema", {"table_name": "users"})
for col in schema['columns']:
    print(f"{col['field']}: {col['type']}")

# Execute query
data = await mcp_client.call_tool("query_data", {
    "query": "SELECT * FROM users WHERE active = 1",
    "limit": 50
})
print(f"Found {data['count']} active users")
```

### **Health Check**
```python
# Check database status
status = await mcp_client.get_resource("mysql://status")
print(status)  # ✅ MySQL server is healthy and ready
```

## 🧪 Testing

Run the included test suite:

```bash
# Run all tests
python3 tests/test_live_mysql.py

# Test database switching functionality
python3 tests/test_database_switching.py

# Test without default database configuration
python3 tests/test_no_default_database.py

# Expected output:
# 🎯 Tests passed: 6/6
# 🎉 All tests passed! MySQL MCP Server is fully functional.
```

**Test coverage:**
- ✅ Database connection and health checks
- ✅ List databases functionality
- ✅ Global database switching (`change_database`)
- ✅ Per-query database selection (all tools with `database` parameter)
- ✅ List tables functionality (current and specific databases)
- ✅ Schema retrieval (current and specific databases)
- ✅ Query execution with database switching
- ✅ Security features (blocks INSERT/UPDATE/DELETE)
- ✅ SHOW commands with proper result limiting
- ✅ MCP resources (status, tables)
- ✅ Error handling for missing default database
- ✅ Graceful cleanup and connection management

## 🔒 Security Features

### **Query Safety**
- Only `SELECT` statements allowed
- Automatic `LIMIT` injection if missing
- SQL injection protection through parameterized queries
- Input validation and sanitization

### **Access Control**
- Read-only database operations
- Connection pooling with limits
- Environment-based configuration
- No DDL operations allowed

### **Error Handling**
- Structured error responses
- Comprehensive logging with emojis
- No sensitive data in error messages
- Connection timeout management

## 📊 Response Format

All tools return structured responses:

```json
{
  "status": "success|error",
  "message": "Human readable message", 
  "data": "Tool-specific data",
  "count": "Number of results"
}
```

## 🐳 Docker Deployment

### Building the Docker Image

```bash
# Build the Docker image
docker build -t mysql-mcp-server .
```

### Running with Docker

#### Option 1: Using Environment File (Recommended)

Create a `.env` file with your database configuration:
```env
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database  # Optional - can be changed via tools
```

Run the container:
```bash
# Run with environment file
docker run -d \
  --name mysql-mcp-server-fssx0132x \
  --network mynet \
  -p 8087:8000 \
  --env-file .env \
  mysql-mcp-server
```

#### Option 2: Using Environment Variables

```bash
# Run with inline environment variables
docker run -d \
  --name mysql-mcp-server \
  --network mynet \
  -p 8087:8000 \
  -e DB_HOST=your-mysql-host \
  -e DB_PORT=3306 \
  -e DB_USER=your-username \
  -e DB_PASSWORD=your-password \
  -e DB_NAME=your-database \
  mysql-mcp-server
```

#### Option 3: Database-Specific Deployment

For **IP Management** database:
```bash
docker run -d \
  --name mysql-mcp-ipmanagement \
  --network mynet \
  -p 8087:8000 \
  -e DB_NAME=ipmanagement \
  --env-file .env \
  mysql-mcp-server
```

For **DWH N8N** database:
```bash
docker run -d \
  --name mysql-mcp-dwh-n8n \
  --network mynet \
  -p 8088:8000 \
  -e DB_NAME=dwh-n8n \
  --env-file .env \
  mysql-mcp-server
```

### Docker Management Commands

```bash
# View logs
docker logs mysql-mcp-server-fssx0132x

# Stop container
docker stop mysql-mcp-server-fssx0132x

# Remove container
docker rm mysql-mcp-server-fssx0132x

# Restart container
docker restart mysql-mcp-server-fssx0132x

# Execute commands inside container
docker exec -it mysql-mcp-server-fssx0132x bash
```

### Health Check

Verify the server is running:
```bash
# Check if server responds
curl http://localhost:8087/health

# Or check container status
docker ps | grep mysql-mcp-server
```

### Network Configuration

The example uses a custom Docker network (`mynet`). Create it if it doesn't exist:
```bash
# Create custom network
docker network create mynet

# List networks
docker network ls

# Inspect network
docker network inspect mynet
```

### Production Considerations

For production deployment:

1. **Use Docker Compose** for easier management:
```yaml
# docker compose.yml
version: '3.8'
services:
  mysql-mcp-server:
    build: .
    container_name: mysql-mcp-server-fssx0132x
    ports:
      - "8087:8000"
    env_file:
      - .env
    networks:
      - mynet
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  mynet:
    external: true
```

2. **Environment Variables for Security**:
   - Store sensitive data in `.env` file
   - Don't include `.env` in version control
   - Use Docker secrets for production

3. **Resource Limits**:
```bash
docker run -d \
  --name mysql-mcp-server-fssx0132x \
  --network mynet \
  -p 8087:8000 \
  --memory="512m" \
  --cpus="0.5" \
  --env-file .env \
  mysql-mcp-server
```

### Troubleshooting

Common issues and solutions:

```bash
# Check container logs for errors
docker logs -f mysql-mcp-server-fssx0132x

# Test database connectivity from container
docker exec mysql-mcp-server-fssx0132x python -c "
import mysql.connector
import os
try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# Check if port is accessible
telnet localhost 8087
```

## 🔗 MCP Client Connection

Once the Docker container is running, connect your MCP client to:
- **URL**: `http://localhost:8087`
- **Transport**: Streamable HTTP (MCP 2024-11-05+)

Example client configuration:
```json
{
  "servers": {
    "mysql-server": {
      "url": "http://localhost:8087",
      "transport": "streamable-http"
    }
  }
}
```

---

**Built with ❤️ for the MCP community** | **Production-ready MySQL database access**
