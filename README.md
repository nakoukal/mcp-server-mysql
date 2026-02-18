# MySQL MCP Server

[![MCP](https://img.shields.io/badge/Model%20Context%20Protocol-MCP-blue)](https://modelcontextprotocol.io/)
[![FastMCP](https://img.shields.io/badge/FastMCP-latest-green)](https://github.com/jlowin/fastmcp)
[![MySQL](https://img.shields.io/badge/MySQL-Compatible-orange)](https://mysql.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)

> MySQL MCP Server poskytující čtecí i zápisové operace do databáze skrze Model Context Protocol.

## O projektu

Server je postaven na FastMCP a aiomysql s connection poolingem. Podporuje více transportů (stdio, SSE, HTTP) a umožňuje pracovat s více databázemi v rámci jednoho připojení.

## MCP nástroje

| Nástroj | Popis | Typ operace |
|---------|-------|-------------|
| `list_databases` | Seznam všech databází na serveru | Metadata |
| `change_database` | Přepnutí aktivní databáze | Konfigurace |
| `query_data` | Spuštění SELECT dotazů s automatickým limitem | Čtení |
| `execute_write` | Spuštění INSERT / UPDATE / DELETE v transakci | Zápis |
| `list_tables` | Seznam tabulek v databázi | Metadata |
| `get_schema` | Detailní schéma tabulky včetně komentářů | Metadata |

### Parametry nástrojů

```
query_data(query, limit=100, database=None)
execute_write(query, params=None, database=None)
list_tables(database=None)
get_schema(table_name, database=None)
```

Parametr `database` je volitelný u všech nástrojů — umožňuje dotaz na jinou než aktivní databázi bez změny globálního kontextu.

## MCP Resources

| Resource | Popis |
|----------|-------|
| `mysql://status` | Health check databázového serveru |
| `mysql://tables` | Rychlý výpis tabulek jako text |

## Rychlý start (lokálně)

### 1. Klonování

```bash
git clone <repo-url> mysql-mcp-server
cd mysql-mcp-server
```

### 2. Virtuální prostředí

```bash
python3 -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\Activate.ps1       # Windows (PowerShell)
```

### 3. Instalace závislostí

```bash
pip install -r requirements.txt
```

### 4. Konfigurace

Vytvoř `.env` soubor podle vzoru:

```bash
cp .env.example .env
```

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database   # volitelné — lze změnit za běhu přes change_database
DEBUG_MODE=false
```

### 5. Spuštění

```bash
# STDIO (výchozí — pro Claude Desktop a Claude Code)
./start_server.sh

# SSE (pro Langflow a webové aplikace)
./start_server.sh --transport sse --port 8000

# HTTP
./start_server.sh --transport streamable-http --port 8000
```

Nebo přímo Pythonem:

```bash
python mysql_server.py --transport stdio
python mysql_server.py --transport sse --port 8000
python mysql_server.py --transport streamable-http --port 8000
```

## Konfigurace pro Claude Desktop

Soubor `claude_desktop_config.json` přidej do:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mysql": {
      "command": "/abs/cesta/k/venv/bin/python",
      "args": ["/abs/cesta/k/mysql_server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "your_user",
        "DB_PASSWORD": "your_password",
        "DB_NAME": "your_database",
        "DEBUG_MODE": "false"
      }
    }
  }
}
```

Nebo s `.env` souborem (doporučeno pro bezpečnost):

```json
{
  "mcpServers": {
    "mysql": {
      "command": "/abs/cesta/k/venv/bin/python",
      "args": ["/abs/cesta/k/mysql_server.py"],
      "cwd": "/abs/cesta/k/mysql-mcp-server"
    }
  }
}
```

## Příklady použití

### Čtení dat

```python
# Seznam tabulek
await mcp_client.call_tool("list_tables")

# Schema tabulky
await mcp_client.call_tool("get_schema", {"table_name": "users"})

# SELECT dotaz
await mcp_client.call_tool("query_data", {
    "query": "SELECT * FROM users WHERE active = 1",
    "limit": 50
})

# Dotaz na jinou databázi bez změny globálního kontextu
await mcp_client.call_tool("query_data", {
    "query": "SELECT COUNT(*) FROM logs",
    "database": "analytics_db"
})
```

### Zápis dat

```python
# INSERT — přímý dotaz
await mcp_client.call_tool("execute_write", {
    "query": "INSERT INTO users (name, email) VALUES ('Jan', 'jan@example.com')"
})

# INSERT — parametrizovaný (doporučeno, ochrana před SQL injection)
await mcp_client.call_tool("execute_write", {
    "query": "INSERT INTO users (name, email) VALUES (%s, %s)",
    "params": ["Jan", "jan@example.com"]
})

# UPDATE
await mcp_client.call_tool("execute_write", {
    "query": "UPDATE users SET active = 0 WHERE last_login < %s",
    "params": ["2024-01-01"]
})

# DELETE
await mcp_client.call_tool("execute_write", {
    "query": "DELETE FROM sessions WHERE expires_at < NOW()"
})
```

Odpověď `execute_write`:

```json
{
  "success": true,
  "message": "Query executed successfully",
  "query": "INSERT INTO users ...",
  "database": "my_db",
  "affected_rows": 1,
  "last_insert_id": 42
}
```

### Práce s více databázemi

```python
# Trvalá změna aktivní databáze
await mcp_client.call_tool("change_database", {"database_name": "production_db"})

# Jednorázový dotaz na jinou databázi
await mcp_client.call_tool("list_tables", {"database": "analytics_db"})
```

## Bezpečnost

### query_data (SELECT)
- Povoleny pouze `SELECT` dotazy
- Automatický `LIMIT` pokud chybí
- SQL injection ochrana přes aiomysql

### execute_write (INSERT / UPDATE / DELETE / REPLACE)
- Povoleny pouze DML operace — DDL (`CREATE`, `DROP`, `ALTER`) jsou blokovány
- Každý dotaz běží v explicitní transakci; při chybě se automaticky provede `ROLLBACK`
- Podporuje parametrizované dotazy (`params`) pro bezpečné předávání hodnot

### Obecně
- Connection pooling s omezeným počtem spojení
- Konfigurace přes `.env` (neverzovaný soubor)
- Logy na stderr, žádná citlivá data v chybových zprávách

## Testování

```bash
# Aktivuj venv
source venv/bin/activate

# Testy připojení a základních operací
python tests/test_live_mysql.py

# Test přepínání databází
python tests/test_database_switching.py

# Test bez výchozí databáze
python tests/test_no_default_database.py

# Test STDIO transportu
python tests/test_stdio_transport.py
```

## Docker

### Build a spuštění

```bash
docker build -t mysql-mcp-server .

docker run -d \
  --name mysql-mcp-server \
  --network mynet \
  -p 8000:8000 \
  --env-file .env \
  mysql-mcp-server
```

### Docker Compose

```yaml
services:
  mysql-mcp-server:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    networks:
      - mynet
    restart: unless-stopped

networks:
  mynet:
    external: true
```

### Správa kontejneru

```bash
docker logs -f mysql-mcp-server
docker restart mysql-mcp-server
docker exec -it mysql-mcp-server bash
```

## Langflow integrace

1. Spusť server v SSE módu:
   ```bash
   python mysql_server.py --transport sse --port 8000
   ```

2. V Langflow MCP Connection komponentě:
   - **SSE URL**: `http://<HOST_IP>:8000/sse`
   - **Transport**: `sse`

3. Zjištění IP adresy hosta:
   ```bash
   hostname -I | awk '{print $1}'
   ```

## Struktura projektu

```
mysql-mcp-server/
├── mysql_server.py          # Hlavní MCP server
├── start_server.sh          # Startovací skript
├── requirements.txt         # Python závislosti
├── pyproject.toml
├── Dockerfile
├── .env.example             # Vzorová konfigurace
├── claude_desktop_config.json  # Vzorová konfigurace pro Claude Desktop
├── tests/
│   ├── test_live_mysql.py
│   ├── test_database_switching.py
│   ├── test_no_default_database.py
│   ├── test_stdio_transport.py
│   └── ...
└── CLAUDE_SETUP.md          # Průvodce nastavením pro Claude Desktop / Claude Code
```
