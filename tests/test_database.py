"""
Unit tests for Database class.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.db import Database


def test_database_creation():
    """Test database creation."""
    db = Database("testdb")
    assert db.name == "testdb"
    assert len(db.list_tables()) == 0


def test_create_table():
    """Test creating a table."""
    db = Database()
    table = db.create_table('users', ['id', 'name', 'email'])
    
    assert table.name == 'users'
    assert 'users' in db.list_tables()
    assert len(db.list_tables()) == 1


def test_create_table_invalid_name():
    """Test creating table with invalid name."""
    db = Database()
    
    with pytest.raises(ValueError, match="Invalid table name"):
        db.create_table('123invalid', ['id', 'name'])


def test_create_table_duplicate():
    """Test creating duplicate table."""
    db = Database()
    db.create_table('users', ['id', 'name'])
    
    with pytest.raises(ValueError, match="Table already exists"):
        db.create_table('users', ['id', 'email'])


def test_create_table_no_columns():
    """Test creating table with no columns."""
    db = Database()
    
    with pytest.raises(ValueError, match="at least one column"):
        db.create_table('users', [])


def test_drop_table():
    """Test dropping a table."""
    db = Database()
    db.create_table('users', ['id', 'name'])
    assert 'users' in db.list_tables()
    
    result = db.drop_table('users')
    assert result == True
    assert 'users' not in db.list_tables()


def test_drop_nonexistent_table():
    """Test dropping non-existent table."""
    db = Database()
    
    with pytest.raises(ValueError, match="Table does not exist"):
        db.drop_table('nonexistent')


def test_get_table():
    """Test getting a table."""
    db = Database()
    db.create_table('users', ['id', 'name'])
    
    table = db.get_table('users')
    assert table.name == 'users'
    assert table.columns == ['id', 'name']


def test_get_nonexistent_table():
    """Test getting non-existent table."""
    db = Database()
    
    with pytest.raises(ValueError, match="Table does not exist"):
        db.get_table('nonexistent')


def test_list_tables():
    """Test listing tables."""
    db = Database()
    assert db.list_tables() == []
    
    db.create_table('users', ['id', 'name'])
    db.create_table('products', ['id', 'title'])
    
    tables = db.list_tables()
    assert len(tables) == 2
    assert 'users' in tables
    assert 'products' in tables


def test_insert():
    """Test inserting through database."""
    db = Database()
    db.create_table('users', ['id', 'name'])
    
    result = db.insert('users', {'id': 1, 'name': 'John'})
    assert result == True
    
    table = db.get_table('users')
    assert table.count() == 1


def test_select():
    """Test selecting through database."""
    db = Database()
    db.create_table('users', ['id', 'name', 'age'])
    db.insert('users', {'id': 1, 'name': 'John', 'age': 30})
    db.insert('users', {'id': 2, 'name': 'Jane', 'age': 25})
    
    # Select all
    rows = db.select('users')
    assert len(rows) == 2
    
    # Select with columns
    rows = db.select('users', columns=['name'])
    assert len(rows) == 2
    assert 'id' not in rows[0]
    
    # Select with WHERE
    rows = db.select('users', where={'column': 'age', 'operator': '>', 'value': 26})
    assert len(rows) == 1
    assert rows[0]['name'] == 'John'


def test_update():
    """Test updating through database."""
    db = Database()
    db.create_table('users', ['id', 'name', 'age'])
    db.insert('users', {'id': 1, 'name': 'John', 'age': 30})
    db.insert('users', {'id': 2, 'name': 'Jane', 'age': 25})
    
    count = db.update('users', {'age': 31}, where={'column': 'id', 'operator': '=', 'value': 1})
    assert count == 1
    
    rows = db.select('users', where={'column': 'id', 'operator': '=', 'value': 1})
    assert rows[0]['age'] == 31


def test_delete():
    """Test deleting through database."""
    db = Database()
    db.create_table('users', ['id', 'name'])
    db.insert('users', {'id': 1, 'name': 'John'})
    db.insert('users', {'id': 2, 'name': 'Jane'})
    
    count = db.delete('users', where={'column': 'id', 'operator': '=', 'value': 1})
    assert count == 1
    
    table = db.get_table('users')
    assert table.count() == 1


def test_multiple_tables():
    """Test operations on multiple tables."""
    db = Database()
    
    # Create tables
    db.create_table('users', ['id', 'name'])
    db.create_table('products', ['id', 'title', 'price'])
    
    # Insert into both
    db.insert('users', {'id': 1, 'name': 'John'})
    db.insert('products', {'id': 1, 'title': 'Widget', 'price': 9.99})
    
    # Verify independence
    assert db.get_table('users').count() == 1
    assert db.get_table('products').count() == 1
    
    # Drop one table
    db.drop_table('users')
    assert 'users' not in db.list_tables()
    assert 'products' in db.list_tables()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
