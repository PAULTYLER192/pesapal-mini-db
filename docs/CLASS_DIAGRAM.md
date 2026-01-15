# Class Diagram

## Overview

This document provides the UML class diagram for the Pesapal Mini Database system, showing the relationships between classes and their methods.

## Complete Class Diagram

```
┌──────────────────────────────────────────────┐
│              <<module>>                       │
│                utils                          │
├──────────────────────────────────────────────┤
│ + validate_column_name(name: str) → bool     │
│ + validate_table_name(name: str) → bool      │
│ + parse_value(value_str: str) → any          │
│ + format_value(value: any) → str             │
│ + compare_values(val1, op: str, val2) → bool │
└──────────────────────────────────────────────┘
                       △
                       │ uses
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────┴────────────────────┐  ┌────┴─────────────────────┐
│       Database             │  │        Table             │
├────────────────────────────┤  ├──────────────────────────┤
│ - name: str                │  │ - name: str              │
│ - tables: dict[str, Table] │  │ - columns: list[str]     │
├────────────────────────────┤  │ - rows: list[dict]       │
│ + __init__(name: str)      │  ├──────────────────────────┤
│ + create_table(            │  │ + __init__(name: str,    │
│     name: str,             │  │     columns: list)       │
│     columns: list) → Table │  │ + insert(                │
│ + drop_table(              │  │     values: dict) → bool │
│     name: str) → bool      │  │ + select(                │
│ + get_table(               │  │     columns: list,       │
│     name: str) → Table     │  │     where: dict) → list  │
│ + list_tables() → list     │  │ + update(                │
│ + insert(                  │  │     values: dict,        │
│     table: str,            │  │     where: dict) → int   │
│     values: dict) → bool   │  │ + delete(                │
│ + select(                  │  │     where: dict) → int   │
│     table: str,            │  │ + count() → int          │
│     columns: list,         │  └──────────────────────────┘
│     where: dict) → list    │              △
│ + update(                  │              │
│     table: str,            │              │ contains
│     values: dict,          │              │ (1:N)
│     where: dict) → int     │              │
│ + delete(                  │  ┌───────────┴───────────┐
│     table: str,            │  │                       │
│     where: dict) → int     │  │    dict (Row data)    │
│ + execute_query(           │  │                       │
│     query: str) → any      │  └───────────────────────┘
└────────────────────────────┘
         │
         │ uses
         │
┌────────┴─────────────────────────┐
│        QueryParser               │
├──────────────────────────────────┤
│ + __init__()                     │
│ + parse(query: str) → dict       │
├──────────────────────────────────┤
│ - _parse_create_table() → dict   │
│ - _parse_drop_table() → dict     │
│ - _parse_insert() → dict         │
│ - _parse_select() → dict         │
│ - _parse_update() → dict         │
│ - _parse_delete() → dict         │
│ - _parse_where() → dict          │
│ - _parse_values_list() → list    │
└──────────────────────────────────┘
```

## Class Details

### Database Class

**Purpose**: Main database engine that manages tables and operations.

**Attributes:**
- `name: str` - Name of the database instance
- `tables: dict[str, Table]` - Dictionary mapping table names to Table objects

**Methods:**

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `__init__` | `name: str = "minidb"` | None | Initialize database |
| `create_table` | `table_name: str, columns: list[str]` | `Table` | Create new table |
| `drop_table` | `table_name: str` | `bool` | Drop existing table |
| `get_table` | `table_name: str` | `Table` | Retrieve table object |
| `list_tables` | None | `list[str]` | List all table names |
| `insert` | `table_name: str, values: dict` | `bool` | Insert row into table |
| `select` | `table_name: str, columns: list, where: dict` | `list[dict]` | Select rows from table |
| `update` | `table_name: str, values: dict, where: dict` | `int` | Update rows in table |
| `delete` | `table_name: str, where: dict` | `int` | Delete rows from table |

**Relationships:**
- Composes multiple `Table` objects (1:N)
- Uses utility functions from `utils` module
- Can use `QueryParser` for SQL parsing

---

### Table Class

**Purpose**: Represents a table with schema and data.

**Attributes:**
- `name: str` - Name of the table
- `columns: list[str]` - Ordered list of column names
- `rows: list[dict]` - List of row data as dictionaries

**Methods:**

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `__init__` | `name: str, columns: list[str]` | None | Initialize table |
| `insert` | `values: dict` | `bool` | Insert row |
| `select` | `columns: list, where: dict` | `list[dict]` | Select rows |
| `update` | `values: dict, where: dict` | `int` | Update rows |
| `delete` | `where: dict` | `int` | Delete rows |
| `count` | None | `int` | Count rows |

**Relationships:**
- Contained by `Database` (N:1)
- Contains multiple row dictionaries (1:N)
- Uses utility functions from `utils` module

---

### QueryParser Class

**Purpose**: Parses SQL-like query strings into structured data.

**Methods:**

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `__init__` | None | None | Initialize parser |
| `parse` | `query: str` | `dict` | Parse SQL query |
| `_parse_create_table` | `query: str` | `dict` | Parse CREATE TABLE |
| `_parse_drop_table` | `query: str` | `dict` | Parse DROP TABLE |
| `_parse_insert` | `query: str` | `dict` | Parse INSERT |
| `_parse_select` | `query: str` | `dict` | Parse SELECT |
| `_parse_update` | `query: str` | `dict` | Parse UPDATE |
| `_parse_delete` | `query: str` | `dict` | Parse DELETE |
| `_parse_where` | `where_str: str` | `dict` | Parse WHERE clause |
| `_parse_values_list` | `values_str: str` | `list` | Parse values list |

