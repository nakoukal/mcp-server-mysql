# Nastavení MySQL MCP Server pro Claude Desktop / Claude Code

## Konfigurace pro Claude Desktop

Otevři konfigurační soubor Claude Desktop:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### Varianta A — přihlašovací údaje v konfiguraci

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

### Varianta B — přihlašovací údaje v `.env` souboru (doporučeno)

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

Server automaticky načte `.env` z `cwd`.

### Windows (PowerShell / příkazový řádek)

```json
{
  "mcpServers": {
    "mysql": {
      "command": "C:\\cesta\\k\\.venv\\Scripts\\python.exe",
      "args": ["C:\\cesta\\k\\mysql_server.py"],
      "cwd": "C:\\cesta\\k\\mysql-mcp-server"
    }
  }
}
```

## Konfigurace pro Claude Code (CLI)

```bash
# Přidání serveru
claude mcp add mysql \
  -e DB_HOST=localhost \
  -e DB_PORT=3306 \
  -e DB_USER=your_user \
  -e DB_PASSWORD=your_password \
  -e DB_NAME=your_database \
  -e DEBUG_MODE=false \
  -- /abs/cesta/k/venv/bin/python /abs/cesta/k/mysql_server.py

# Ověření
claude mcp list
claude mcp get mysql
```

## Dostupné nástroje

| Nástroj | Popis |
|---------|-------|
| `list_databases` | Seznam všech databází na serveru |
| `change_database` | Přepnutí aktivní databáze |
| `query_data` | Spuštění SELECT dotazů |
| `execute_write` | Spuštění INSERT / UPDATE / DELETE v transakci |
| `list_tables` | Seznam tabulek v databázi |
| `get_schema` | Schéma tabulky |

## Příklady dotazů v Claude

```
"Zobraz mi všechny databáze"
"Přepni na databázi 'customers'"
"Vypiš všechny tabulky"
"Ukaž schéma tabulky 'orders'"
"Spusť dotaz: SELECT * FROM orders WHERE status = 'pending'"
"Vlož nový záznam do tabulky products"
"Aktualizuj stav objednávky č. 123 na 'shipped'"
```

## Testování

```bash
# Test STDIO transportu (ověří, že server komunikuje správně)
python tests/test_stdio_transport.py

# Přímé spuštění (výstup do stderr)
python mysql_server.py
# Očekáváš: 🚀 Starting minimalist MySQL MCP server...

# Test připojení k databázi
python test_connection.py
```

## Řešení problémů

### Server se nespustí

```bash
# Ověř cestu k Pythonu
which python   # Linux/macOS
where python   # Windows

# Ověř závislosti
pip list | grep -i "fastmcp\|aiomysql"

# Reinstalace
pip install -r requirements.txt
```

### Claude nevidí nástroje

1. Zkontroluj cestu k `mysql_server.py` v konfiguraci
2. Restartuj Claude Desktop
3. Zkontroluj logy: **Help → View Logs**

### Chyba připojení k databázi

```bash
python test_connection.py
mysql -h localhost -u your_user -p
```
