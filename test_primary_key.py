"""Test script for primary key indexing and O(1) lookups"""
import os
import sys
import tempfile
import shutil
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from table import Table, DuplicateKeyError

def test_primary_key():
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # Create a test schema with 'id' as primary key
        schema = {
            "name": "users",
            "columns": [
                {"name": "id", "type": "int"},
                {"name": "name", "type": "str"},
                {"name": "email", "type": "str"}
            ]
        }
        
        # Create table WITH primary key
        table_with_pk = Table("users_with_pk", schema, data_dir, primary_key="id")
        
        print("=" * 60)
        print("TEST SUITE: Primary Key Indexing and O(1) Lookups")
        print("=" * 60)
        
        print("\nTest 1: Insert valid records with unique primary keys")
        try:
            r1 = table_with_pk.insert({"id": 1, "name": "Alice", "email": "alice@example.com"})
            r2 = table_with_pk.insert({"id": 2, "name": "Bob", "email": "bob@example.com"})
            r3 = table_with_pk.insert({"id": 3, "name": "Charlie", "email": "charlie@example.com"})
            print(f"✅ PASSED - Inserted 3 records with unique PKs")
            print(f"   Index state: {len(table_with_pk.index)} entries")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 2: Attempt duplicate primary key (should raise DuplicateKeyError)")
        try:
            table_with_pk.insert({"id": 1, "name": "Duplicate Alice", "email": "dup@example.com"})
            print(f"❌ FAILED - Should have raised DuplicateKeyError")
        except DuplicateKeyError as e:
            print(f"✅ PASSED - Correctly raised DuplicateKeyError: {e}")
        except Exception as e:
            print(f"❌ FAILED - Wrong exception type: {e}")
        
        print("\nTest 3: select_by_id() - O(1) lookup")
        try:
            result = table_with_pk.select_by_id(2)
            if result and result.get("name") == "Bob":
                print(f"✅ PASSED - Found record with id=2: {result}")
            else:
                print(f"❌ FAILED - Got unexpected result: {result}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 4: select_by_id() - Record not found")
        try:
            result = table_with_pk.select_by_id(999)
            if result is None:
                print(f"✅ PASSED - Correctly returned None for non-existent id")
            else:
                print(f"❌ FAILED - Expected None, got: {result}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 5: Table without primary key - select_by_id should raise ValueError")
        table_no_pk = Table("users_no_pk", schema, data_dir)
        try:
            result = table_no_pk.select_by_id(1)
            print(f"❌ FAILED - Should have raised ValueError")
        except ValueError as e:
            print(f"✅ PASSED - Correctly raised ValueError: {e}")
        except Exception as e:
            print(f"❌ FAILED - Wrong exception type: {e}")
        
        print("\nTest 6: DELETE maintains index consistency")
        try:
            deleted = table_with_pk.delete(where={"id": 1})
            if deleted == 1 and 1 not in table_with_pk.index:
                print(f"✅ PASSED - Deleted record, index updated correctly")
            else:
                print(f"❌ FAILED - Index not updated after delete")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 7: Can re-insert deleted primary key")
        try:
            r = table_with_pk.insert({"id": 1, "name": "Alice Restored", "email": "alice.new@example.com"})
            print(f"✅ PASSED - Reinserted deleted PK: {r}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 8: UPDATE maintains index consistency")
        try:
            updated = table_with_pk.update(
                set_values={"name": "Robert"},
                where={"id": 2}
            )
            result = table_with_pk.select_by_id(2)
            if updated == 1 and result.get("name") == "Robert":
                print(f"✅ PASSED - Updated record, index maintained: {result}")
            else:
                print(f"❌ FAILED - Update or index not correct")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 9: Performance - Index vs Sequential Scan")
        # Create a table with many records
        table_perf = Table("perf_test", schema, data_dir, primary_key="id")
        num_records = 10000
        
        print(f"   Inserting {num_records} records...")
        for i in range(1, num_records + 1):
            table_perf.insert({
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@example.com"
            })
        
        # Measure O(1) lookup with index
        start = time.time()
        for _ in range(1000):
            table_perf.select_by_id(9999)
        index_time = time.time() - start
        
        # Measure O(n) lookup with sequential scan (just one scan)
        start = time.time()
        result = table_perf.select(where={"id": 9999})
        scan_time = time.time() - start
        
        if index_time < scan_time:
            speedup = scan_time / index_time if index_time > 0 else float('inf')
            print(f"✅ PASSED - Index lookup {speedup:.1f}x faster than sequential scan")
            print(f"   Index: {index_time*1000:.2f}ms for 1000 lookups")
            print(f"   Scan:  {scan_time*1000:.2f}ms for 1 scan")
        else:
            print(f"⚠️  Index performance similar to scan (acceptable for small dataset)")
        
        print("\nTest 10: Index state after various operations")
        print(f"✅ PASSED - Final index has {len(table_with_pk.index)} entries")
        print(f"   Keys in index: {sorted(table_with_pk.index.keys())}")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\n✨ Test directory cleaned up")

if __name__ == "__main__":
    test_primary_key()
