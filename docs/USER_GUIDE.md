# User Guide

## Introduction

Welcome to Pesapal Mini Database! This is a lightweight, in-memory database with SQL-like query support, designed for educational purposes and simple data management tasks.

## Features

- **In-Memory Storage**: Fast operations with data stored in memory
- **SQL-Like Syntax**: Familiar SQL commands for database operations
- **Python API**: Direct Python API for programmatic access
- **Web Interface**: User-friendly web UI for interactive queries
- **Zero Configuration**: No setup required, just import and use
- **Lightweight**: Minimal dependencies (Flask for web app, pytest for testing)

## Installation

### Requirements

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone or download the repository:
```bash
git clone https://github.com/PAULTYLER192/pesapal-mini-db.git
cd pesapal-mini-db
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

That's it! No database server to install or configure.

## Usage

### Option 1: Python API

Use the database directly in your Python code.

```python
from src.db import Database

# Create a database
db = Database("my_app_db")

# Create a table
db.create_table('users', ['id', 'name', 'email', 'age'])

# Insert data
db.insert('users', {
    'id': 1,
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30
})

# Query data
users = db.select('users')
print(users)

# Query with filter
adult_users = db.select('users', where={
    'column': 'age',
    'operator': '>=',
    'value': 18
})
print(adult_users)

# Update data
db.update('users', {'age': 31}, where={
    'column': 'id',
    'operator': '=',
    'value': 1
})

# Delete data
db.delete('users', where={
    'column': 'id',
    'operator': '=',
    'value': 1
})
```

### Option 2: SQL-Like Queries

Use SQL-like syntax with the query parser.

```python
from src.db import Database
from src.parser import QueryParser

db = Database()
parser = QueryParser()

# Parse and execute queries
queries = [
    "CREATE TABLE products (id, name, price, stock)",
    "INSERT INTO products (id, name, price, stock) VALUES (1, 'Widget', 9.99, 100)",
    "SELECT * FROM products WHERE price < 10",
    "UPDATE products SET stock = 95 WHERE id = 1",
    "DELETE FROM products WHERE stock = 0"
]

for query in queries:
    parsed = parser.parse(query)
    # Execute based on parsed['type']
    print(f"Executed: {query}")
```

### Option 3: Web Interface

Launch the web application for an interactive experience.

```bash
cd web_app
python app.py
```

Then open your browser to `http://127.0.0.1:5000`

The web interface provides:
- Visual table browser
- SQL query editor
- Real-time results display
- Quick example queries
- Error handling and validation

## Quick Start Tutorial

### Step 1: Create Your First Table

```python
from src.db import Database

db = Database("tutorial_db")

# Create a table for storing books
db.create_table('books', ['id', 'title', 'author', 'year', 'rating'])
```

### Step 2: Add Some Data

```python
# Add books
db.insert('books', {
    'id': 1,
    'title': 'The Python Tutorial',
    'author': 'Guido van Rossum',
    'year': 2020,
    'rating': 4.5
})

db.insert('books', {
    'id': 2,
    'title': 'Database Systems',
    'author': 'Abraham Silberschatz',
    'year': 2019,
    'rating': 4.8
})

db.insert('books', {
    'id': 3,
    'title': 'Clean Code',
    'author': 'Robert Martin',
    'year': 2008,
    'rating': 4.7
})
```

### Step 3: Query Your Data

```python
# Get all books
all_books = db.select('books')
print(f"All books: {all_books}")

# Get only titles and authors
books_info = db.select('books', columns=['title', 'author'])
print(f"Books info: {books_info}")

# Get highly rated books
top_books = db.select('books', where={
    'column': 'rating',
    'operator': '>',
    'value': 4.6
})
print(f"Top rated books: {top_books}")

# Get recent books
recent_books = db.select('books', where={
    'column': 'year',
    'operator': '>=',
    'value': 2019
})
print(f"Recent books: {recent_books}")
```

### Step 4: Update Data

```python
# Update a book's rating
db.update('books', {'rating': 5.0}, where={
    'column': 'id',
    'operator': '=',
    'value': 1
})

print("Rating updated!")
```

### Step 5: Delete Data

```python
# Delete old books
count = db.delete('books', where={
    'column': 'year',
    'operator': '<',
    'value': 2010
})

print(f"Deleted {count} old books")
```

## Common Use Cases

### 1. Simple Cache

