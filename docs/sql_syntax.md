# SQL Syntax Reference

This document describes the SQL-like syntax supported by the Mini DB parser. Since we use a custom parser (not a full SQL engine), only a subset of SQL commands is supported.

---

## Supported Commands

### 1. CREATE TABLE

Creates a new table with a schema.

**Syntax:**
```sql
CREATE TABLE table_name (column1 type1, column2 type2, ...)
```

**Supported Types:**
- `int`, `integer` - Integer numbers
- `float`, `double` - Floating-point numbers
- `str`, `string` - Text strings
- `bool`, `boolean` - Boolean values (true/false)

**Examples:**
```sql
CREATE TABLE users (id int, name str, email str)

CREATE TABLE products (id int, title str, price float, active bool)

CREATE TABLE logs (timestamp int, message str, level str)
```

**Notes:**
- Table names must be valid identifiers (alphanumeric + underscore, starting with letter/underscore)
- Column names follow the same rules
- Primary keys must be specified via the Database API (not supported in SQL syntax)

---

### 2. DROP TABLE

Deletes a table and all its data.

**Syntax:**
```sql
DROP TABLE table_name
```

**Examples:**
```sql
DROP TABLE users

DROP TABLE old_data
```

**Warning:** This permanently deletes both the schema and data files. Cannot be undone.

---

### 3. INSERT INTO

Inserts a new row into a table.

**Syntax:**
```sql
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...)
```

**Supported Value Types:**
- Integers: `1`, `42`, `-10`
- Floats: `3.14`, `99.99`, `-5.5`
- Strings: `'Alice'`, `"Bob"`, `'test@example.com'`
- Booleans: `true`, `false` (case-insensitive)
- Null: `NULL`, `null`

**Examples:**
```sql
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')

INSERT INTO products (id, title, price, active) VALUES (1, 'Widget', 19.99, true)

INSERT INTO logs (timestamp, message, level) VALUES (1234567890, 'System started', 'INFO')

-- Null values
INSERT INTO users (id, name, email) VALUES (2, NULL, NULL)
```

**Notes:**
- Number of columns must match number of values
- String values can use single (`'`) or double (`"`) quotes
- Values are type-validated against the table schema
- Primary key uniqueness is enforced if table has a primary key

---

### 4. SELECT

Queries rows from a table.

**Syntax:**
```sql
SELECT column1, column2, ... FROM table_name [WHERE condition] [LIMIT n]

SELECT * FROM table_name [WHERE condition] [LIMIT n]
```

**WHERE Clause:**
- Supports equality comparisons: `column = value`
- Multiple conditions with AND: `column1 = value1 AND column2 = value2`
- OR is NOT supported
- Only `=` operator supported (no `<`, `>`, `!=`, `LIKE`, etc.)

**Examples:**
```sql
-- Select all columns
SELECT * FROM users

-- Select specific columns
SELECT id, name FROM users

SELECT name, email FROM users

-- Filter with WHERE
SELECT * FROM users WHERE id = 1

SELECT * FROM products WHERE active = true

SELECT * FROM logs WHERE level = 'ERROR'

-- Multiple conditions (AND)
SELECT * FROM users WHERE id = 1 AND name = 'Alice'

SELECT * FROM products WHERE active = true AND price = 19.99

-- Limit results
SELECT * FROM users LIMIT 10

SELECT * FROM logs WHERE level = 'ERROR' LIMIT 100

-- Combined
SELECT name, email FROM users WHERE active = true LIMIT 50
```

**Notes:**
- `*` selects all columns
- Column names must be comma-separated
- WHERE conditions are evaluated with AND logic only
- LIMIT must be a positive integer

---

### 5. UPDATE

Modifies existing rows in a table.

**Syntax:**
```sql
UPDATE table_name SET column1 = value1, column2 = value2, ... [WHERE condition]
```

**Examples:**
```sql
-- Update specific row
UPDATE users SET name = 'Bob' WHERE id = 1

UPDATE products SET price = 24.99 WHERE id = 1

-- Update multiple columns
UPDATE users SET name = 'Charlie', email = 'charlie@example.com' WHERE id = 2

-- Update all rows (use with caution!)
UPDATE products SET active = false

UPDATE users SET status = 'inactive'
```

**Notes:**
- Without WHERE clause, updates ALL rows
- SET clause can update multiple columns (comma-separated)
- WHERE clause supports same conditions as SELECT (equality with AND)

---

### 6. DELETE

Removes rows from a table.

**Syntax:**
```sql
DELETE FROM table_name [WHERE condition]
```

**Examples:**
```sql
-- Delete specific row
DELETE FROM users WHERE id = 1

-- Delete with condition
DELETE FROM products WHERE active = false

DELETE FROM logs WHERE level = 'DEBUG'

-- Delete multiple conditions
DELETE FROM users WHERE active = false AND created_at = 0

-- Delete all rows (use with caution!)
DELETE FROM temp_data
```

**Notes:**
- Without WHERE clause, deletes ALL rows
- WHERE clause supports same conditions as SELECT
- Does not drop the table (schema remains)

---

### 7. SHOW TABLES

Lists all tables in the database.

**Syntax:**
```sql
SHOW TABLES
```

**Examples:**
```sql
SHOW TABLES
```

**Returns:**
List of table names: `['products', 'users', 'logs']`

---

### 8. DESCRIBE

Shows the schema for a table.

**Syntax:**
```sql
DESCRIBE table_name
```

**Examples:**
```sql
DESCRIBE users

DESCRIBE products
```

**Returns:**
Schema dictionary with table name, columns (name and type), and primary key (if set).

---

## Limitations

