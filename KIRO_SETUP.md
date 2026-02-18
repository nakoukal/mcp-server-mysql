# MySQL MCP Server — Nastavení pro Kiro / Claude Code CLI

## Přidání serveru

```bash
claude mcp add mysql \
  -e DB_HOST=your_host \
  -e DB_PORT=3306 \
  -e DB_USER=your_user \
  -e DB_PASSWORD=your_password \
  -e DB_NAME=your_database \
  -e DEBUG_MODE=false \
  -- /abs/cesta/k/venv/bin/python /abs/cesta/k/mysql_server.py
```

> **Tip:** Místo `DB_NAME` v příkazu výše můžeš databázi vynechat a přepínat ji za běhu nástrojem `change_database`.

## Správa serverů

```bash
claude mcp list           # seznam všech MCP serverů
claude mcp get mysql      # detail serveru
claude mcp remove mysql -s local   # odstranění
```

## Dostupné nástroje

| Nástroj | Popis | Příklad |
|---------|-------|---------|
| `list_databases` | Seznam všech databází | `list_databases` |
| `change_database` | Přepnutí aktivní databáze | `change_database "production"` |
| `query_data` | SELECT dotazy | `query_data "SELECT * FROM users LIMIT 5"` |
| `execute_write` | INSERT / UPDATE / DELETE v transakci | `execute_write "UPDATE orders SET status='shipped' WHERE id=1"` |
| `list_tables` | Seznam tabulek | `list_tables` nebo `list_tables database="analytics"` |
| `get_schema` | Schéma tabulky | `get_schema "users"` |

## Příklady použití

### Čtení dat

```bash
# Zobrazení databází a tabulek
/mcp list_databases
/mcp list_tables
/mcp list_tables database="analytics_db"

# Schema tabulky
/mcp get_schema "orders"

# SELECT dotazy
/mcp query_data "SELECT * FROM users LIMIT 10"
/mcp query_data "SELECT name, email FROM users WHERE active = 1"
/mcp query_data "SELECT COUNT(*) as total FROM orders"
/mcp query_data "SELECT * FROM logs LIMIT 5" database="analytics_db"
```

### Zápis dat

```bash
# INSERT
/mcp execute_write "INSERT INTO products (name, price) VALUES ('Widget', 9.99)"

# UPDATE
/mcp execute_write "UPDATE orders SET status = 'shipped' WHERE id = 42"

# DELETE
/mcp execute_write "DELETE FROM sessions WHERE expires_at < NOW()"
```

### Přepínání databází

```bash
# Trvalá změna aktivní databáze
/mcp change_database "analytics_db"
/mcp list_tables  # zobrazí tabulky z analytics_db

# Jednorázový dotaz na jinou databázi
/mcp query_data "SELECT * FROM logs LIMIT 5" database="logs_db"
```

## Konfigurace přes .env soubor

Místo předávání přihlašovacích údajů přímo v příkazu `claude mcp add` lze použít `.env` soubor:

```env
DB_HOST=your_host
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
DEBUG_MODE=false
```

Pak přidej server pouze s `cwd`:

```bash
claude mcp add mysql \
  --cwd /abs/cesta/k/mysql-mcp-server \
  -- /abs/cesta/k/venv/bin/python /abs/cesta/k/mysql_server.py
```

## Bezpečnostní poznámky

- `query_data` povoluje pouze `SELECT` dotazy
- `execute_write` povoluje `INSERT`, `UPDATE`, `DELETE`, `REPLACE` — každý dotaz běží v transakci s automatickým rollbackem při chybě
- DDL operace (`CREATE`, `DROP`, `ALTER`) nejsou k dispozici (je nutné je provést přímo v DB)
- Preferuj parametrizované dotazy pro předávání hodnot: `execute_write(query="INSERT INTO t (col) VALUES (%s)", params=["value"])`

## Řešení problémů

### Server není v seznamu

```bash
claude mcp list
# Pokud chybí, znovu ho přidej příkazem výše
```

### Chyba připojení k databázi

```bash
python test_connection.py
# nebo
python -c "import aiomysql; print('aiomysql OK')"
```

### Python nebo závislosti chybí

```bash
source venv/bin/activate
pip install -r requirements.txt
pip list | grep -i "fastmcp\|aiomysql"
```
