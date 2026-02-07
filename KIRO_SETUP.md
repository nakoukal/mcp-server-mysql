# 🚀 MySQL MCP Server - Nastavení pro Kiro/Claude CLI

## ✅ Server je nakonfigurovaný!

Váš MySQL MCP server je úspěšně přidaný do Claude CLI.

## 📋 Aktuální konfigurace

```
Server: mysql
Status: ✓ Connected
Type: stdio
Python: P:\00_IT_Applications\05_PYTHON\mcp-server-mysql\.venv\Scripts\python.exe
Script: P:\00_IT_Applications\05_PYTHON\mcp-server-mysql\mysql_server.py

Database:
  Host: fssx0132x.fs.cz.int.vitesco.com
  Port: 3309
  User: notifier
  Database: ipmanagement
```

## 🎯 Dostupné příkazy

### Správa MCP serverů

```bash
# Seznam všech MCP serverů
claude mcp list

# Detail konkrétního serveru
claude mcp get mysql

# Odstranění serveru
claude mcp remove mysql -s local

# Nápověda
claude mcp --help
```

### Použití v konverzaci

V Claude CLI můžete nyní používat příkaz `/mcp`:

```bash
# Zobrazit dostupné MCP nástroje
/mcp

# Použít konkrétní nástroj
/mcp list_databases
/mcp list_tables
/mcp query_data "SELECT * FROM users LIMIT 10"
```

## 🛠️ Dostupné MCP nástroje

| Nástroj | Popis | Příklad |
|---------|-------|---------|
| `list_databases` | Seznam všech databází | `/mcp list_databases` |
| `change_database` | Změna aktivní databáze | `/mcp change_database "production"` |
| `query_data` | Spuštění SELECT dotazu | `/mcp query_data "SELECT * FROM users LIMIT 5"` |
| `list_tables` | Seznam tabulek | `/mcp list_tables` |
| `get_schema` | Schéma tabulky | `/mcp get_schema "users"` |

## 📊 Příklady použití

### 1. Základní dotazy

```bash
# Zobraz všechny databáze
/mcp list_databases

# Přepni na jinou databázi
/mcp change_database "dwh-n8n"

# Vypiš tabulky
/mcp list_tables

# Zobraz schéma tabulky
/mcp get_schema "users"
```

### 2. SQL dotazy

```bash
# Jednoduchý SELECT
/mcp query_data "SELECT * FROM users LIMIT 10"

# S podmínkou
/mcp query_data "SELECT name, email FROM users WHERE active = 1"

# Agregace
/mcp query_data "SELECT COUNT(*) as total FROM orders"

# JOIN
/mcp query_data "SELECT u.name, o.order_date FROM users u JOIN orders o ON u.id = o.user_id LIMIT 20"
```

### 3. Práce s více databázemi

```bash
# Dotaz na konkrétní databázi (bez změny globální)
/mcp list_tables database="analytics_db"
/mcp query_data "SELECT * FROM logs LIMIT 5" database="analytics_db"

# Změna globální databáze
/mcp change_database "production_db"
/mcp list_tables  # Nyní zobrazí tabulky z production_db
```

## 🔒 Bezpečnostní funkce

- ✅ **Pouze SELECT dotazy** - INSERT/UPDATE/DELETE jsou blokovány
- ✅ **Automatické LIMIT** - Pokud chybí, přidá se automaticky
- ✅ **SQL injection ochrana** - Parametrizované dotazy
- ✅ **Connection pooling** - Efektivní správa spojení
- ✅ **Error handling** - Strukturované chybové zprávy

## 🔧 Změna konfigurace

### Změna databáze

```bash
# Odstranit současný server
claude mcp remove mysql -s local

# Přidat s novou databází
claude mcp add mysql -e DB_HOST=fssx0132x.fs.cz.int.vitesco.com -e DB_PORT=3309 -e DB_USER=notifier -e DB_PASSWORD=yfiton -e DB_NAME=nova_databaze -e DEBUG_MODE=false -- P:\00_IT_Applications\05_PYTHON\mcp-server-mysql\.venv\Scripts\python.exe P:\00_IT_Applications\05_PYTHON\mcp-server-mysql\mysql_server.py
```

### Vypnutí debug módu

```bash
claude mcp remove mysql -s local
claude mcp add mysql -e DB_HOST=fssx0132x.fs.cz.int.vitesco.com -e DB_PORT=3309 -e DB_USER=notifier -e DB_PASSWORD=yfiton -e DB_NAME=ipmanagement -e DEBUG_MODE=false -- P:\00_IT_Applications\05_PYTHON\mcp-server-mysql\.venv\Scripts\python.exe P:\00_IT_Applications\05_PYTHON\mcp-server-mysql\mysql_server.py
```

## 🐛 Řešení problémů

### Server se nehlásí jako připojený

```bash
# Zkontrolujte status
claude mcp list

# Zkontrolujte logy
# Logy jsou v stderr, můžete je vidět při spuštění serveru
```

### Chyba připojení k databázi

```bash
# Test připojení mimo MCP
python test_connection.py

# Zkontrolujte .env soubor
type .env

# Zkontrolujte, že MySQL server běží
# ping fssx0132x.fs.cz.int.vitesco.com
```

### Python nebo závislosti chybí

```bash
# Aktivujte virtual environment
.venv\Scripts\activate

# Zkontrolujte závislosti
pip list | findstr -i "fastmcp aiomysql"

# Reinstalujte pokud chybí
pip install -r requirements.txt
```

## 📝 Konfigurační soubor

Konfigurace je uložena v:
```
C:\Users\uidv7359\.claude.json
```

Můžete ji editovat ručně, ale doporučujeme používat `claude mcp` příkazy.

## 🎉 Hotovo!

Váš MySQL MCP server je připravený k použití. Zkuste:

```bash
/mcp list_databases
```

---

**✅ Server je plně funkční a připojený k databázi ipmanagement!**
