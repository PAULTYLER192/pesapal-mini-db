# Entity-Relationship Diagram

## Overview

This document describes the entity-relationship model of the Pesapal Mini Database system.

## Core Entities

### 1. Database

**Attributes:**
- `name` (string): The name of the database instance
- `tables` (dict): Collection of tables in the database

**Description:**
The Database entity represents the top-level container for all tables. It manages the lifecycle of tables and provides methods to interact with them.

**Relationships:**
- **HAS-MANY** Tables (1:N relationship)

---

### 2. Table

**Attributes:**
- `name` (string): The name of the table
- `columns` (list): Ordered list of column names
- `rows` (list): Collection of data rows

**Description:**
The Table entity represents a structured collection of data with a fixed schema (columns). Each table belongs to exactly one database.

**Relationships:**
- **BELONGS-TO** Database (N:1 relationship)
- **HAS-MANY** Rows (1:N relationship)

---

### 3. Row

**Attributes:**
- Dynamic attributes based on table schema
- Each column becomes an attribute

**Description:**
A Row represents a single record in a table. Rows are stored as dictionaries with column names as keys.

**Relationships:**
- **BELONGS-TO** Table (N:1 relationship)

---

## ER Diagram (Textual Representation)

```
┌─────────────────────────────────────────┐
│             DATABASE                     │
├─────────────────────────────────────────┤
│ - name: string                          │
│ - tables: dict<string, Table>           │
├─────────────────────────────────────────┤
│ + create_table()                        │
│ + drop_table()                          │
│ + get_table()                           │
│ + list_tables()                         │
│ + insert()                              │
│ + select()                              │
│ + update()                              │
│ + delete()                              │
└─────────────────────────────────────────┘
                │
                │ 1:N
                │ (has many)
                ▼
┌─────────────────────────────────────────┐
│              TABLE                       │
├─────────────────────────────────────────┤
│ - name: string                          │
│ - columns: list<string>                 │
│ - rows: list<dict>                      │
├─────────────────────────────────────────┤
│ + insert()                              │
│ + select()                              │
│ + update()                              │
│ + delete()                              │
│ + count()                               │
└─────────────────────────────────────────┘
                │
                │ 1:N
                │ (has many)
                ▼
┌─────────────────────────────────────────┐
│               ROW                        │
├─────────────────────────────────────────┤
│ - column1: any                          │
│ - column2: any                          │
│ - ...                                   │
│ - columnN: any                          │
└─────────────────────────────────────────┘
```

## Visual ER Diagram

```
                    ┌───────────────┐
                    │   Database    │
                    └───────┬───────┘
                            │
                            │ contains (1:N)
                            │
                    ┌───────▼───────┐
                    │     Table     │
                    └───────┬───────┘
                            │
                            │ stores (1:N)
                            │
                    ┌───────▼───────┐
                    │      Row      │
                    └───────────────┘
```

## Cardinality Details

### Database ↔ Table
- **Cardinality**: 1:N (One-to-Many)
- **Description**: One database can contain multiple tables, but each table belongs to exactly one database
- **Participation**: 
  - Database: Partial (can exist without tables)
  - Table: Total (must belong to a database)

### Table ↔ Row
- **Cardinality**: 1:N (One-to-Many)
- **Description**: One table can contain multiple rows, but each row belongs to exactly one table
- **Participation**:
  - Table: Partial (can exist without rows)
  - Row: Total (must belong to a table)

## Data Flow

### Insert Operation Flow
```
User → Database.insert() → Table.insert() → Row (created)
```

### Select Operation Flow
```
User → Database.select() → Table.select() → Rows (filtered and projected)
```

### Update Operation Flow
```
User → Database.update() → Table.update() → Rows (modified in place)
```

### Delete Operation Flow
```
User → Database.delete() → Table.delete() → Rows (removed)
```

## Example Instance

Here's an example of how entities relate in a real instance:

```
Database: "company_db"
│
├─ Table: "employees"
│  │  columns: [id, name, department, salary]
│  │
│  ├─ Row 1: {id: 1, name: "John", department: "IT", salary: 50000}
│  ├─ Row 2: {id: 2, name: "Jane", department: "HR", salary: 45000}
│  └─ Row 3: {id: 3, name: "Bob", department: "IT", salary: 55000}
│
└─ Table: "departments"
   │  columns: [id, name, budget]
   │
   ├─ Row 1: {id: 1, name: "IT", budget: 200000}
   └─ Row 2: {id: 2, name: "HR", budget: 150000}
```

## Constraints and Rules

### Naming Constraints
- **Table names**: Must start with letter or underscore, contain only alphanumeric characters and underscores
- **Column names**: Same rules as table names
- **Uniqueness**: Table names must be unique within a database

### Data Constraints
- **Schema enforcement**: All rows in a table must have values for all columns
- **Type flexibility**: No type constraints (Python dynamic typing)
- **NULL values**: Supported for any column

### Operational Constraints
- **Atomicity**: Each operation is independent (no transactions)
- **Referential integrity**: Not enforced (no foreign keys)
- **Uniqueness**: Not enforced (no primary keys or unique constraints)

## Query Processing

### WHERE Clause Processing

```
┌──────────────────────┐
│  WHERE Condition     │
├──────────────────────┤
│ - column: string     │
│ - operator: string   │
│ - value: any         │
└──────────────────────┘
         │
         ▼
   Applied to each Row
         │
         ▼
┌──────────────────────┐
│  Filtered Results    │
└──────────────────────┘
```

### Supported Operators
- `=` (Equal)
- `!=` (Not Equal)
- `<` (Less Than)
- `>` (Greater Than)
- `<=` (Less Than or Equal)
- `>=` (Greater Than or Equal)

## Conceptual Model Summary

The Pesapal Mini Database follows a simple hierarchical model:

1. **Database** is the top-level container
2. **Tables** provide structure and schema
3. **Rows** store the actual data

This model is similar to traditional relational databases but simplified:
- No support for relationships between tables (foreign keys)
- No indexes or optimization structures
- All data stored in memory (no persistence layer)
- Dynamic typing instead of strict type definitions

## Use Cases by Entity

### Database Level
- Create/destroy data collections
- Manage multiple independent tables
- Provide namespace isolation

### Table Level
- Define data schema
- Store structured records
- Enforce column consistency

### Row Level
- Store individual data records
- Support CRUD operations
- Enable data retrieval and filtering
