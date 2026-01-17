"""Test script for Database class with table management"""
import os
import sys
import tempfile
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from database import Database

def test_database():
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    
    try:
        print("=" * 60)
        print("TEST SUITE: Database Table Management")
        print("=" * 60)
        
        print("\nTest 1: Database initialization with empty metadata folder")
        try:
            db = Database(base_dir=test_dir)
            tables = db.list_tables()
            if tables == []:
                print(f"✅ PASSED - Database initialized with 0 tables")
            else:
                print(f"❌ FAILED - Expected 0 tables, got {len(tables)}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 2: create_table() - saves schema to metadata/{name}.json")
        try:
            schema = db.create_table(
                name="users",
                columns=[
                    {"name": "id", "type": "int"},
                    {"name": "name", "type": "str"},
                    {"name": "email", "type": "str"}
                ],
                primary_key="id"
            )
            
            # Verify schema file was created
            schema_path = os.path.join(test_dir, "metadata", "users.json")
            if os.path.exists(schema_path):
                print(f"✅ PASSED - Schema file created at {schema_path}")
                # Verify schema content
                with open(schema_path, "r") as f:
                    import json
                    saved_schema = json.load(f)
                    if saved_schema.get("primary_key") == "id":
                        print(f"✅ PASSED - Primary key saved in schema")
                    else:
                        print(f"❌ FAILED - Primary key not in schema")
            else:
                print(f"❌ FAILED - Schema file not created")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 3: get_table() - loads schema and returns Table object")
        try:
            table = db.get_table("users")
            if table is not None and table.name == "users":
                print(f"✅ PASSED - Retrieved table object: {table.name}")
                if table.primary_key == "id":
                    print(f"✅ PASSED - Primary key loaded correctly")
                else:
                    print(f"❌ FAILED - Primary key not loaded")
            else:
                print(f"❌ FAILED - Table object invalid")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 4: Table caching - get_table() returns same instance")
        try:
            table1 = db.get_table("users")
            table2 = db.get_table("users")
            if table1 is table2:  # Same object in memory
                print(f"✅ PASSED - Table cached, same instance returned")
            else:
                print(f"⚠️  Tables are different instances (caching not working)")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 5: list_tables() - returns all created tables")
        try:
            db.create_table(
                name="products",
                columns=[
                    {"name": "product_id", "type": "int"},
                    {"name": "title", "type": "str"},
                    {"name": "price", "type": "float"}
                ],
                primary_key="product_id"
            )
            tables = db.list_tables()
            if len(tables) == 2 and "users" in tables and "products" in tables:
                print(f"✅ PASSED - list_tables() returns: {tables}")
            else:
                print(f"❌ FAILED - Expected ['products', 'users'], got {tables}")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 6: Insert and retrieve via Database")
        try:
            table = db.get_table("users")
            result = table.insert({"id": 1, "name": "Alice", "email": "alice@example.com"})
            print(f"✅ PASSED - Inserted record: {result}")
            
            # Retrieve via select_by_id
            retrieved = table.select_by_id(1)
            if retrieved and retrieved.get("name") == "Alice":
                print(f"✅ PASSED - Retrieved record via select_by_id")
            else:
                print(f"❌ FAILED - Could not retrieve record")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 7: Duplicate primary key prevention")
        try:
            table = db.get_table("users")
            table.insert({"id": 1, "name": "Duplicate Alice", "email": "dup@example.com"})
            print(f"❌ FAILED - Should have raised DuplicateKeyError")
        except Exception as e:
            if "DuplicateKeyError" in str(type(e).__name__):
                print(f"✅ PASSED - Correctly raised DuplicateKeyError: {e}")
            else:
                print(f"❌ FAILED - Wrong exception: {e}")
        
        print("\nTest 8: drop_table() - removes table and clears cache")
        try:
            schema_path = os.path.join(test_dir, "metadata", "products.json")
            data_path = os.path.join(test_dir, "data", "products.jsonl")
            
            db.drop_table("products")
            
            if not os.path.exists(schema_path) and not os.path.exists(data_path):
                print(f"✅ PASSED - Schema and data files removed")
            else:
                print(f"❌ FAILED - Files not removed")
            
            tables = db.list_tables()
            if "products" not in tables:
                print(f"✅ PASSED - Table removed from list_tables()")
            else:
                print(f"❌ FAILED - Table still in list")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 9: Auto-load existing tables on Database init")
        try:
            # Create a new database instance pointing to same location
            db2 = Database(base_dir=test_dir)
            tables = db2.list_tables()
            
            if "users" in tables:
                print(f"✅ PASSED - Existing table auto-loaded")
                
                # Verify it has the data we inserted
                table = db2.get_table("users")
                retrieved = table.select_by_id(1)
                if retrieved and retrieved.get("name") == "Alice":
                    print(f"✅ PASSED - Auto-loaded table has correct data and index")
                else:
                    print(f"❌ FAILED - Data not preserved or index not rebuilt")
            else:
                print(f"❌ FAILED - Table not auto-loaded")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\nTest 10: Schema with optional primary key")
        try:
            db.create_table(
                name="logs",
                columns=[
                    {"name": "message", "type": "str"},
                    {"name": "level", "type": "str"}
                ]
                # No primary_key specified
            )
            
            table = db.get_table("logs")
            if table.primary_key is None:
                print(f"✅ PASSED - Table created without primary key")
                
                # Can still insert without PK constraints
                result = table.insert({"message": "Test log", "level": "INFO"})
                print(f"✅ PASSED - Inserted without primary key")
            else:
                print(f"❌ FAILED - Primary key should be None")
        except Exception as e:
            print(f"❌ FAILED - {e}")
        
        print("\n" + "=" * 60)
        print("Final Database State:")
        final_tables = db.list_tables()
        print(f"Tables: {final_tables}")
        for tbl_name in final_tables:
            tbl = db.get_table(tbl_name)
            print(f"  - {tbl_name}: PK={tbl.primary_key}, rows={tbl.count()}")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\n✨ Test directory cleaned up")

if __name__ == "__main__":
    test_database()
