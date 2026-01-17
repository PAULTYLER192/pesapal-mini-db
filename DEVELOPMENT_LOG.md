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

## Commit 4: Implement Primary Key Indexing for O(1) Lookups (January 17, 2026)

### What We Implemented
- ✅ Primary key enforcement with in-memory indexing
- ✅ Duplicate key detection
- ✅ Fast `select_by_id()` method with O(1) complexity
- ✅ Index consistency maintenance across CRUD operations
- ✅ Custom `DuplicateKeyError` exception

### User Story
**As a Table**, I need to enforce Primary Keys and support fast lookups to enable efficient data retrieval.

### Acceptance Criteria Met
1. **Primary key index dictionary** ✓
   - `self.index = {}` maintains mapping of primary key values to row data
   - Built on initialization if primary key is defined
   - Automatically rebuilt from JSONL file

2. **Duplicate key detection** ✓
   - `insert()` checks if primary key value exists in `self.index`
   - Raises `DuplicateKeyError` with descriptive message if duplicate found
   - Example: `Duplicate primary key 'id=1' already exists`

3. **O(1) lookup with select_by_id()** ✓
   - Dictionary lookup: `self.index.get(pk_value)`
   - Returns row data directly from index
   - No sequential scanning of JSONL file
   - Raises `ValueError` if table has no primary key

### Key Features
1. **Optional Primary Key**
   - Constructor parameter: `primary_key: Optional[str] = None`
   - If not specified, table operates without indexing
   - Can be added when Table is instantiated

2. **Index Maintenance**
   - **INSERT**: Adds new entry to index after validation
   - **UPDATE**: Removes old PK entry, adds new entry if PK is modified
   - **DELETE**: Removes PK entry from index
   - **Full Rebuild**: `_rebuild_index()` reconstructs index from JSONL file

3. **Exception Handling**
   - Custom `DuplicateKeyError` exception for constraint violations
   - Clear error messages indicating which PK value caused the conflict
   - `ValueError` if `select_by_id()` called on table without PK

### Challenges Faced
**Challenge 1: Index Consistency on UPDATE**
- **Problem**: If primary key value is updated, need to update index mapping
- **Solution**: 
  - Check if `primary_key` is in `set_values`
  - Store old PK value before modification
  - Remove old entry, add new entry to index
  - Handles both PK and non-PK column updates

**Challenge 2: Index Consistency on DELETE**
- **Problem**: Deleting rows must remove their entries from index
- **Solution**:
  - Before writing updated file, remove deleted row's PK from index
  - Ensures index always reflects actual data

**Challenge 3: Initial Index Population**
- **Problem**: Table created with existing JSONL file needs index built
- **Solution**:
  - `_rebuild_index()` called in `__init__` if primary key defined
  - Reads all rows and populates index
  - Handles corrupted/missing files gracefully

### Code Changes
**File Modified**: `src/table.py`

**Changes**:
1. Added `DuplicateKeyError` exception class (line ~6-8)

2. Updated `Table.__init__()` (line ~94-127)
   - Added `primary_key: Optional[str] = None` parameter
   - Initialize `self.index: Dict[Any, Dict[str, Any]] = {}`
   - Call `_rebuild_index()` if primary key defined

3. Added `_rebuild_index()` method (line ~129-140)
   - Clears existing index
   - Iterates through all rows
   - Populates index with PK -> row mappings

4. Updated `insert()` method (line ~142-177)
   - Check for duplicate keys before saving
   - Update index after successful insert
   - Raise `DuplicateKeyError` for duplicates

5. Added `select_by_id()` method (line ~179-195)
   - Takes primary key value as parameter
   - Returns `self.index.get(pk_value)` for O(1) lookup
   - Raises `ValueError` if no primary key defined

6. Updated `update()` method (line ~221-251)
   - Handles PK value changes
   - Maintains index consistency
   - Removes old entry, adds new if PK changed

7. Updated `delete()` method (line ~253-271)
   - Removes deleted rows from index
   - Maintains consistency before writing to file

