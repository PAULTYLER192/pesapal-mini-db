"""Test script for SQL parser"""
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from parser import parse_sql

def test_parser():
    print("=" * 70)
    print("TEST SUITE: SQL Parser - Text to Method Calls Translation")
    print("=" * 70)
    
    # Test 1: INSERT INTO with JSON values
    print("\nTest 1: INSERT INTO table VALUES with JSON-like data")
    try:
        query = "INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')"
        result = parse_sql(query)
        if (result["type"] == "insert" and 
            result["name"] == "users" and 
            result["values"]["id"] == 1 and
            result["values"]["name"] == "Alice" and
            result["values"]["email"] == "alice@example.com"):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 2: SELECT * FROM table
    print("\nTest 2: SELECT * FROM table")
    try:
        query = "SELECT * FROM users"
        result = parse_sql(query)
        if (result["type"] == "select" and 
            result["name"] == "users" and 
            result["columns"] is None):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 3: SELECT * FROM table WHERE id = X
    print("\nTest 3: SELECT * FROM table WHERE id = X (integer condition)")
    try:
        query = "SELECT * FROM users WHERE id = 1"
        result = parse_sql(query)
        if (result["type"] == "select" and 
            result["name"] == "users" and 
            result["where"]["id"] == 1):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 4: SELECT specific columns
    print("\nTest 4: SELECT specific columns FROM table")
    try:
        query = "SELECT id, name FROM users"
        result = parse_sql(query)
        if (result["type"] == "select" and 
            result["columns"] == ["id", "name"]):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 5: SELECT with multiple WHERE conditions
    print("\nTest 5: SELECT with multiple WHERE conditions (AND)")
    try:
        query = "SELECT * FROM users WHERE id = 1 AND name = 'Alice'"
        result = parse_sql(query)
        if (result["type"] == "select" and 
            result["where"]["id"] == 1 and
            result["where"]["name"] == "Alice"):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 6: SELECT with LIMIT
    print("\nTest 6: SELECT with LIMIT clause")
    try:
        query = "SELECT * FROM users LIMIT 10"
        result = parse_sql(query)
        if (result["type"] == "select" and 
            result["limit"] == 10):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 7: SELECT with WHERE and LIMIT
    print("\nTest 7: SELECT with WHERE and LIMIT")
    try:
        query = "SELECT * FROM users WHERE id = 5 LIMIT 100"
        result = parse_sql(query)
        if (result["type"] == "select" and 
            result["where"]["id"] == 5 and
            result["limit"] == 100):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 8: CREATE TABLE
    print("\nTest 8: CREATE TABLE with schema")
    try:
        query = "CREATE TABLE users (id int, name str, email str)"
        result = parse_sql(query)
        if (result["type"] == "create_table" and 
            result["name"] == "users" and
            len(result["columns"]) == 3):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 9: UPDATE statement
    print("\nTest 9: UPDATE table SET columns WHERE condition")
    try:
        query = "UPDATE users SET name = 'Bob', email = 'bob@example.com' WHERE id = 1"
        result = parse_sql(query)
        if (result["type"] == "update" and 
            result["name"] == "users" and
            result["set"]["name"] == "Bob" and
            result["where"]["id"] == 1):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 10: DELETE statement
    print("\nTest 10: DELETE FROM table WHERE condition")
    try:
        query = "DELETE FROM users WHERE id = 1"
        result = parse_sql(query)
        if (result["type"] == "delete" and 
            result["name"] == "users" and
            result["where"]["id"] == 1):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 11: DROP TABLE
    print("\nTest 11: DROP TABLE statement")
    try:
        query = "DROP TABLE users"
        result = parse_sql(query)
        if (result["type"] == "drop_table" and 
            result["name"] == "users"):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 12: SHOW TABLES
    print("\nTest 12: SHOW TABLES statement")
    try:
        query = "SHOW TABLES"
        result = parse_sql(query)
        if result["type"] == "show_tables":
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 13: DESCRIBE table
    print("\nTest 13: DESCRIBE table statement")
    try:
        query = "DESCRIBE users"
        result = parse_sql(query)
        if (result["type"] == "describe" and 
            result["name"] == "users"):
            print(f"✅ PASSED - Parsed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Unexpected result: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 14: INSERT with integer, float, boolean, and string values
    print("\nTest 14: INSERT with mixed types (int, float, bool, string)")
    try:
        query = "INSERT INTO products (id, name, price, active) VALUES (1, 'Widget', 19.99, true)"
        result = parse_sql(query)
        if (result["type"] == "insert" and 
            isinstance(result["values"]["id"], int) and
            isinstance(result["values"]["price"], float) and
            isinstance(result["values"]["active"], bool) and
            isinstance(result["values"]["name"], str)):
            print(f"✅ PASSED - Parsed with correct types: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Type conversion failed: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 15: Case insensitivity
    print("\nTest 15: Parser is case insensitive for keywords")
    try:
        query = "select * from users where id = 5"
        result = parse_sql(query)
        if (result["type"] == "select" and 
            result["name"] == "users" and
            result["where"]["id"] == 5):
            print(f"✅ PASSED - Case-insensitive parsing works")
        else:
            print(f"❌ FAILED - Case sensitivity issue: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 16: Trailing semicolon handling
    print("\nTest 16: Parser handles trailing semicolons")
    try:
        query = "SELECT * FROM users WHERE id = 1;"
        result = parse_sql(query)
        if (result["type"] == "select" and 
            result["where"]["id"] == 1):
            print(f"✅ PASSED - Semicolon handled correctly")
        else:
            print(f"❌ FAILED - Semicolon handling failed: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 17: Quote handling in string values
    print("\nTest 17: Quote handling in string values (single and double quotes)")
    try:
        query = 'INSERT INTO users (name, email) VALUES ("Alice", \'alice@example.com\')'
        result = parse_sql(query)
        if (result["values"]["name"] == "Alice" and
            result["values"]["email"] == "alice@example.com"):
            print(f"✅ PASSED - Both quote types handled: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - Quote handling failed: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    # Test 18: NULL value handling
    print("\nTest 18: NULL value handling")
    try:
        query = "INSERT INTO users (id, name, email) VALUES (1, NULL, NULL)"
        result = parse_sql(query)
        if (result["values"]["id"] == 1 and
            result["values"]["name"] is None and
            result["values"]["email"] is None):
            print(f"✅ PASSED - NULL values parsed correctly: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ FAILED - NULL handling failed: {result}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\n" + "=" * 70)
    print("Test Summary: SQL Parser converts text commands to AST dictionaries")
    print("These dictionaries are then passed to Database.execute() for execution")
    print("=" * 70)

if __name__ == "__main__":
    test_parser()
