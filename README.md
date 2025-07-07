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
| `query_data` | Execute SELECT queries with automatic limits | 🔒 Read-only |
| `list_tables` | List all available database tables | 🔒 Metadata |
| `get_schema` | Get detailed table schema information | 🔒 Metadata |

## 📋 MCP Resources

| Resource | Description |
|----------|-------------|
| `mysql://status` | Database server health check |
| `mysql://tables` | Quick tables list as text |

## 🚀 Quick Start

### 1. **Installation**

```bash
# Clone or create project directory
mkdir mysql-mcp-server && cd mysql-mcp-server

# Install dependencies
pip install fastmcp aiomysql python-dotenv pytest
```

### 2. **Configuration**

Create `.env` file:
```bash
# MySQL MCP Server Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
DEBUG_MODE=false
```

### 3. **Usage**

```bash
# Help
python3 mysql_server.py --help

# STDIO transport (for MCP clients like Claude Desktop)
python3 mysql_server.py

# SSE transport (for Langflow, web applications)
python3 mysql_server.py --transport sse --port 8000

# HTTP transport (for REST API access)
python3 mysql_server.py --transport streamable-http --port 8000
```

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
python3 test_live_mysql.py

# Expected output:
# 🎯 Tests passed: 6/6
# 🎉 All tests passed! MySQL MCP Server is fully functional.
```

**Test coverage:**
- ✅ Database connection
- ✅ List tables functionality
- ✅ Schema retrieval
- ✅ Query execution
- ✅ Security features (blocks INSERT/UPDATE/DELETE)
- ✅ MCP resources

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

### **Build and Run**

```bash
# Build image
docker build -t mysql-mcp-server:latest .

# Run with SSE transport
docker run -d --name mysql-mcp-server \
  -p 8000:8000 \
  --env-file .env \
  mysql-mcp-server:latest \
  python3 mysql_server.py --transport sse --port 8000
```

### **Docker Compose**

```yaml
version: '3.8'
services:
  mysql-mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=mysql-db
      - DB_USER=root
      - DB_PASSWORD=password
      - DB_NAME=myapp
    command: python3 mysql_server.py --transport sse --port 8000
    depends_on:
      - mysql-db
      
  mysql-db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: myapp
```

## 🔧 Configuration

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | MySQL server hostname |
| `DB_PORT` | `3306` | MySQL server port |
| `DB_USER` | `root` | Database username |
| `DB_PASSWORD` | `` | Database password |
| `DB_NAME` | `mysql` | Database name |
| `DEBUG_MODE` | `false` | Enable debug logging |

### **Connection Pool Settings**

- **Min Size**: 1 connection
- **Max Size**: 10 connections  
- **Charset**: utf8mb4
- **Autocommit**: Enabled

## 🚨 Troubleshooting

### **Common Issues**

**Connection Failed**
```bash
# Check MySQL service
systemctl status mysql

# Test connection manually
mysql -h localhost -u root -p
```

**Permission Denied**
```bash
# Grant SELECT permissions
GRANT SELECT ON database.* TO 'username'@'%';
FLUSH PRIVILEGES;
```

**Langflow Docker Connection**
```bash
# Use host IP instead of localhost
# Find host IP: hostname -I | awk '{print $1}'
# Use: http://HOST_IP:8000/sse
```

## 📈 Performance

- **Connection Pooling**: 1-10 concurrent connections
- **Query Limits**: Automatic LIMIT injection (default: 100 rows)
- **Timeouts**: Configurable connection timeouts
- **Memory Efficient**: Streaming results for large datasets

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: This README and inline code comments
- **Issues**: Report bugs via GitHub Issues
- **MCP Protocol**: Learn more at [modelcontextprotocol.io](https://modelcontextprotocol.io/)

---

**Built with ❤️ for the MCP community** | **Production-ready MySQL database access**
