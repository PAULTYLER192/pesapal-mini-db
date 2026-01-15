# SQL Syntax Guide

## Overview

Pesapal Mini Database supports a subset of SQL syntax for common database operations. This guide describes the supported SQL commands and their syntax.

## Supported Commands

### CREATE TABLE

Creates a new table with specified columns.

**Syntax:**
```sql
CREATE TABLE table_name (column1, column2, column3, ...)
```

**Examples:**
```sql
CREATE TABLE users (id, name, email, age)

CREATE TABLE products (id, title, description, price, quantity)

CREATE TABLE orders (order_id, user_id, product_id, quantity, total)
```

**Notes:**
- Table names must start with a letter or underscore
- Table names can contain letters, numbers, and underscores
- Column names follow the same rules as table names
- Semicolon at the end is optional

---

### DROP TABLE

Drops (deletes) an existing table and all its data.

**Syntax:**
```sql
DROP TABLE table_name
```

**Examples:**
```sql
DROP TABLE users

DROP TABLE products;
```

**Notes:**
- This operation cannot be undone
- All data in the table will be permanently deleted

---

### INSERT INTO

Inserts a new row into a table.

**Syntax:**
```sql
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...)
```

**Examples:**
```sql
INSERT INTO users (id, name, email, age) VALUES (1, 'John Doe', 'john@example.com', 30)

INSERT INTO products (id, title, price) VALUES (1, "Widget", 9.99)

INSERT INTO users (id, name, email, age) VALUES (2, 'Jane Smith', 'jane@example.com', NULL)
```

**Value Types:**
- **Integers**: 123, -456
- **Floats**: 3.14, -2.5
- **Strings**: 'text' or "text" (with quotes)
- **Booleans**: TRUE, FALSE (case insensitive)
- **NULL**: NULL (case insensitive)

**Notes:**
- All columns must be specified
- Number of values must match number of columns
- Values must be in the same order as columns

---

### SELECT

Retrieves data from a table.

**Syntax:**
```sql
SELECT column1, column2, ... FROM table_name [WHERE condition]
SELECT * FROM table_name [WHERE condition]
```

**Examples:**

**Select all columns:**
```sql
SELECT * FROM users
```

**Select specific columns:**
```sql
SELECT name, email FROM users

SELECT id, title, price FROM products
```

**Select with WHERE clause:**
```sql
SELECT * FROM users WHERE age = 30

SELECT * FROM users WHERE age > 25

SELECT name, email FROM users WHERE id = 1

SELECT * FROM products WHERE price <= 10.00
```

**WHERE Operators:**
- `=` : Equal to
- `!=` : Not equal to
- `<` : Less than
- `>` : Greater than
- `<=` : Less than or equal to
- `>=` : Greater than or equal to

**Notes:**
- Use `*` to select all columns
- Column names are comma-separated
- WHERE clause is optional

---

### UPDATE

Updates existing rows in a table.

**Syntax:**
```sql
UPDATE table_name SET column1 = value1, column2 = value2, ... [WHERE condition]
```

**Examples:**

**Update with WHERE clause:**
```sql
UPDATE users SET age = 31 WHERE id = 1

UPDATE products SET price = 9.99, quantity = 100 WHERE id = 1

UPDATE users SET email = 'newemail@example.com' WHERE name = 'John Doe'
```

**Update all rows:**
```sql
UPDATE users SET status = 'active'

UPDATE products SET in_stock = TRUE
```

**Notes:**
- Multiple columns can be updated at once (comma-separated)
- Without WHERE clause, all rows will be updated
- Use caution when updating without WHERE clause

---

### DELETE FROM

Deletes rows from a table.

**Syntax:**
```sql
DELETE FROM table_name [WHERE condition]
```

**Examples:**

**Delete with WHERE clause:**
```sql
DELETE FROM users WHERE id = 1

DELETE FROM products WHERE price > 100

DELETE FROM orders WHERE status = 'cancelled'
```

