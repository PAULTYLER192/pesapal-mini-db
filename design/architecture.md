# Architecture & Design Decisions

This document explains the key architectural choices made in building the Mini DB RDBMS.

---

## Storage Format: Why JSONL?

### Decision
We use **JSON Lines (JSONL)** format for storing table data, where each row is stored as a separate JSON object on its own line.

### Rationale

**1. O(1) Append Performance**
```
Row 1: {"id": 1, "name": "Alice"}
Row 2: {"id": 2, "name": "Bob"}
Row 3: {"id": 3, "name": "Charlie"}
```
- New rows are simply appended to the file
- No need to read existing data
- No need to rewrite the entire file for inserts
- Constant-time operation regardless of file size

**2. Crash Safety**
- Each line is a complete, valid JSON object
- If a write is interrupted mid-line, only the incomplete line is corrupted
- All previous rows remain intact and readable
- Compare to single JSON array: one corrupt byte breaks the entire file

**3. Line-by-Line Reading**
- Can process large files without loading entire dataset into memory
- Stream processing: read one line at a time
- Memory usage stays constant regardless of table size
- Enables processing files larger than available RAM

**4. Simplicity**
- No need for binary formats or custom parsers
- Human-readable: easy to inspect and debug
- Works with standard text tools (grep, sed, awk, etc.)
- Cross-platform compatibility

**5. Partial Recovery**
- If corruption occurs, can skip bad lines and recover rest
- Easy to write recovery tools using standard text processing

### Trade-offs

**Disadvantages:**
- **Updates/Deletes require full rewrite:** No in-place modification
  - Solution: Good enough for small-to-medium datasets
  - Alternative for scale: WAL (Write-Ahead Log) pattern
  
- **No compression:** Each line is separate JSON
  - Impact: Larger file sizes than binary formats
  - Mitigation: Text files compress well with gzip if needed

- **No indexes on disk:** All indexes in memory
  - Impact: Index rebuild required on startup
  - Mitigation: Fast enough for typical use cases

### Alternatives Considered

**Single JSON Array:**
```json
[
  {"id": 1, "name": "Alice"},
  {"id": 2, "name": "Bob"}
]
```
❌ **Rejected:** Requires rewriting entire file for any change. Not crash-safe.

**CSV:**
```csv
id,name
1,Alice
2,Bob
```
❌ **Rejected:** No type information. Complex escaping for nested data.

**SQLite:**
✅ **Best for production** but defeats the learning purpose of building a custom RDBMS.

**Binary Formats (Parquet, Avro):**
❌ **Rejected:** Adds complexity. Not human-readable. Requires specialized libraries.

---

## Primary Key Indexing

### Decision
We maintain an **in-memory dictionary** mapping primary key values to row data.

### Rationale

**1. O(1) Lookup Performance**
```python
self.index = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"}
}
```
- `select_by_id(1)` is instant dictionary lookup
- No need to scan through JSONL file
- Benchmark: 348x faster than sequential scan (10,000 records)

**2. Uniqueness Enforcement**
- Check `if pk_value in self.index` before insert
- Prevents duplicate primary keys at insert time
- No need to scan entire file to check uniqueness

**3. Simple Implementation**
- Standard Python dictionary
- No complex B-tree or hash table implementation needed
- Easy to maintain and debug

### Trade-offs

**Memory Usage:**
- Index stores full row data in memory
- For 10,000 users (~100 bytes each): ~1 MB RAM
- Trade-off: Fast lookups vs. memory consumption
- Solution: Fine for small-to-medium datasets

**Index Rebuild on Startup:**
- Must read entire JSONL file to rebuild index
- O(n) operation on database initialization
- Mitigated by: Table caching reduces rebuilds

### Alternatives Considered

**Store File Offset:**
```python
self.index = {
    1: 0,      # byte offset in file
    2: 156,
    3: 312
}
```
✅ **Memory efficient** but requires seek operations and parsing on lookup.
❌ **Rejected:** Complexity of maintaining offsets after updates/deletes.

**No Index (Always Scan):**
❌ **Rejected:** O(n) performance unacceptable for primary key lookups.

**Persistent B-Tree Index:**
✅ **Best for production** but adds significant complexity.

---

## Schema Storage: Separate Metadata Files