### What's NOT Supported

**JOIN Operations:**
```sql
-- ❌ NOT SUPPORTED
SELECT * FROM users JOIN orders ON users.id = orders.user_id
```

**Subqueries:**
```sql
-- ❌ NOT SUPPORTED
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)
```

**Advanced WHERE Operators:**
```sql
-- ❌ NOT SUPPORTED
SELECT * FROM products WHERE price > 50
SELECT * FROM users WHERE name LIKE '%Alice%'
SELECT * FROM logs WHERE level != 'DEBUG'
SELECT * FROM products WHERE price BETWEEN 10 AND 50
```

**OR Logic:**
```sql
-- ❌ NOT SUPPORTED
SELECT * FROM users WHERE id = 1 OR id = 2
```

**Aggregations:**
```sql
-- ❌ NOT SUPPORTED
SELECT COUNT(*) FROM users
SELECT AVG(price) FROM products
SELECT MAX(created_at) FROM logs
```

**GROUP BY / HAVING:**
```sql
-- ❌ NOT SUPPORTED
SELECT status, COUNT(*) FROM users GROUP BY status
```

**ORDER BY:**
```sql
-- ❌ NOT SUPPORTED
SELECT * FROM users ORDER BY name ASC
```

**ALTER TABLE:**
```sql
-- ❌ NOT SUPPORTED
ALTER TABLE users ADD COLUMN age int
```

---

## Syntax Rules

### Case Sensitivity
- **Keywords:** Case-insensitive (`SELECT`, `select`, `SeLeCt` all work)
- **Table names:** Case-sensitive
- **Column names:** Case-sensitive
- **String values:** Case-sensitive

### Quotes
- Single quotes: `'Alice'`
- Double quotes: `"Alice"`
- Both work for string values

### Semicolons
- Optional at end of statement
- `SELECT * FROM users;` and `SELECT * FROM users` both work

### Whitespace
- Extra whitespace is ignored
- Can span multiple lines

### Identifiers
- Table and column names: `[a-zA-Z_][a-zA-Z0-9_]*`
- Must start with letter or underscore
- Can contain letters, numbers, underscores

---

## Type Conversion Examples

The parser automatically infers types from values:

```sql
-- Integer
INSERT INTO users (id) VALUES (42)        -- int: 42

-- Float
INSERT INTO products (price) VALUES (19.99)  -- float: 19.99

-- Boolean
INSERT INTO users (active) VALUES (true)     -- bool: True
INSERT INTO users (active) VALUES (false)    -- bool: False

-- String
INSERT INTO users (name) VALUES ('Alice')    -- str: "Alice"
INSERT INTO users (name) VALUES ("Bob")      -- str: "Bob"

-- Null
INSERT INTO users (email) VALUES (NULL)      -- None
INSERT INTO users (email) VALUES (null)      -- None
```

---

## Parser Implementation

The parser uses:
- **Regex patterns** for keyword detection and structure matching
- **String splitting** for comma-separated lists (quote-aware)
- **Type inference** for value parsing

Example parser flow for `SELECT * FROM users WHERE id = 1`:
1. Match `SELECT` keyword (case-insensitive)
2. Extract columns (`*`)
3. Extract table name (`users`)
4. Extract WHERE clause (`id = 1`)
5. Parse condition into `{"id": 1}` dictionary
6. Return AST: `{"type": "select", "name": "users", "columns": None, "where": {"id": 1}}`

---

## Workarounds for Unsupported Features

### Pagination
```python
# Instead of: SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 10
# Use Python slicing:
all_users = table.select()
page_2 = all_users[10:20]
```

### Count
```python
# Instead of: SELECT COUNT(*) FROM users
# Use the count() method:
count = table.count()
```

### Filtering with OR
```python
# Instead of: SELECT * FROM users WHERE id = 1 OR id = 2
# Use Python filtering:
users = table.select()
filtered = [u for u in users if u['id'] in [1, 2]]
```

### Comparison Operators
```python
# Instead of: SELECT * FROM products WHERE price > 50
# Use Python filtering:
products = table.select()
expensive = [p for p in products if p['price'] > 50]
```

### Sorting
```python
# Instead of: SELECT * FROM users ORDER BY name
# Use Python sorting:
users = table.select()
sorted_users = sorted(users, key=lambda u: u['name'])
```

---

## Best Practices

1. **Use Primary Keys:** Enable O(1) lookups with `select_by_id()`
2. **Batch Operations:** Use Python for complex filtering instead of multiple queries
3. **Validate First:** Check syntax with simple queries before complex ones
4. **Use Python API:** For advanced operations, use `Table` methods directly
5. **WHERE Specificity:** Make WHERE clauses as specific as possible for performance

---

## Examples of Valid Queries

```sql
-- Data Definition
CREATE TABLE users (id int, name str, email str, active bool)
DROP TABLE old_table

-- Data Insertion
INSERT INTO users (id, name, email, active) VALUES (1, 'Alice', 'alice@example.com', true)
INSERT INTO users (id, name, email, active) VALUES (2, 'Bob', 'bob@example.com', true)

-- Data Query
SELECT * FROM users
SELECT id, name FROM users
SELECT * FROM users WHERE id = 1
SELECT * FROM users WHERE active = true LIMIT 10
SELECT name, email FROM users WHERE active = true AND id = 1

-- Data Modification
UPDATE users SET name = 'Alice Johnson' WHERE id = 1
UPDATE users SET active = false, email = 'newemail@example.com' WHERE id = 2
DELETE FROM users WHERE id = 1
DELETE FROM users WHERE active = false

-- Utility
SHOW TABLES
DESCRIBE users
```
