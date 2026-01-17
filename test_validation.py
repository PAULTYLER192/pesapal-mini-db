"""Test script for data validation in Table.insert()"""
import os
import sys
import tempfile
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from table import Table

def test_validation():
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # Create a test schema
        schema = {
            "name": "users",
            "columns": [
                {"name": "id", "type": "int"},
                {"name": "name", "type": "str"},
                {"name": "age", "type": "int"},
                {"name": "active", "type": "bool"}
            ]
        }
        
        table = Table("users", schema, data_dir)
        
        print("Test 1: Valid data insertion")
        try:
            result = table.insert({"id": 1, "name": "Alice", "age": 30, "active": True})
            print(f"✅ PASSED - Inserted: {result}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 2: Valid data with type conversion (string to int)")
        try:
            result = table.insert({"id": 2, "name": "Bob", "age": "25", "active": "true"})
            print(f"✅ PASSED - Inserted with conversion: {result}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 3: Invalid type - string for int field (should raise TypeError)")
        try:
            result = table.insert({"id": 3, "name": "Charlie", "age": "twenty", "active": True})
            print(f"❌ FAILED - Should have raised TypeError but inserted: {result}")
        except TypeError as e:
            print(f"✅ PASSED - Correctly raised TypeError: {e}")
        except Exception as e:
            print(f"❌ FAILED - Wrong exception type: {e}")
        
        print("\nTest 4: Missing required column (should raise ValueError)")
        try:
            result = table.insert({"id": 4, "name": "David"})  # Missing 'age' and 'active'
            print(f"❌ FAILED - Should have raised ValueError but inserted: {result}")
        except ValueError as e:
            print(f"✅ PASSED - Correctly raised ValueError: {e}")
        except Exception as e:
            print(f"❌ FAILED - Wrong exception type: {e}")
        
        print("\nTest 5: Extra columns allowed (not in schema)")
        try:
            result = table.insert({
                "id": 5, 
                "name": "Eve", 
                "age": 28, 
                "active": False,
                "email": "eve@example.com"  # Extra column
            })
            print(f"✅ PASSED - Inserted with extra column: {result}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 6: Null values allowed")
        try:
            result = table.insert({"id": 6, "name": None, "age": None, "active": None})
            print(f"✅ PASSED - Inserted with null values: {result}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        # Verify all valid insertions
        print("\n" + "="*50)
        print("Verifying inserted records:")
        rows = table.select()
        print(f"Total rows: {len(rows)}")
        for row in rows:
            print(f"  {row}")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\n✨ Test directory cleaned up")

if __name__ == "__main__":
    test_validation()