**File Created**: `test_primary_key.py`
- 10 comprehensive test cases
- Tests insertion, duplicate detection, lookups
- Performance comparison: index vs sequential scan

### Test Results
✅ **Test 1**: Insert unique primary keys - PASSED  
✅ **Test 2**: Duplicate PK detection - PASSED (raises DuplicateKeyError)  
✅ **Test 3**: select_by_id() retrieval - PASSED  
✅ **Test 4**: select_by_id() not found - PASSED (returns None)  
✅ **Test 5**: Table without PK - PASSED (raises ValueError)  
✅ **Test 6**: DELETE maintains index - PASSED  
✅ **Test 7**: Re-insert deleted PK - PASSED  
✅ **Test 8**: UPDATE maintains index - PASSED  
✅ **Test 9**: Performance benchmark - PASSED (348.1x faster with index)
  - 10,000 records inserted
  - 1,000 index lookups: 0.16ms
  - 1 sequential scan: 56.26ms

✅ **Test 10**: Index state verification - PASSED  

### Performance Analysis
- **Index Lookup**: O(1) dictionary access
- **Sequential Scan**: O(n) full file read and comparison
- **Benchmark Result**: 348x speedup with index on 10,000 records
- **Real-world impact**: For applications with frequent lookups, massive performance improvement

### Data Integrity Benefits
1. **Uniqueness**: Enforces primary key constraints
2. **Fast Access**: Direct lookup without scanning entire dataset
3. **Consistency**: Index always synchronized with JSONL file
4. **Recovery**: Index auto-rebuilt on initialization

---

## Commit 5: Implement Database Table Manager with Auto-Loading (January 17, 2026)

### What We Implemented
- ✅ Database class with table management and caching
- ✅ Auto-loading of existing tables on startup
- ✅ Schema persistence in metadata/{name}.json
- ✅ Table caching for efficient repeated access
- ✅ Primary key support integrated with table creation

### User Story
**As a Database**, I need to create and retrieve tables to manage multiple datasets efficiently.

### Acceptance Criteria Met
1. **create_table(name, schema)** ✓
   - Saves schema to metadata/{name}.json
   - Supports optional primary_key parameter
   - Creates Table object with primary key indexing
   - Raises FileExistsError if table already exists

2. **get_table(name)** ✓
   - Loads schema from metadata/{name}.json
   - Returns Table object with proper primary key support
   - Caches table instance for repeated access
   - Raises FileNotFoundError if table doesn't exist

3. **Auto-load on startup** ✓
   - `_load_existing_tables()` called in `__init__`
   - Scans metadata/ folder for .json schema files
   - Rebuilds indexes for tables with primary keys
   - Handles load errors gracefully without failing

### Key Features
1. **Table Caching**
   - In-memory cache: `self._tables: Dict[str, Table]`
   - Repeated calls to `get_table()` return same instance
   - Reduces repeated disk I/O for metadata/data loading

2. **Schema Management**
   - Schema persisted in JSON format for durability
   - Primary key stored in schema for auto-configuration
   - Schema metadata accessible via `describe()` method

3. **Initialization Flow**
   - Create data/ and metadata/ directories
   - Initialize empty table cache
   - Scan and load all existing tables
   - Build indexes for tables with primary keys

4. **Cache Invalidation**
   - `drop_table()` removes table from cache
   - `create_table()` immediately caches new table
   - Cache always reflects current state of disk

### Challenges Faced
**Challenge 1: Initialization Order - Attribute Definition**
- **Problem**: `_load_existing_tables()` was called before `self._tables` was initialized
- **Solution**: 
  - Initialize `self._tables: Dict[str, Table] = {}` in `__init__` first
  - Then call `_load_existing_tables()` which populates the cache
  - Ensures all attributes exist before methods use them

**Challenge 2: Primary Key Persistence**
- **Problem**: Primary key information was lost when reloading table from schema file
- **Solution**:
  - Store `primary_key` field directly in schema JSON
  - Read it back with `schema.get("primary_key")`
  - Pass to Table constructor to rebuild indexes automatically

