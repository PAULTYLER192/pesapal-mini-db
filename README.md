# pesapal-mini-db

Mini JSONL-backed database with a simple SQL-like interface, a CLI REPL, and a tiny Flask web UI.

**Structure**
- `data/`: table heap data stored as `.jsonl` (one JSON per line)
- `metadata/`: table schemas stored as JSON (catalog)
- `src/`: core logic
	- `table.py`: Table CRUD engine
	- `database.py`: Database manager + SQL dispatcher
	- `parser.py`: Minimal SQL string parser
- `main.py`: CLI REPL
- `app/`: Flask web UI (`app.py`, `templates/index.html`)
- `requirements.txt`: dependencies

**Setup**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**CLI REPL**
```powershell
python .\main.py
```

Example session:
```sql
CREATE TABLE products (id int, name str, price float);
INSERT INTO products (id, name, price) VALUES (1, 'Pen', 1.99);
INSERT INTO products (id, name, price) VALUES (2, 'Notebook', 3.5);
SELECT * FROM products LIMIT 10;
SELECT name, price FROM products WHERE id = 2;
UPDATE products SET price = 3.75 WHERE id = 2;
DELETE FROM products WHERE name = 'Pen';
SHOW TABLES;
DESCRIBE products;
DROP TABLE products;
```

Notes:
- WHERE supports equality (`col = value`) with `AND` conjunctions.
- Supported types: `str`, `int`, `float`, `bool`.

**Web UI**
```powershell
python .\app\app.py
```
Open http://127.0.0.1:5000 to:
- Create tables (e.g. `id:int, name:str, price:float`)
- Insert rows with JSON (e.g. `{ "id": 1, "name": "Pen", "price": 1.99 }`)
- Run SQL (SELECT/INSERT/UPDATE/DELETE/SHOW/DESCRIBE)

**Data & Schemas**
- Tables are persisted as `data/<table>.jsonl`.
- Schemas are stored as `metadata/<table>.json` with:
```json
{ "name": "products", "columns": [ {"name": "id", "type": "int"}, {"name": "name", "type": "str"}, {"name": "price", "type": "float"} ] }
```

**Development**
- The code favors simplicity and small datasets; UPDATE/DELETE rewrite files.
- If you change parser rules, adjust `src/parser.py` and run via CLI.