```python
from src.db import Database

cache = Database("cache_db")
cache.create_table('cache', ['key', 'value', 'timestamp'])

# Store value
import time
cache.insert('cache', {
    'key': 'user_123',
    'value': '{"name": "John", "email": "john@example.com"}',
    'timestamp': time.time()
})

# Retrieve value
result = cache.select('cache', where={
    'column': 'key',
    'operator': '=',
    'value': 'user_123'
})
```

### 2. Configuration Storage

```python
db = Database("config_db")
db.create_table('settings', ['key', 'value', 'description'])

# Store settings
settings = [
    {'key': 'theme', 'value': 'dark', 'description': 'UI theme'},
    {'key': 'language', 'value': 'en', 'description': 'Interface language'},
    {'key': 'notifications', 'value': 'true', 'description': 'Enable notifications'}
]

for setting in settings:
    db.insert('settings', setting)

# Retrieve setting
theme = db.select('settings', where={
    'column': 'key',
    'operator': '=',
    'value': 'theme'
})
```

### 3. Simple TODO Application

```python
db = Database("todo_db")
db.create_table('todos', ['id', 'task', 'status', 'priority', 'created_at'])

# Add tasks
import datetime

db.insert('todos', {
    'id': 1,
    'task': 'Write documentation',
    'status': 'completed',
    'priority': 'high',
    'created_at': str(datetime.datetime.now())
})

db.insert('todos', {
    'id': 2,
    'task': 'Review pull requests',
    'status': 'pending',
    'priority': 'medium',
    'created_at': str(datetime.datetime.now())
})

# Get pending tasks
pending = db.select('todos', where={
    'column': 'status',
    'operator': '=',
    'value': 'pending'
})

# Mark task as completed
db.update('todos', {'status': 'completed'}, where={
    'column': 'id',
    'operator': '=',
    'value': 2
})
```

## Best Practices

### 1. Data Types

While the database doesn't enforce types, be consistent:

```python
# Good: Consistent types
db.insert('users', {'id': 1, 'name': 'John', 'age': 30})
db.insert('users', {'id': 2, 'name': 'Jane', 'age': 25})

# Avoid: Inconsistent types
db.insert('users', {'id': 1, 'name': 'John', 'age': 30})
db.insert('users', {'id': '2', 'name': 'Jane', 'age': '25'})  # Different types
```

### 2. Naming Conventions

Use clear, descriptive names:

```python
# Good
db.create_table('user_accounts', ['user_id', 'username', 'email'])

# Less clear
db.create_table('tbl1', ['c1', 'c2', 'c3'])
```

### 3. Error Handling

Always handle potential errors:

```python
try:
    db.create_table('users', ['id', 'name'])
    db.insert('users', {'id': 1, 'name': 'John'})
except ValueError as e:
    print(f"Error: {e}")
```

### 4. Resource Management

Remember that data is stored in memory:

```python
# For large datasets, consider:
# - Limiting query results
# - Periodically clearing old data
# - Using proper database for production

# Clear old cache entries
old_timestamp = time.time() - 3600  # 1 hour ago
db.delete('cache', where={
    'column': 'timestamp',
    'operator': '<',
    'value': old_timestamp
})
```

## Limitations to Consider

1. **In-Memory Only**: Data is lost when the program exits
2. **No Persistence**: Use this for temporary/session data only
3. **Single Thread**: Not suitable for concurrent access
4. **No Transactions**: Operations are not atomic
5. **Limited SQL**: Only basic SQL commands supported
6. **No Joins**: Can't join multiple tables
7. **No Indexing**: All queries are full table scans

For production applications with these requirements, use SQLite, PostgreSQL, or MySQL.

## Testing

Run the test suite to verify everything works:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_database.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

## Troubleshooting

### Import Error

If you get import errors:
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### Flask Not Found

Install Flask:
```bash
pip install Flask
```

### Tests Not Found

Install pytest:
```bash
pip install pytest
```

## Getting Help

- Check the [API Documentation](API.md) for detailed API reference
- Review [SQL Syntax Guide](SQL_SYNTAX.md) for query syntax
- Look at the test files in `tests/` for more examples
- Examine the web app code in `web_app/app.py` for Flask integration

## Contributing

Contributions are welcome! Areas for improvement:
- Add more SQL operators (LIKE, IN, BETWEEN)
- Support for ORDER BY and LIMIT
- Basic JOIN support
- File persistence option
- More comprehensive error messages

## License

See LICENSE file for details.
