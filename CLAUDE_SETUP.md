# 🔧 Nastavení MySQL MCP Server pro Claude Desktop

## ✅ STDIO Transport - Ověřeno

Váš `mysql_server.py` nyní správně podporuje STDIO transport:
- ✅ Čte příkazy ze **stdin**
- ✅ Píše odpovědi na **stdout**  
- ✅ Loguje na **stderr**

## 📋 Konfigurace pro Claude Desktop

### 1. Najděte konfigurační soubor Claude Desktop

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Přidejte MySQL MCP Server

Otevřete `claude_desktop_config.json` a přidejte:

```json
{
  "mcpServers": {
    "mysql": {
      "command": "python",
      "args": ["C:\\cesta\\k\\mysql_server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "root",
        "DB_PASSWORD": "your_password",
        "DB_NAME": "your_database",
        "DEBUG_MODE": "false"
      }
    }
  }
}
```

### 3. S Virtual Environment (Doporučeno)

Pokud používáte virtual environment:

```json
{
  "mcpServers": {
    "mysql": {
      "command": "C:\\cesta\\k\\.venv\\Scripts\\python.exe",
      "args": ["C:\\cesta\\k\\mysql_server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "root",
        "DB_PASSWORD": "your_password",
        "DB_NAME": "your_database"
      }
    }
  }
}
```

### 4. Použití .env souboru (Bezpečnější)

Místo zadávání hesel v konfiguraci můžete použít .env soubor:

```json
{
  "mcpServers": {
    "mysql": {
      "command": "C:\\cesta\\k\\.venv\\Scripts\\python.exe",
      "args": ["C:\\cesta\\k\\mysql_server.py"],
      "cwd": "C:\\cesta\\k"
    }
  }
}
```

Server automaticky načte `.env` soubor z pracovního adresáře.

## 🧪 Testování

### Test 1: Ověření STDIO transportu

```bash
python test_stdio_transport.py
```

### Test 2: Manuální test

```bash
# Spusťte server
python mysql_server.py

# Server by měl vypsat:
# 🚀 Starting minimalist MySQL MCP server...
# 📊 Transport: stdio
# 📝 Starting STDIO transport...
```

### Test 3: V Claude Desktop

Po restartu Claude Desktop byste měli vidět:
1. MySQL server v seznamu MCP serverů
2. Dostupné nástroje: `list_databases`, `change_database`, `query_data`, `list_tables`, `get_schema`

## 🔍 Řešení problémů

### Server se nespustí

```bash
# Zkontrolujte Python cestu
where python

# Zkontrolujte závislosti
pip list | findstr -i "fastmcp aiomysql"

# Zkontrolujte .env soubor
type .env
```

### Claude Desktop nevidí server

1. Zkontrolujte cestu k `mysql_server.py` v konfiguraci
2. Restartujte Claude Desktop
3. Zkontrolujte logy Claude Desktop (Help → View Logs)

### Chyby připojení k databázi

```bash
# Test připojení
python test_connection.py

# Zkontrolujte MySQL server
mysql -h localhost -u root -p
```

## 📊 Dostupné MCP nástroje

Po úspěšném připojení máte k dispozici:

| Nástroj | Popis |
|---------|-------|
| `list_databases` | Seznam všech databází |
| `change_database` | Změna aktivní databáze |
| `query_data` | Spuštění SELECT dotazů |
| `list_tables` | Seznam tabulek |
| `get_schema` | Schéma tabulky |

## 🔒 Bezpečnost

- ✅ Pouze SELECT dotazy povoleny
- ✅ Automatické LIMIT pro ochranu
- ✅ SQL injection ochrana
- ✅ Connection pooling
- ✅ Strukturované error handling

## 📝 Příklady použití v Claude

```
"Zobraz mi všechny databáze"
"Přepni na databázi 'customers'"
"Vypiš všechny tabulky"
"Ukaž schéma tabulky 'users'"
"Spusť dotaz: SELECT * FROM orders WHERE status = 'pending'"
```

---

**✅ Server je připraven pro použití v Claude Desktop!**
