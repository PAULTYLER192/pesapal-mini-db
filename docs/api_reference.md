# API Reference

Complete reference for the Mini DB RDBMS classes and methods.

---

## Database Class

The `Database` class manages multiple tables, handles schema persistence, and executes SQL-like queries.

### Constructor

```python
Database(base_dir: Optional[str] = None)
```

**Parameters:**
- `base_dir` (str, optional): Base directory for data and metadata storage. Defaults to project root.

**Description:**
Creates a new Database instance. Automatically creates `data/` and `metadata/` directories if they don't exist. Auto-loads all existing tables from the metadata folder.

**Example:**
```python
from database import Database

db = Database(base_dir="/path/to/project")
```

---

### Methods

#### `create_table(name, columns, primary_key=None)`

Creates a new table with the specified schema.

**Parameters:**
- `name` (str): Name of the table to create
- `columns` (List[Dict[str, str]]): Column definitions with `name` and `type` keys
- `primary_key` (str, optional): Column name to use as primary key

**Returns:**
- `dict`: The created schema

**Raises:**
- `FileExistsError`: If table already exists

**Example:**
```python
schema = db.create_table(
    name="users",
    columns=[
        {"name": "id", "type": "int"},
        {"name": "name", "type": "str"},
        {"name": "email", "type": "str"}
    ],
    primary_key="id"
)
```

---

#### `get_table(name)`

Retrieves a table object by name. Returns cached instance if available.

**Parameters:**
- `name` (str): Name of the table to retrieve

**Returns:**
- `Table`: The requested table object

**Raises:**
- `FileNotFoundError`: If table doesn't exist

**Example:**
```python
users = db.get_table("users")
```

---

#### `list_tables()`

Returns a sorted list of all table names.

**Returns:**
- `List[str]`: List of table names

**Example:**
```python
tables = db.list_tables()
# Returns: ['products', 'users']
```

---

#### `drop_table(name)`

Deletes a table, removing both schema and data files.

**Parameters:**
- `name` (str): Name of the table to drop

**Example:**
```python
db.drop_table("users")
```

---

#### `describe(name)`

Returns the schema for a table.

**Parameters:**
- `name` (str): Name of the table

**Returns:**
- `dict`: Schema dictionary with `name`, `columns`, and optional `primary_key`

**Raises:**
- `FileNotFoundError`: If table doesn't exist

**Example:**
```python
schema = db.describe("users")
# Returns: {"name": "users", "columns": [...], "primary_key": "id"}
```

---

#### `execute(sql)`

Executes a SQL-like query string.

**Parameters:**
- `sql` (str): SQL command to execute

**Returns:**
- Varies by command type:
  - `INSERT`: Returns inserted row dict
  - `SELECT`: Returns list of matching rows
  - `UPDATE`: Returns `{"updated": count}`
  - `DELETE`: Returns `{"deleted": count}`
  - `CREATE TABLE`: Returns schema dict
  - `DROP TABLE`: Returns `{"ok": True}`
  - `SHOW TABLES`: Returns list of table names
  - `DESCRIBE`: Returns schema dict

**Raises:**
- `ValueError`: If SQL syntax is invalid or unsupported

**Example:**
```python
# Insert
result = db.execute("INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")

# Select
rows = db.execute("SELECT * FROM users WHERE id = 1")

# Update
result = db.execute("UPDATE users SET name = 'Bob' WHERE id = 1")

# Delete
result = db.execute("DELETE FROM users WHERE id = 1")
```

---

## Table Class

The `Table` class represents a single table with JSONL-backed storage and optional primary key indexing.

### Constructor

```python
Table(name: str, schema: Dict[str, Any], data_dir: str, primary_key: Optional[str] = None)
```

**Parameters:**
- `name` (str): Table name
- `schema` (dict): Schema with `name` and `columns` keys
- `data_dir` (str): Directory path for JSONL data files
- `primary_key` (str, optional): Column name to use as primary key

**Description:**
Creates a table instance. Auto-creates JSONL file if it doesn't exist. If `primary_key` is specified, builds an in-memory index for O(1) lookups.

**Note:** Usually created via `Database.create_table()` or `Database.get_table()` rather than directly.

---

### Methods

#### `insert(values)`

Inserts a new row into the table with data validation.

**Parameters:**
- `values` (dict): Column-value pairs to insert

**Returns:**
- `dict`: The inserted row (with type conversions applied)

**Raises:**
- `ValueError`: If required columns are missing
- `TypeError`: If values cannot be converted to schema types
- `DuplicateKeyError`: If primary key value already exists