### Decision
Store table schemas in `metadata/{table_name}.json` files, separate from data.

### Rationale

**1. Fast Schema Access**
- Read schema without touching data files
- Schema queries (DESCRIBE) don't require loading row data
- Quick table listing and schema inspection

**2. Schema Evolution**
- Can modify schema independently of data
- Easier to add features like indexes, constraints
- Data migration becomes simpler

**3. Durability**
- Schema persists across application restarts
- Auto-loading: scan metadata folder on startup
- No hardcoded schemas in code

**4. Clean Separation**
```
project/
├── data/
│   ├── users.jsonl      # Row data only
│   └── products.jsonl
└── metadata/
    ├── users.json       # Schema: columns, types, primary_key
    └── products.json
```

### Schema Format
```json
{
  "name": "users",
  "columns": [
    {"name": "id", "type": "int"},
    {"name": "name", "type": "str"},
    {"name": "email", "type": "str"}
  ],
  "primary_key": "id"
}
```

### Alternatives Considered

**Schema in Data File Header:**
❌ **Rejected:** Complicates reading data. Header becomes outdated.

**Schema in Code:**
❌ **Rejected:** Not persistent. Requires code changes for new tables.

**Single schemas.json File:**
❌ **Rejected:** All tables coupled together. Harder to manage individually.

---

## Table Caching

### Decision
Cache `Table` objects in `Database._tables` dictionary after first access.

### Rationale

**1. Avoid Repeated Disk I/O**
```python
# Without caching: 3 file reads
db.get_table("users")  # Read metadata/users.json, build index
db.get_table("users")  # Read again
db.get_table("users")  # Read again

# With caching: 1 file read
db.get_table("users")  # Read metadata/users.json, build index, cache
db.get_table("users")  # Return cached instance
db.get_table("users")  # Return cached instance
```

**2. Index Preservation**
- Primary key index built once
- Subsequent calls reuse in-memory index
- No need to rebuild index on every query

**3. Consistency**
- All operations on same table use same instance
- Index stays synchronized with data
- No risk of stale data from multiple instances

### Implementation
```python
class Database:
    def __init__(self):
        self._tables = {}  # Cache
        self._load_existing_tables()  # Pre-populate cache
    
    def get_table(self, name):
        if name in self._tables:
            return self._tables[name]  # Cache hit
        # Cache miss: load and cache
        table = Table(...)
        self._tables[name] = table
        return table
```

### Trade-offs

**Memory Usage:**
- All accessed tables stay in memory
- For large databases with many tables, consider LRU eviction
- Current implementation: Simple, no eviction

---

## Type System

### Decision
Support 4 basic types: `int`, `float`, `str`, `bool`, plus `null`.

### Rationale

**1. Simplicity**
- Covers 95% of use cases
- Easy to implement and validate
- No complex type hierarchies

**2. JSON Compatibility**
- All types map directly to JSON primitives
- No serialization complexity
- Human-readable in JSONL files

**3. Type Safety**
- Validation on insert
- Type conversion with error handling
- Prevents data corruption

### Type Conversion Rules
```python
# String to int
"42" → 42  ✅
"hello" → TypeError  ❌

# String to bool
"true" → True  ✅
"1" → True  ✅
"yes" → True  ✅
"invalid" → TypeError  ❌

# Null
null → None  ✅ (allowed for any type)
```

### Alternatives Considered

**More Types (date, time, blob):**
❌ **Rejected:** Adds complexity. Can store as strings and parse in application.

**No Type System:**
❌ **Rejected:** Loses validation benefits. Harder to ensure data quality.

**Strict Types (no conversion):**
❌ **Rejected:** Too rigid. User must match types exactly, poor UX.

---

## SQL Parser: Custom vs. Library

### Decision
Build a **custom regex-based parser** instead of using a SQL parsing library.

### Rationale

**1. Learning Value**
- Understand how parsers work
- Control over supported syntax
- No external dependencies

**2. Simplicity**
- Support only needed commands
- No 100+ SQL features we don't need
- Easier to debug and maintain

**3. Customization**
- Can support JSON values in INSERT
- Can evolve syntax for specific needs
- Not bound by SQL standard

