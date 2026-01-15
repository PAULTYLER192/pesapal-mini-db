# API Documentation

## Overview

Pesapal Mini Database provides a Python API for interacting with an in-memory database. This document describes the core classes and their methods.

## Database Class

The `Database` class represents the main database instance.

### Constructor

```python
Database(name="minidb")
```

Creates a new database instance.

**Parameters:**
- `name` (str, optional): Database name. Default: "minidb"

**Example:**
```python
from src.db import Database

db = Database("my_database")
```

### Methods

#### create_table(table_name, columns)

Creates a new table in the database.

**Parameters:**
- `table_name` (str): Name of the table
- `columns` (list): List of column names

**Returns:** Table object

**Raises:**
- `ValueError`: If table name is invalid, table already exists, or no columns provided

**Example:**
```python
table = db.create_table('users', ['id', 'name', 'email', 'age'])
```

#### drop_table(table_name)

Drops (deletes) a table from the database.

**Parameters:**
- `table_name` (str): Name of the table to drop

**Returns:** True if successful

**Raises:**
- `ValueError`: If table does not exist

**Example:**
```python
db.drop_table('users')
```

#### get_table(table_name)

Retrieves a table object by name.

**Parameters:**
- `table_name` (str): Name of the table

**Returns:** Table object

**Raises:**
- `ValueError`: If table does not exist

**Example:**
```python
table = db.get_table('users')
```

#### list_tables()

Lists all table names in the database.

**Returns:** List of table names (list of str)

**Example:**
```python
tables = db.list_tables()
print(tables)  # ['users', 'products', 'orders']
```

#### insert(table_name, values)

Inserts a row into a table.

**Parameters:**
- `table_name` (str): Name of the table
- `values` (dict): Dictionary mapping column names to values

**Returns:** True if successful

**Raises:**
- `ValueError`: If table does not exist or column validation fails

**Example:**
```python
db.insert('users', {
    'id': 1,
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30
})
```

#### select(table_name, columns=None, where=None)

Selects rows from a table.

**Parameters:**
- `table_name` (str): Name of the table
- `columns` (list, optional): List of column names to return. None for all columns
- `where` (dict, optional): WHERE clause as dictionary with keys 'column', 'operator', 'value'

**Returns:** List of matching rows (list of dict)

**Example:**
```python
# Select all columns
rows = db.select('users')

# Select specific columns
rows = db.select('users', columns=['name', 'email'])

# Select with WHERE clause
rows = db.select('users', where={'column': 'age', 'operator': '>', 'value': 25})
```

#### update(table_name, values, where=None)

Updates rows in a table.

**Parameters:**
- `table_name` (str): Name of the table
- `values` (dict): Dictionary mapping column names to new values
- `where` (dict, optional): WHERE clause as dictionary

**Returns:** Number of rows updated (int)

**Example:**
```python
# Update with WHERE clause
count = db.update('users', {'age': 31}, where={'column': 'id', 'operator': '=', 'value': 1})

# Update all rows
count = db.update('users', {'status': 'active'})
```

#### delete(table_name, where=None)

Deletes rows from a table.

**Parameters:**
- `table_name` (str): Name of the table
- `where` (dict, optional): WHERE clause as dictionary

**Returns:** Number of rows deleted (int)

**Example:**
```python
# Delete with WHERE clause
count = db.delete('users', where={'column': 'id', 'operator': '=', 'value': 1})

# Delete all rows
count = db.delete('users')
```

---

## Table Class

The `Table` class represents a table in the database.

### Constructor

```python
Table(name, columns)
```

Creates a new table instance.

**Parameters:**
- `name` (str): Table name
- `columns` (list): List of column names

### Methods

#### insert(values)

Inserts a row into the table.

**Parameters:**
- `values` (dict): Dictionary mapping column names to values

**Returns:** True if successful

#### select(columns=None, where=None)

Selects rows from the table.

**Parameters:**
- `columns` (list, optional): List of column names to return
- `where` (dict, optional): WHERE clause

**Returns:** List of matching rows

#### update(values, where=None)

Updates rows in the table.

**Parameters:**
- `values` (dict): New values
- `where` (dict, optional): WHERE clause

**Returns:** Number of rows updated

#### delete(where=None)

Deletes rows from the table.

**Parameters:**
- `where` (dict, optional): WHERE clause

**Returns:** Number of rows deleted

#### count()

Returns the number of rows in the table.

**Returns:** Number of rows (int)

---

## QueryParser Class

The `QueryParser` class parses SQL-like query strings.

### Constructor

```python
QueryParser()
```

Creates a new parser instance.

### Methods

#### parse(query)

Parses a SQL-like query string.

**Parameters:**
- `query` (str): SQL-like query string

**Returns:** Parsed query as dictionary

**Raises:**
- `ValueError`: If query syntax is invalid

**Example:**
```python
from src.parser import QueryParser

parser = QueryParser()
parsed = parser.parse("SELECT * FROM users WHERE age > 25")
print(parsed)
# {
#     'type': 'SELECT',
#     'table': 'users',
#     'columns': None,
#     'where': {'column': 'age', 'operator': '>', 'value': 25}
# }
```

---

## Utility Functions

### validate_column_name(name)

Validates a column name.

**Parameters:**
- `name` (str): Column name

**Returns:** True if valid, False otherwise

### validate_table_name(name)

Validates a table name.

**Parameters:**
- `name` (str): Table name

**Returns:** True if valid, False otherwise

### parse_value(value_str)

Parses a string value to appropriate Python type.

**Parameters:**
- `value_str` (str): Value as string

**Returns:** Appropriate Python type (int, float, str, bool, None)

### format_value(value)

Formats a Python value for display.

**Parameters:**
- `value`: Value to format

**Returns:** Formatted value (str)

### compare_values(val1, operator, val2)

Compares two values using the specified operator.

**Parameters:**
- `val1`: First value
- `operator` (str): Comparison operator (=, !=, <, >, <=, >=)
- `val2`: Second value

**Returns:** Result of comparison (bool)

---

## Complete Example

```python
from src.db import Database
from src.parser import QueryParser

# Create database
db = Database("example_db")

# Create table
db.create_table('users', ['id', 'name', 'email', 'age'])

# Insert data
db.insert('users', {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'age': 30})
db.insert('users', {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'age': 25})

# Select data
all_users = db.select('users')
print(f"All users: {all_users}")

older_users = db.select('users', where={'column': 'age', 'operator': '>', 'value': 25})
print(f"Users over 25: {older_users}")

# Update data
db.update('users', {'age': 31}, where={'column': 'id', 'operator': '=', 'value': 1})

# Delete data
db.delete('users', where={'column': 'id', 'operator': '=', 'value': 2})

# Using QueryParser
parser = QueryParser()
parsed = parser.parse("SELECT name, email FROM users WHERE age >= 30")
rows = db.select(parsed['table'], parsed['columns'], parsed['where'])
print(f"Query results: {rows}")
```
