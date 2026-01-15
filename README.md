# Mini Database

A lightweight, SQL-based mini database system implemented in Python. Features a CLI REPL interface and a web-based UI for executing SQL commands and managing data.

## 🌟 Features

- **SQL Command Support**: CREATE, INSERT, SELECT, UPDATE, DELETE, DROP operations
- **Multiple Data Types**: TEXT, INTEGER, FLOAT, BOOLEAN
- **Two Interfaces**: 
  - Command-line REPL for interactive SQL execution
  - Web UI for browser-based database management
- **Simple Storage**: 
  - Data stored in `.jsonl` files (JSON Lines format)
  - Schemas stored in JSON format
- **WHERE Clause Support**: Filter data with conditions (`=`, `!=`, `>`, `<`, `>=`, `<=`)

## 📁 Project Structure

```
pesapal-mini-db/
├── data/                 # Table data (.jsonl files)
├── metadata/             # Table schemas (.json files)
├── src/                  # Core database logic
│   ├── database.py       # Database manager
│   ├── table.py          # Table CRUD engine
│   └── parser.py         # SQL string parser
├── app/                  # Flask web application
│   ├── app.py            # Flask app
│   └── templates/
│       └── index.html    # Web UI
├── main.py               # CLI REPL
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/PAULTYLER192/pesapal-mini-db.git
   cd pesapal-mini-db
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

### CLI REPL

Run the interactive command-line interface:

```bash
python main.py
```

Example session:
```sql
minidb> CREATE TABLE users (name TEXT, age INTEGER, email TEXT)
Table 'users' created successfully

minidb> INSERT INTO users VALUES ('Alice', 30, 'alice@example.com')
Inserted 1 row into 'users'

minidb> SELECT * FROM users
name  | age | email
--------------------------
Alice | 30  | alice@example.com

(1 row(s))

minidb> UPDATE users SET age=31 WHERE name='Alice'
Updated 1 row(s) in 'users'

minidb> DELETE FROM users WHERE age>30
Deleted 1 row(s) from 'users'

minidb> DROP TABLE users
Table 'users' dropped successfully

minidb> exit
Goodbye!
```

### Web UI

1. **Start the Flask server**:
   ```bash
   python app/app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Use the web interface** to:
   - Execute SQL commands
   - View query results in formatted tables
   - Browse existing tables
   - View table schemas

## 📖 SQL Commands Reference

### CREATE TABLE
Create a new table with specified columns and types:
```sql
CREATE TABLE table_name (column1 TYPE1, column2 TYPE2, ...)
```

**Supported Types**: `TEXT`, `INTEGER`, `FLOAT`, `BOOLEAN`

**Example**:
```sql
CREATE TABLE products (id INTEGER, name TEXT, price FLOAT, available BOOLEAN)
```

### INSERT INTO
Insert a new row into a table:
```sql
INSERT INTO table_name VALUES (value1, value2, ...)
```

**Example**:
```sql
INSERT INTO products VALUES (1, 'Laptop', 999.99, TRUE)
```

### SELECT
Retrieve data from a table:
```sql
SELECT * FROM table_name [WHERE condition]
SELECT column1, column2 FROM table_name [WHERE condition]
```

**Examples**:
```sql
SELECT * FROM products
SELECT name, price FROM products WHERE price > 500
SELECT * FROM products WHERE available = TRUE
```

### UPDATE
Modify existing rows:
```sql
UPDATE table_name SET column=value [WHERE condition]
```

**Example**:
```sql
UPDATE products SET price=899.99 WHERE id=1
```

### DELETE
Remove rows from a table:
```sql
DELETE FROM table_name [WHERE condition]
```

**Examples**:
```sql
DELETE FROM products WHERE id=1
DELETE FROM products WHERE available=FALSE
```

### DROP TABLE
Delete a table and all its data:
```sql
DROP TABLE table_name
```

**Example**:
```sql
DROP TABLE products
```

### Special Commands (CLI Only)

- `SHOW TABLES` - List all tables in the database
- `DESCRIBE table_name` - Display the schema of a table
- `help` - Show help information
- `exit` or `quit` - Exit the REPL

## 🔧 Architecture

### Components

1. **SQL Parser** (`src/parser.py`):
   - Parses SQL strings into structured commands
   - Uses regex patterns to match SQL syntax
   - Validates SQL structure and extracts components

2. **Table Engine** (`src/table.py`):
   - Handles CRUD operations for individual tables
   - Manages data persistence to `.jsonl` files
   - Validates data types and schema constraints
   - Evaluates WHERE clause conditions

3. **Database Manager** (`src/database.py`):
   - Coordinates all database operations
   - Manages table lifecycle (create, drop, list)
   - Executes parsed SQL commands
   - Provides unified interface for CLI and web UI

4. **CLI REPL** (`main.py`):
   - Interactive command-line interface
   - Formats query results as tables
   - Provides help and special commands

5. **Web UI** (`app/app.py` + `templates/index.html`):
   - Flask-based web application
   - REST API for SQL execution
   - Modern, responsive user interface
   - Real-time query results display

### Data Storage

- **Data Files** (`data/*.jsonl`): Each table has a `.jsonl` file where each line is a JSON object representing a row
- **Metadata Files** (`metadata/*.json`): Each table has a JSON file storing its schema (column names and types)

## 🎯 Example Use Cases

### Creating a Simple Task Manager

```sql
-- Create tasks table
CREATE TABLE tasks (id INTEGER, title TEXT, completed BOOLEAN)

-- Add tasks
INSERT INTO tasks VALUES (1, 'Buy groceries', FALSE)
INSERT INTO tasks VALUES (2, 'Write report', FALSE)
INSERT INTO tasks VALUES (3, 'Call dentist', TRUE)

-- View all tasks
SELECT * FROM tasks

-- View incomplete tasks
SELECT * FROM tasks WHERE completed=FALSE

-- Mark task as complete
UPDATE tasks SET completed=TRUE WHERE id=1

-- Delete completed tasks
DELETE FROM tasks WHERE completed=TRUE
```

### Managing a Product Inventory

```sql
-- Create inventory table
CREATE TABLE inventory (product_id INTEGER, product_name TEXT, quantity INTEGER, price FLOAT)

-- Add products
INSERT INTO inventory VALUES (101, 'Widget A', 50, 19.99)
INSERT INTO inventory VALUES (102, 'Widget B', 30, 29.99)
INSERT INTO inventory VALUES (103, 'Widget C', 0, 39.99)

-- Check low stock items
SELECT * FROM inventory WHERE quantity < 10

-- Update stock
UPDATE inventory SET quantity=60 WHERE product_id=101

-- View expensive items
SELECT product_name, price FROM inventory WHERE price > 25
```

## 🛠️ Development

### Running Tests

Currently, the project doesn't include automated tests, but you can manually test by:

1. Running the CLI and executing various SQL commands
2. Starting the web UI and testing through the browser interface
3. Verifying data persistence by restarting the application

### Adding New Features

The modular architecture makes it easy to extend:

- Add new SQL commands in `src/parser.py`
- Implement new operations in `src/table.py`
- Update `src/database.py` to handle new command types
- Enhance the UI in `app/templates/index.html`

## 📝 Limitations

- Single-user access (no concurrent access control)
- Limited SQL syntax support (no JOINs, subqueries, etc.)
- Simple WHERE clauses (no AND/OR logic)
- No indexing or query optimization
- No transaction support
- No authentication/authorization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 👤 Author

**Paul Tyler**

---

Made with ❤️ for learning and demonstration purposes.