**Delete all rows:**
```sql
DELETE FROM users
```

**Notes:**
- Without WHERE clause, all rows will be deleted
- The table structure remains intact
- Use caution when deleting without WHERE clause

---

## General Syntax Rules

### Case Sensitivity
- SQL keywords (SELECT, FROM, WHERE, etc.) are **case insensitive**
- Table names and column names are **case sensitive**

```sql
-- These are all valid:
SELECT * FROM users
select * from users
SeLeCt * FrOm users
```

### Whitespace
- Extra spaces are allowed and ignored
- Queries can span multiple lines

```sql
SELECT   name,   email
FROM     users
WHERE    age  >  25
```

### Semicolons
- Semicolons at the end of queries are optional
- Both work the same:

```sql
SELECT * FROM users
SELECT * FROM users;
```

### String Literals
- Use single quotes `'text'` or double quotes `"text"`
- Both are equivalent

```sql
INSERT INTO users (id, name) VALUES (1, 'John')
INSERT INTO users (id, name) VALUES (1, "John")
```

---

## Query Examples by Use Case

### Creating a Simple Database

```sql
-- Create tables
CREATE TABLE users (id, username, email, created_at)
CREATE TABLE posts (id, user_id, title, content, likes)

-- Insert users
INSERT INTO users (id, username, email, created_at) VALUES (1, 'john_doe', 'john@example.com', '2024-01-15')
INSERT INTO users (id, username, email, created_at) VALUES (2, 'jane_smith', 'jane@example.com', '2024-01-16')

-- Insert posts
INSERT INTO posts (id, user_id, title, content, likes) VALUES (1, 1, 'First Post', 'Hello World!', 10)
INSERT INTO posts (id, user_id, title, content, likes) VALUES (2, 1, 'Second Post', 'Learning SQL', 25)
```

### Querying Data

```sql
-- Get all users
SELECT * FROM users

-- Get specific user information
SELECT username, email FROM users WHERE id = 1

-- Get popular posts
SELECT * FROM posts WHERE likes > 15

-- Get all posts by a user
SELECT title, content FROM posts WHERE user_id = 1
```

### Updating Data

```sql
-- Update user email
UPDATE users SET email = 'newemail@example.com' WHERE id = 1

-- Increment post likes
UPDATE posts SET likes = 26 WHERE id = 2

-- Update multiple columns
UPDATE users SET username = 'john_doe_updated', email = 'updated@example.com' WHERE id = 1
```

### Deleting Data

```sql
-- Delete a specific post
DELETE FROM posts WHERE id = 1

-- Delete posts with no likes
DELETE FROM posts WHERE likes = 0

-- Delete all posts by a user
DELETE FROM posts WHERE user_id = 2
```

### Cleaning Up

```sql
-- Remove all data from a table
DELETE FROM posts

-- Remove the table entirely
DROP TABLE posts
```

---

## Limitations

The following SQL features are **NOT supported**:

- JOINs between tables
- Subqueries
- Aggregate functions (COUNT, SUM, AVG, etc.)
- GROUP BY and HAVING clauses
- ORDER BY and LIMIT clauses
- Indexes
- Transactions
- Data types (all values are dynamically typed)
- Constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL)
- ALTER TABLE
- Multiple WHERE conditions (AND, OR operators)
- IN, LIKE, BETWEEN operators

For these advanced features, consider using a full SQL database like SQLite, PostgreSQL, or MySQL.

---

## Error Messages

Common error messages and their meanings:

- **"Invalid table name"**: Table name doesn't follow naming rules
- **"Table already exists"**: Attempting to create a table that already exists
- **"Table does not exist"**: Attempting to access a non-existent table
- **"Unknown column"**: Column name is not in the table
- **"Missing columns"**: INSERT is missing required columns
- **"Invalid syntax"**: Query doesn't follow proper SQL syntax
- **"Unknown operator"**: WHERE clause uses an unsupported operator
