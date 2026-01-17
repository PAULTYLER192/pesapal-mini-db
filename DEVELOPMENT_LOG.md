# Development Log - Pesapal Mini DB

This document tracks all implementations, challenges faced, and solutions applied throughout the project development.

---

## Commit 1: Initial Project Setup (January 17, 2026)

### What We Implemented
- ✅ Basic project structure with Flask web UI
- ✅ Mini RDBMS implementation using JSONL for storage
- ✅ Database class for managing multiple tables
- ✅ Parser for SQL-like commands
- ✅ REPL interface (`main.py`)
- ✅ Web interface using Flask (`app/app.py`)
- ✅ Environment variable support with `.env` file

### Features Implemented
1. **Table Class** (`src/table.py`)
   - JSONL-backed storage
   - Schema support with type conversion (str, int, float, bool)
   - CRUD operations: INSERT, SELECT, UPDATE, DELETE
   - Basic WHERE clause filtering

2. **Database Class** (`src/database.py`)
   - Table creation and management
   - Metadata storage in JSON files
   - SQL-like command execution
   - SHOW TABLES and DESCRIBE commands

3. **Parser** (`src/parser.py`)
   - SQL-like query parsing
   - Support for CREATE TABLE, INSERT INTO, SELECT, UPDATE, DELETE, DROP TABLE

4. **Web UI** (`app/app.py`)
   - Flask-based interface
   - Create tables via web form
   - Insert records with JSON input
   - View table data
   - Execute SQL-like queries

### Challenges Faced
**Challenge 1: Secret Key Security**
- **Problem**: Flask secret key was hardcoded in source code, posing a security risk if pushed to git
- **Solution**: 
  - Implemented `.env` file support using `python-dotenv`
  - Created `.env.example` as a template
  - Updated `.gitignore` to exclude `.env` from version control
  - Modified `app.py` to load secret key from environment variables with fallback

**Challenge 2: Python-specific .gitignore**
- **Problem**: Repository had AL/Dynamics 365 `.gitignore` template, not suitable for Python
- **Solution**: Replaced with comprehensive Python `.gitignore` including:
  - `__pycache__/` and compiled Python files
  - Virtual environment folders
  - `.env` file
  - IDE-specific files
  - OS-specific files

### Technical Decisions
- **JSONL Format**: Chosen for simple line-by-line append operations and easy debugging
- **Metadata Separation**: Table schemas stored separately in `metadata/` directory for quick access
- **Type System**: Basic type conversion supporting str, int, float, bool
- **Flask for UI**: Lightweight framework suitable for demo purposes

---

## Commit 2: Refactor Table Class to Match Acceptance Criteria (January 17, 2026)

### What We Implemented
- ✅ Refactored Table class with explicit `_load_rows()` and `_save_row()` methods
- ✅ Clearer separation of concerns for read/write operations
- ✅ Auto-creation of JSONL files if they don't exist

### Acceptance Criteria Met
1. **Table class accepts name and schema** ✓
   - Constructor takes `name: str`, `schema: Dict[str, Any]`, and `data_dir: str`

2. **`_load_rows()` method** ✓
   - Reads line-by-line from `data/{name}.jsonl`
   - Parses each line as JSON
   - Returns `List[Dict[str, Any]]`
   - Handles corrupted lines gracefully

3. **`_save_row(row_dict)` method** ✓
   - Appends a single JSON string to `data/{name}.jsonl`
   - Ensures proper newline separation

4. **Auto-create constraint** ✓
   - If file doesn't exist, creates it automatically in `__init__`
   - Creates parent directories if needed using `os.makedirs()`

### Challenges Faced
**Challenge 1: Method Naming Clarity**
- **Problem**: Original implementation had `_read_all()` which didn't clearly communicate the line-by-line reading requirement
- **Solution**: 
  - Renamed to `_load_rows()` to better match acceptance criteria
  - Added clear docstring: "Read line-by-line from data/{name}.jsonl"
  - Kept implementation unchanged (was already reading line-by-line)

**Challenge 2: Single Row vs Bulk Write**
- **Problem**: Needed both single-row append and bulk rewrite capabilities
- **Solution**:
  - `_save_row()` - appends single row (used by INSERT)
  - `_write_all()` - rewrites entire file (used by UPDATE/DELETE for consistency)
  - This provides flexibility for different operation types

### Code Changes
- **File Modified**: `src/table.py`
- **Changes**:
  - `_read_all()` → `_load_rows()` (renamed for clarity)
  - Added explicit `_save_row(row_dict)` method
  - Updated `insert()` to use `_save_row()`
  - Updated `select()`, `update()`, `delete()` to use `_load_rows()`

### Technical Notes
- JSONL format allows efficient append operations without reading entire file
- Line-by-line reading prevents memory issues with large datasets
- File auto-creation uses `os.makedirs(exist_ok=True)` for directory creation
- UTF-8 encoding ensures proper handling of international characters

---

## Next Steps
- [ ] Add indexing for faster queries
- [ ] Implement JOIN operations
- [ ] Add transaction support
- [ ] Improve error handling and validation
- [ ] Add unit tests
- [ ] Performance optimization for large datasets