**Relationships:**
- Used by `Database` or external code
- Uses utility functions from `utils` module

---

### Utils Module

**Purpose**: Provides utility functions for validation, parsing, and comparison.

**Functions:**

| Function | Parameters | Return Type | Description |
|----------|-----------|-------------|-------------|
| `validate_column_name` | `name: str` | `bool` | Validate column name |
| `validate_table_name` | `name: str` | `bool` | Validate table name |
| `parse_value` | `value_str: str` | `any` | Parse string to typed value |
| `format_value` | `value: any` | `str` | Format value for display |
| `compare_values` | `val1: any, operator: str, val2: any` | `bool` | Compare two values |

**Relationships:**
- Used by `Database`, `Table`, and `QueryParser` classes

---

## Sequence Diagrams

### INSERT Operation

```
User → Database: insert(table_name, values)
Database → Database: get_table(table_name)
Database → Table: insert(values)
Table → utils: validate_column_name() [for each column]
Table → Table: rows.append(row)
Table → Database: return True
Database → User: return True
```

### SELECT Operation

```
User → Database: select(table_name, columns, where)
Database → Database: get_table(table_name)
Database → Table: select(columns, where)
Table → Table: for each row in rows
Table → utils: compare_values() [if where clause]
Table → Table: filter and project row
Table → Database: return filtered_rows
Database → User: return filtered_rows
```

### Query Parsing Flow

```
User → QueryParser: parse(query_string)
QueryParser → QueryParser: identify query type
QueryParser → QueryParser: _parse_specific_type()
QueryParser → utils: parse_value() [for values]
QueryParser → User: return parsed_dict
User → Database: execute operation using parsed_dict
```

## Design Patterns Used

### 1. Composite Pattern
- `Database` contains multiple `Table` objects
- `Table` contains multiple row dictionaries
- Allows treating single objects and compositions uniformly

### 2. Strategy Pattern (Implicit)
- `QueryParser` uses different parsing strategies for different query types
- Each query type has its own parsing method

### 3. Data Access Object (DAO) Pattern
- `Database` and `Table` classes act as DAOs
- Provide abstract interface to data storage
- Hide implementation details from users

## Class Interactions

### Creating and Populating a Database

```
┌──────┐                ┌──────────┐              ┌───────┐
│ User │                │ Database │              │ Table │
└───┬──┘                └────┬─────┘              └───┬───┘
    │                        │                        │
    │  Database("mydb")      │                        │
    │───────────────────────>│                        │
    │                        │                        │
    │  create_table(...)     │                        │
    │───────────────────────>│                        │
    │                        │  Table(name, cols)     │
    │                        │───────────────────────>│
    │                        │                        │
    │  insert(table, vals)   │                        │
    │───────────────────────>│                        │
    │                        │  insert(vals)          │
    │                        │───────────────────────>│
    │                        │                        │
```

### Query Execution with Parser

```
┌──────┐      ┌──────────────┐      ┌──────────┐      ┌───────┐
│ User │      │ QueryParser  │      │ Database │      │ Table │
└───┬──┘      └──────┬───────┘      └────┬─────┘      └───┬───┘
    │                │                   │                 │
    │  parse(query)  │                   │                 │
    │───────────────>│                   │                 │
    │                │                   │                 │
    │  parsed_dict   │                   │                 │
    │<───────────────│                   │                 │
    │                │                   │                 │
    │  select(...)   │                   │                 │
    │───────────────────────────────────>│                 │
    │                │                   │  select(...)    │
    │                │                   │────────────────>│
    │                │                   │                 │
    │                │                   │  results        │
    │                │                   │<────────────────│
    │  results       │                   │                 │
    │<───────────────────────────────────│                 │
```

## Extension Points

The design allows for easy extensions:

1. **New Query Types**: Add new `_parse_*` methods to `QueryParser`
2. **Persistence**: Add save/load methods to `Database` class
3. **Indexes**: Add index data structures to `Table` class
4. **Transactions**: Add transaction manager class
5. **Constraints**: Add validation hooks to `Table` methods
6. **Joins**: Add join logic to `Database` class

## Dependencies

```
┌─────────────┐
│   Web App   │
│  (Flask)    │
└──────┬──────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   Database   │────>│    Table     │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │                    │
       ▼                    ▼
┌──────────────┐     ┌──────────────┐
│ QueryParser  │     │    utils     │
└──────────────┘     └──────────────┘
```

## Thread Safety

**Current Implementation**: Not thread-safe
- All operations directly modify internal state
- No locks or synchronization primitives
- Suitable for single-threaded applications only

**For Multi-threading**: Would need:
- Add mutex locks to `Database` and `Table` classes
- Use thread-safe collections
- Implement transaction isolation

## Memory Management

- All data stored in Python data structures (dict, list)
- Garbage collection handles memory cleanup
- No manual memory management required
- Consider memory limits for large datasets

## Performance Characteristics

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `create_table` | O(1) | Dictionary insertion |
| `drop_table` | O(1) | Dictionary deletion |
| `insert` | O(1) | List append |
| `select` (no WHERE) | O(n) | Full table scan |
| `select` (with WHERE) | O(n) | Full table scan with filter |
| `update` | O(n) | Full table scan |
| `delete` | O(n) | Full table scan |

Where n = number of rows in table