**Example:**
```python
table = db.get_table("users")
row = table.insert({
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com"
})
```

---

#### `select(where=None, columns=None, limit=None)`

Queries rows from the table with optional filtering.

**Parameters:**
- `where` (dict, optional): Column-value pairs for filtering (AND logic)
- `columns` (list, optional): Column names to return. None returns all columns
- `limit` (int, optional): Maximum number of rows to return

**Returns:**
- `List[dict]`: List of matching rows

**Example:**
```python
# Select all
all_users = table.select()

# Filter by condition
alice = table.select(where={"name": "Alice"})

# Select specific columns
names = table.select(columns=["name", "email"])

# Combine filters
recent = table.select(where={"active": True}, limit=10)
```

---

#### `select_by_id(pk_value)`

Fast O(1) lookup of a row by primary key value.

**Parameters:**
- `pk_value`: The primary key value to look up

**Returns:**
- `dict` or `None`: The matching row, or None if not found

**Raises:**
- `ValueError`: If table has no primary key defined

**Example:**
```python
user = table.select_by_id(1)
# Returns: {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

---

#### `update(set_values, where=None)`

Updates rows matching the WHERE condition.

**Parameters:**
- `set_values` (dict): Column-value pairs to update
- `where` (dict, optional): Filter condition. If None, updates all rows

**Returns:**
- `int`: Number of rows updated

**Example:**
```python
# Update specific row
count = table.update(
    set_values={"name": "Bob"},
    where={"id": 1}
)

# Update all rows
count = table.update(set_values={"active": False})
```

---

#### `delete(where=None)`

Deletes rows matching the WHERE condition.

**Parameters:**
- `where` (dict, optional): Filter condition. If None, deletes all rows

**Returns:**
- `int`: Number of rows deleted

**Example:**
```python
# Delete specific row
count = table.delete(where={"id": 1})

# Delete multiple rows
count = table.delete(where={"active": False})
```

---

#### `count()`

Returns the total number of rows in the table.

**Returns:**
- `int`: Row count

**Example:**
```python
total = table.count()
```

---

## Exceptions

### `DuplicateKeyError`

Raised when attempting to insert a row with a duplicate primary key value.

**Example:**
```python
from table import DuplicateKeyError

try:
    table.insert({"id": 1, "name": "Alice"})
    table.insert({"id": 1, "name": "Bob"})  # Duplicate!
except DuplicateKeyError as e:
    print(f"Error: {e}")
```

---

## Type System

Supported column types:

| Type | Python Type | Examples |
|------|-------------|----------|
| `str`, `string` | `str` | `"Alice"`, `"test@example.com"` |
| `int`, `integer` | `int` | `1`, `42`, `-10` |
| `float`, `double` | `float` | `3.14`, `99.99` |
| `bool`, `boolean` | `bool` | `True`, `False` |

**Type Conversion:**
- Automatic type conversion on INSERT (with validation)
- `null` or `None` values allowed for any type
- Invalid conversions raise `TypeError`

---

## Usage Examples

### Complete Workflow

```python
from database import Database

# Initialize database
db = Database()

# Create table
db.create_table(
    name="products",
    columns=[
        {"name": "id", "type": "int"},
        {"name": "name", "type": "str"},
        {"name": "price", "type": "float"},
        {"name": "active", "type": "bool"}
    ],
    primary_key="id"
)

# Get table
products = db.get_table("products")

# Insert data
products.insert({"id": 1, "name": "Widget", "price": 19.99, "active": True})
products.insert({"id": 2, "name": "Gadget", "price": 29.99, "active": True})

# Query data
all_products = products.select()
active = products.select(where={"active": True})
cheap = products.select(where={"price": 19.99})

# Fast lookup
product = products.select_by_id(1)

# Update
products.update({"price": 24.99}, where={"id": 1})

# Delete
products.delete(where={"id": 2})

# Count
total = products.count()

# Execute SQL
result = db.execute("SELECT * FROM products WHERE active = true LIMIT 10")
```

---

## Performance Characteristics

| Operation | Without Primary Key | With Primary Key |
|-----------|-------------------|------------------|
| Insert | O(1) append | O(1) append + index update |
| Select by PK | O(n) scan | O(1) dictionary lookup |
| Select (filtered) | O(n) scan | O(n) scan |
| Update | O(n) read + write | O(n) read + write + index update |
| Delete | O(n) read + write | O(n) read + write + index update |
| Count | O(n) iteration | O(n) iteration |

**Note:** All operations that modify data require rewriting the entire JSONL file for consistency.
