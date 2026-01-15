# Pesapal Mini Database 🗄️

A lightweight, in-memory database with SQL-like query support, built in Python. Perfect for educational purposes, prototyping, and simple data management tasks.

## Features

✨ **Simple & Intuitive**: Easy-to-use Python API and SQL-like syntax  
🚀 **Zero Configuration**: No setup or installation of database servers  
💾 **In-Memory Storage**: Fast operations with data stored in RAM  
🌐 **Web Interface**: Beautiful Flask-based UI for interactive queries  
🧪 **Well-Tested**: Comprehensive test suite with pytest  
📚 **Documented**: Extensive documentation and examples  

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/PAULTYLER192/pesapal-mini-db.git
cd pesapal-mini-db

# Install dependencies
pip install -r requirements.txt
```

### Python API Usage

```python
from src.db import Database

# Create a database
db = Database("my_app")

# Create a table
db.create_table('users', ['id', 'name', 'email', 'age'])

# Insert data
db.insert('users', {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'age': 30})
db.insert('users', {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'age': 25})

# Query data
all_users = db.select('users')
print(all_users)

# Query with filter
adults = db.select('users', where={'column': 'age', 'operator': '>=', 'value': 18})
print(adults)

# Update data
db.update('users', {'age': 31}, where={'column': 'id', 'operator': '=', 'value': 1})

# Delete data
db.delete('users', where={'column': 'id', 'operator': '=', 'value': 2})
```

### SQL-Like Query Usage

```python
from src.db import Database
from src.parser import QueryParser

db = Database()
parser = QueryParser()

# Parse and execute queries
query = "CREATE TABLE products (id, name, price, stock)"
parsed = parser.parse(query)
db.create_table(parsed['table'], parsed['columns'])

query = "INSERT INTO products (id, name, price, stock) VALUES (1, 'Widget', 9.99, 100)"
parsed = parser.parse(query)
db.insert(parsed['table'], parsed['values'])

query = "SELECT * FROM products WHERE price < 10"
parsed = parser.parse(query)
results = db.select(parsed['table'], parsed['columns'], parsed['where'])
print(results)
```

### Web Interface

```bash
cd web_app
python app.py
```

Then open your browser to `http://127.0.0.1:5000`

![Web Interface](https://img.shields.io/badge/Web-Interface-blue)

## Project Structure

```
pesapal-mini-db/
├── src/                      # Core database engine
│   ├── __init__.py          # Package initialization
│   ├── db.py                # Database class
│   ├── table.py             # Table class
│   ├── parser.py            # SQL-like query parser
│   └── utils.py             # Utility functions
├── web_app/                  # Flask web application
│   ├── app.py               # Flask application
│   ├── templates/           # HTML templates
│   │   └── index.html       # Main UI
│   └── static/              # Static files
│       ├── css/
│       │   └── style.css    # Styles
│       └── js/
│           └── app.js       # Frontend JavaScript
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_database.py     # Database tests
│   ├── test_table.py        # Table tests
│   ├── test_parser.py       # Parser tests
│   └── test_utils.py        # Utility tests
├── docs/                     # Documentation
│   ├── API.md               # API documentation
│   ├── SQL_SYNTAX.md        # SQL syntax guide
│   ├── USER_GUIDE.md        # User guide
│   ├── ER_DIAGRAM.md        # Entity-relationship diagram
│   └── CLASS_DIAGRAM.md     # Class diagram
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── LICENSE                  # License information
└── .gitignore              # Git ignore rules
```

## Supported SQL Commands

### CREATE TABLE
```sql
CREATE TABLE users (id, name, email, age)
```

### DROP TABLE
```sql
DROP TABLE users
```

### INSERT INTO
```sql
INSERT INTO users (id, name, email, age) VALUES (1, 'John Doe', 'john@example.com', 30)
```

### SELECT
```sql
SELECT * FROM users
SELECT name, email FROM users
SELECT * FROM users WHERE age > 25
```

### UPDATE
```sql
UPDATE users SET age = 31 WHERE id = 1
UPDATE users SET status = 'active'
```

### DELETE FROM
```sql
DELETE FROM users WHERE id = 1
DELETE FROM users
```

## Documentation

📖 **[User Guide](docs/USER_GUIDE.md)** - Getting started and tutorials  
📋 **[API Documentation](docs/API.md)** - Complete API reference  
💬 **[SQL Syntax Guide](docs/SQL_SYNTAX.md)** - SQL command syntax  
📊 **[ER Diagram](docs/ER_DIAGRAM.md)** - Entity-relationship model  
🏗️ **[Class Diagram](docs/CLASS_DIAGRAM.md)** - Architecture and design  

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_database.py

# Run with coverage
pytest tests/ --cov=src
```

## Examples

### Simple Cache

```python
from src.db import Database
import time

cache = Database("cache")
cache.create_table('cache', ['key', 'value', 'timestamp'])

# Store value
cache.insert('cache', {
    'key': 'user_123',
    'value': '{"name": "John"}',
    'timestamp': time.time()
})

# Retrieve value
result = cache.select('cache', where={'column': 'key', 'operator': '=', 'value': 'user_123'})
```

### TODO Application

```python
from src.db import Database

db = Database("todos")
db.create_table('tasks', ['id', 'task', 'status', 'priority'])

# Add tasks
db.insert('tasks', {'id': 1, 'task': 'Write docs', 'status': 'done', 'priority': 'high'})
db.insert('tasks', {'id': 2, 'task': 'Review PRs', 'status': 'pending', 'priority': 'medium'})

# Get pending tasks
pending = db.select('tasks', where={'column': 'status', 'operator': '=', 'value': 'pending'})

# Mark task as done
db.update('tasks', {'status': 'done'}, where={'column': 'id', 'operator': '=', 'value': 2})
```

## Limitations

⚠️ This is a lightweight, educational database. It has some limitations:

- **In-Memory Only**: Data is lost when the program exits
- **No Persistence**: Not suitable for production data storage
- **Single-Threaded**: Not designed for concurrent access
- **No Transactions**: Operations are not atomic
- **Limited SQL**: Only basic SQL commands supported
- **No Joins**: Cannot join multiple tables
- **No Indexes**: All queries are full table scans

For production applications, consider using SQLite, PostgreSQL, or MySQL.

## Contributing

Contributions are welcome! Here are some areas for improvement:

- [ ] Add file persistence (save/load to disk)
- [ ] Support for ORDER BY and LIMIT clauses
- [ ] Basic JOIN support between tables
- [ ] Add more operators (LIKE, IN, BETWEEN)
- [ ] Implement transactions
- [ ] Add indexes for faster queries
- [ ] Support for aggregate functions (COUNT, SUM, AVG)
- [ ] Better error messages and validation

## Requirements

- Python 3.7+
- Flask 3.0.0
- pytest 7.4.3

## License

See [LICENSE](LICENSE) file for details.

## Author

PAULTYLER192

## Acknowledgments

Built as part of a technical assessment for Pesapal.

---

**⭐ Star this repository if you find it useful!**