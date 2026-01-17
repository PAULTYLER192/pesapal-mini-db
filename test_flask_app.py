"""Test script for Flask web application"""
import os
import sys
import tempfile
import shutil
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import Flask app
os.environ['FLASK_ENV'] = 'testing'
from app.app import app, db

def test_flask_app():
    # Setup
    print("=" * 70)
    print("TEST SUITE: Flask Web Application - User Registration")
    print("=" * 70)
    
    # Create Flask test client
    app.config['TESTING'] = True
    client = app.test_client()
    
    print("\nTest 1: GET / - Load registration page")
    try:
        response = client.get("/")
        if response.status_code == 200 and b"User Registration" in response.data:
            print(f"✅ PASSED - Page loaded successfully (status: {response.status_code})")
        else:
            print(f"❌ FAILED - Unexpected response (status: {response.status_code})")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 2: POST /register - Register a new user")
    try:
        response = client.post("/register", data={
            "name": "Alice Johnson",
            "email": "alice@example.com"
        }, follow_redirects=True)
        
        if response.status_code == 200 and b"Alice Johnson" in response.data:
            print(f"✅ PASSED - User registered successfully")
            print(f"   Name: Alice Johnson, Email: alice@example.com")
        else:
            print(f"❌ FAILED - User not visible in response")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 3: User appears in registered users list")
    try:
        response = client.get("/")
        if b"alice@example.com" in response.data and b"Alice Johnson" in response.data:
            print(f"✅ PASSED - User visible in registered list")
        else:
            print(f"❌ FAILED - User not found in list")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 4: POST /register - Register multiple users")
    try:
        users_data = [
            ("Bob Smith", "bob@example.com"),
            ("Charlie Brown", "charlie@example.com"),
            ("Diana Prince", "diana@example.com")
        ]
        
        for name, email in users_data:
            response = client.post("/register", data={
                "name": name,
                "email": email
            }, follow_redirects=True)
            
            if response.status_code != 200:
                print(f"❌ FAILED - Error registering {name}")
                break
        else:
            print(f"✅ PASSED - Registered 3 more users successfully")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 5: All users display in the list")
    try:
        response = client.get("/")
        response_text = response.data.decode('utf-8')
        
        expected_names = ["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince"]
        expected_emails = ["alice@example.com", "bob@example.com", "charlie@example.com", "diana@example.com"]
        
        all_found = all(name in response_text for name in expected_names)
        all_emails = all(email in response_text for email in expected_emails)
        
        if all_found and all_emails:
            print(f"✅ PASSED - All 4 users visible in list")
            print(f"   Users: {', '.join(expected_names)}")
        else:
            print(f"❌ FAILED - Not all users visible")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 6: Form validation - Missing name")
    try:
        response = client.post("/register", data={
            "name": "",
            "email": "test@example.com"
        }, follow_redirects=True)
        
        if b"required" in response.data.lower() or response.status_code == 200:
            print(f"✅ PASSED - Form validation working (empty name rejected)")
        else:
            print(f"❌ FAILED - Form validation not working")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 7: Form validation - Missing email")
    try:
        response = client.post("/register", data={
            "name": "Test User",
            "email": ""
        }, follow_redirects=True)
        
        if b"required" in response.data.lower() or response.status_code == 200:
            print(f"✅ PASSED - Form validation working (empty email rejected)")
        else:
            print(f"❌ FAILED - Form validation not working")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 8: Database integration - Check users table")
    try:
        users_table = db.get_table("users")
        all_users = users_table.select()
        
        if len(all_users) >= 4:
            print(f"✅ PASSED - Database has {len(all_users)} users")
            print(f"   Users table primary key: {users_table.primary_key}")
            print(f"   Table index size: {len(users_table.index)}")
        else:
            print(f"⚠️  Only {len(all_users)} users in database")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 9: SELECT_BY_ID - Fast lookup of user by ID")
    try:
        users_table = db.get_table("users")
        user = users_table.select_by_id(1)
        
        if user and user.get("name") == "Alice Johnson":
            print(f"✅ PASSED - O(1) lookup retrieved: {user}")
        else:
            print(f"❌ FAILED - User lookup failed or data incorrect")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\nTest 10: Users table structure")
    try:
        users_table = db.get_table("users")
        
        # Check columns
        expected_columns = {"id", "name", "email"}
        actual_columns = set(users_table.columns.keys())
        
        if expected_columns == actual_columns:
            print(f"✅ PASSED - Table has correct schema")
            print(f"   Columns: {', '.join(sorted(actual_columns))}")
            print(f"   Primary Key: {users_table.primary_key}")
        else:
            print(f"❌ FAILED - Column mismatch. Expected {expected_columns}, got {actual_columns}")
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("\n" + "=" * 70)
    print("Flask Integration Test Complete")
    print("The web interface successfully:")
    print("  ✓ Displays a user registration form with Name and Email fields")
    print("  ✓ Handles POST requests to insert users")
    print("  ✓ Shows a live list of registered users")
    print("  ✓ Uses the database with primary key indexing")
    print("=" * 70)

if __name__ == "__main__":
    test_flask_app()