**4. Size**
- Small codebase (~200 lines)
- No megabyte-sized parsing libraries
- Fast imports

### Trade-offs

**Limitations:**
- No JOIN, subqueries, aggregations
- Simple WHERE clause (= and AND only)
- No ORDER BY, GROUP BY, HAVING

**Workarounds:**
- Use Python for complex operations
- Document limitations clearly
- Provide escape hatch via Python API

### Alternatives Considered

**sqlparse Library:**
✅ **Robust** but heavy and unnecessary for simple use case.

**Full SQL Engine (like SQLite):**
✅ **Feature-complete** but defeats learning purpose.

**ANTLR Grammar:**
✅ **Proper parsing** but overkill for 8 simple commands.

---

## Flask Web Interface

### Decision
Provide a **single-page web interface** for user registration as demo.

### Rationale

**1. Visual Demonstration**
- Shows database in action
- Non-technical users can interact
- Better than CLI for demos

**2. Real-World Use Case**
- User registration is common
- Shows CRUD operations
- Demonstrates form handling

**3. Simple Deployment**
- Single Flask app
- No frontend build step
- No JavaScript framework needed

### Architecture
```
Browser → Flask (app.py) → Database → Table → JSONL File
         ↑                                      ↓
         └──────────── JSON Response ───────────┘
```

---

## Performance Characteristics

### Current Performance (10,000 rows)

| Operation | Time | Complexity |
|-----------|------|-----------|
| Insert (with PK) | ~0.1ms | O(1) |
| Insert (without PK) | ~0.1ms | O(1) |
| Select by ID | ~0.16ms | O(1) |
| Select all | ~56ms | O(n) |
| Select (filtered) | ~56ms | O(n) |
| Update | ~60ms | O(n) |
| Delete | ~60ms | O(n) |
| Count | ~20ms | O(n) |

### Optimization Strategies

**When to Optimize:**
- Tables > 100,000 rows
- Frequent updates/deletes
- Complex queries

**How to Optimize:**
1. **Secondary Indexes:** Index non-PK columns for faster WHERE queries
2. **Batch Operations:** Group multiple inserts/updates
3. **Write-Ahead Log:** Avoid full rewrites on updates
4. **Compression:** Gzip JSONL files for storage savings
5. **Sharding:** Split large tables across multiple files

---

## Future Improvements

### Short-term
- [ ] Secondary indexes on frequently queried columns
- [ ] Transaction support (BEGIN, COMMIT, ROLLBACK)
- [ ] Batch insert API
- [ ] Connection pooling for Flask app

### Medium-term
- [ ] JOIN support (hash join for inner joins)
- [ ] Aggregation functions (COUNT, SUM, AVG)
- [ ] ORDER BY and LIMIT optimization
- [ ] Query plan explanation (EXPLAIN)

### Long-term
- [ ] Write-Ahead Log (WAL) for crash recovery
- [ ] Multi-threaded query execution
- [ ] Distributed storage (sharding)
- [ ] Replication and backup

---

## Lessons Learned

### What Worked Well
✅ JSONL format: Simple and effective for learning  
✅ Primary key indexing: Massive performance win  
✅ Python dict for caching: Fast and simple  
✅ Custom parser: Good for understanding internals  

### What Could Be Improved
⚠️ Full file rewrite on UPDATE/DELETE: Acceptable for now, but not scalable  
⚠️ In-memory indexes: Limited by RAM  
⚠️ Simple WHERE parser: Could support more operators  
⚠️ No query optimization: Scans entire table for non-PK queries  

### Design Principles Applied
1. **Start Simple:** Build minimum viable features first
2. **Measure First:** Benchmark before optimizing
3. **Document Trade-offs:** Explain why decisions were made
4. **Iterate:** Can always add features later

---

## Conclusion

This architecture balances **simplicity** (for learning and maintainability) with **functionality** (real-world use cases). While not production-ready for large-scale applications, it demonstrates core database concepts effectively:

- **Storage:** JSONL for append-only writes
- **Indexing:** In-memory hash maps for fast lookups
- **Schema:** JSON metadata for persistence
- **Query:** Custom parser for SQL-like interface
- **Interface:** Flask web app for user interaction

The design provides a solid foundation for understanding how databases work internally, with clear paths for future enhancements when needed.
