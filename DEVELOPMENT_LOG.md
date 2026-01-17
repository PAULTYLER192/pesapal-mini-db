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

## Commit 3: Add Data Validation to Table.insert() (January 17, 2026)

### What We Implemented
- ✅ Data type validation before insertion
- ✅ Required column validation
- ✅ Comprehensive error messages for validation failures
- ✅ Test suite for validation logic

### User Story
**As a Table**, I need to validate data types before insertion to ensure data integrity.

### Acceptance Criteria Met
1. **Type validation** ✓
   - `insert(data)` method checks input dictionary against `self.schema`
   - Validates each column's data type before saving

2. **TypeError for invalid types** ✓
   - If schema defines `age` as `int` and user provides `"twenty"`, raises `TypeError`
   - Error message includes: column name, expected type, and conversion error details
   - Example: `Column 'age' expects type 'int', cannot convert 'twenty': invalid literal for int() with base 10: 'twenty'`

3. **ValueError for missing columns** ✓
   - If required columns are missing from input, raises `ValueError`
   - Error message lists all missing columns
   - Example: `Missing required columns: age, active`

### Challenges Faced
**Challenge 1: Distinguishing Validation vs Silent Conversion**
- **Problem**: Original `_convert_type()` silently kept original value on conversion failure, making debugging difficult
- **Solution**: 
  - Kept `_convert_type()` for backward compatibility (used in UPDATE operations)
  - Created new `_validate_type()` function that raises `TypeError` on conversion failure
  - INSERT now uses `_validate_type()` for strict validation
  - UPDATE continues using `_convert_type()` for more lenient behavior

**Challenge 2: Meaningful Error Messages**
- **Problem**: Generic type errors don't help users understand what went wrong
- **Solution**: 
  - Error messages include column name, expected type, and actual value
  - Propagate underlying conversion errors (e.g., "invalid literal for int()")
  - Format: `Column '{name}' expects type '{type}', cannot convert '{value}': {details}`

**Challenge 3: Handling Edge Cases**
- **Problem**: What about null values, extra columns, or boolean string conversions?
- **Solution**:
  - Null values (`None`) are allowed for any type - bypass validation
  - Extra columns (not in schema) are allowed and passed through
  - Boolean strings accept flexible formats: "true", "1", "yes", "y" (and lowercase variants)
  - Invalid boolean strings raise `TypeError` with clear message

### Code Changes
**File Modified**: `src/table.py`

**Changes**:
1. Added `_validate_type()` function (lines ~48-68)
   - Strict type validation with error raising
   - Detailed error messages with context
   
2. Updated `insert()` method (lines ~120-143)
   - Added missing column check before type validation
   - Uses `_validate_type()` instead of `_convert_type()`
   - Added docstring documenting exceptions
   
3. Kept `_convert_type()` unchanged for UPDATE operations

**File Created**: `test_validation.py`
- Comprehensive test suite with 6 test cases
- Tests valid insertions, type conversions, error conditions
- Verifies both ValueError and TypeError are raised correctly

### Test Results
✅ **Test 1**: Valid data insertion - PASSED  
✅ **Test 2**: Valid data with type conversion ("25" → 25) - PASSED  
✅ **Test 3**: Invalid type (string "twenty" for int) - PASSED (correctly raises TypeError)  
✅ **Test 4**: Missing required columns - PASSED (correctly raises ValueError)  
✅ **Test 5**: Extra columns allowed - PASSED  
✅ **Test 6**: Null values allowed - PASSED  

### Technical Notes
- Type validation happens **before** saving to JSONL, preventing corrupted data
- Validation is strict on INSERT but could remain lenient on UPDATE if needed
- Error messages follow pattern: `{what failed}` expects `{expected}`, got `{actual}`: `{reason}`
- Boolean type handling is most flexible due to common string representations

### Data Integrity Benefits
1. **Prevention**: Invalid data never reaches storage layer
2. **Early Detection**: Errors caught immediately at insertion time
3. **Clear Feedback**: Detailed error messages help users correct input
4. **Type Safety**: Schema enforcement ensures consistent data types across rows

---

## Next Steps
- [x] Improve error handling and validation
- [ ] Add indexing for faster queries
- [ ] Implement JOIN operations
- [ ] Add transaction support
- [ ] Add unit tests for other operations (UPDATE, DELETE, SELECT)
- [ ] Performance optimization for large datasets