**Challenge 3: Table Retrieval Consistency**
- **Problem**: Loading same table multiple times could create different instances
- **Solution**:
  - Check cache first with `if name in self._tables`
  - Return cached instance immediately (O(1) access)
  - Only load from disk if not cached
  - Add to cache after loading

**Challenge 4: Load Error Handling**
- **Problem**: One corrupted schema file could break entire database initialization
- **Solution**:
  - Try-except around each individual table load
  - Print warning but continue loading other tables
  - Database remains functional even if some tables fail to load

### Code Changes
**File Modified**: `src/database.py`

**Changes**:
1. Updated class docstring to explain caching and auto-loading

2. Updated `__init__()` method (lines ~17-28)
   - Initialize `self._tables: Dict[str, Table] = {}` cache
   - Create metadata/ directory
   - Call `_load_existing_tables()` at end

3. Added `_load_existing_tables()` method (lines ~30-50)
   - Scans metadata/ folder for .json files
   - Loads each schema and creates Table object
   - Populates cache with loaded tables
   - Handles and logs errors gracefully

4. Enhanced `create_table()` method (lines ~57-82)
   - Added `primary_key: Optional[str] = None` parameter
   - Saves primary_key in schema JSON
   - Creates and caches Table object immediately

5. Enhanced `get_table()` method (lines ~84-113)
   - Checks cache first for instant retrieval
   - Loads from disk only if not cached
   - Properly extracts and passes primary_key to Table
   - Adds loaded table to cache

6. Enhanced `drop_table()` method (lines ~115-128)
   - Removes table from in-memory cache
   - Deletes schema and data files

**File Created**: `test_database.py`
- 10 comprehensive test cases
- Tests table creation, loading, caching, auto-loading
- Tests primary key integration
- Tests error handling

### Test Results
✅ **Test 1**: Database initialization - PASSED  
✅ **Test 2**: create_table() saves schema - PASSED (file created with PK)  
✅ **Test 3**: get_table() returns Table object - PASSED (with PK loaded)  
✅ **Test 4**: Table caching - PASSED (same instance returned)  
✅ **Test 5**: list_tables() - PASSED (multiple tables listed)  
✅ **Test 6**: Insert and retrieve - PASSED (data persisted)  
✅ **Test 7**: Duplicate PK detection - PASSED (DuplicateKeyError raised)  
✅ **Test 8**: drop_table() - PASSED (files and cache cleared)  
✅ **Test 9**: Auto-load existing tables - PASSED (index rebuilt, data preserved)  
✅ **Test 10**: Optional primary key - PASSED (tables without PK work)

### Architecture Benefits
1. **Multi-Table Support**: Database manages multiple independent tables
2. **Performance**: Caching avoids repeated disk I/O
3. **Durability**: Schemas saved to disk survive application restart
4. **Recovery**: Auto-loading rebuilds indexes and restores state
5. **Flexibility**: Optional primary keys support different use cases

### Persistence Model
```
Database/
├── data/
│   ├── table1.jsonl  (row data, one JSON per line)
│   ├── table2.jsonl
│   └── ...
└── metadata/
    ├── table1.json   (schema with optional primary_key field)
    ├── table2.json
    └── ...
```

### Data Integrity
1. **Atomicity**: Schema created first, data file auto-created with Table
2. **Consistency**: Auto-loading rebuilds indexes matching persistent data
3. **Isolation**: Each table has independent file and index
4. **Durability**: All state persisted in JSON and JSONL files

---

## Next Steps
- [x] Improve error handling and validation
- [x] Implement Primary Key indexing with O(1) lookups
- [x] Create database manager for multiple tables
- [ ] Add secondary indexes for non-primary key columns
- [ ] Implement JOIN operations between tables
- [ ] Add transaction support
- [ ] Add comprehensive integration tests
- [ ] Performance optimization for large datasets
